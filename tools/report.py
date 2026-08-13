#!/usr/bin/env python3
"""report.py — the four measurements that separate real progress from the feeling of it.

  python3 tools/report.py

1. Time curve per kata. Should fall, then flatten.
2. Clean-first-compile rate. Best single proxy for syntax fluency.
   40% by week 4, 55% by week 6, 70% by week 10.
3. Where the time goes. design / write / compile / debug. This is the diagnosis.
4. Reps per week and coverage. What you're avoiding.
"""
import importlib.util
import os
from collections import defaultdict
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "logs", "log.tsv")
SPLITS = os.path.join(ROOT, "logs", "splits.tsv")
KATAS = os.path.join(ROOT, "practice", "katas")


def _targets():
    """Read the targets from drill.py. This file used to keep its own copy, and the
    copy silently fell a kata behind — rollover_timer was measured against the 15-min
    default for as long as the second dict existed. One dict, imported."""
    spec = importlib.util.spec_from_file_location(
        "_drill", os.path.join(ROOT, "tools", "drill.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.TARGETS


TARGETS = _targets()


def read_log():
    rows = []
    if not os.path.exists(LOG):
        return rows
    with open(LOG) as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 5 or p[0] == "date":
                continue
            try:
                rows.append({
                    "date": datetime.strptime(p[0], "%Y-%m-%d").date(),
                    "module": p[1], "variant": p[2], "minutes": float(p[3]),
                    "clean": p[4].strip().lower() in ("y", "yes", "1", "true"),
                })
            except ValueError:
                continue
    return rows


def read_splits():
    rows = []
    if not os.path.exists(SPLITS):
        return rows
    with open(SPLITS) as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 5 or p[0] == "date":
                continue
            try:
                rows.append({"date": datetime.strptime(p[0], "%Y-%m-%d").date(),
                             "module": p[1], "phase": p[3], "minutes": float(p[4])})
            except ValueError:
                continue
    return rows


def phase_report(rows):
    if not rows:
        print("\n  (no phase splits yet — call `make lap` during a rep to get this)\n")
        return
    print("\n" + "=" * 70)
    print("  WHERE THE TIME GOES — this is the diagnosis, not the score.")
    print("=" * 70)

    def block(subset, label):
        tot = sum(r["minutes"] for r in subset)
        if not tot:
            return None
        agg = defaultdict(float)
        for r in subset:
            agg[r["phase"]] += r["minutes"]
        print(f"\n  {label}")
        shares = {}
        for ph in ("design", "write", "compile", "debug"):
            if ph in agg:
                pct = 100 * agg[ph] / tot
                shares[ph] = pct
                print(f"    {ph:<8} {agg[ph]:>7.1f} min  {pct:>4.0f}%  {'#' * int(pct / 3)}")
        for ph in sorted(k for k in agg if k not in ("design", "write", "compile", "debug")):
            pct = 100 * agg[ph] / tot
            print(f"    {ph:<8} {agg[ph]:>7.1f} min  {pct:>4.0f}%")
        return shares

    all_shares = block(rows, "All reps")

    recent = sorted(rows, key=lambda r: r["date"])[-40:]
    first = sorted(rows, key=lambda r: r["date"])[:40]
    if len(rows) > 60:
        block(first, "First reps")
        block(recent, "Recent reps")

    if not all_shares:
        return
    top = max(all_shares, key=all_shares.get)
    print("\n  Reading it:")
    verdicts = {
        "design": "Most time before you type. You don't know the pattern yet — reread the BRIEF\n"
                  "           and draw the invariant on paper before the timer next time.",
        "write":  "Most time typing. That is the syntax-fluency gap, and it is exactly the one\n"
                  "           you set out to fix. It should shrink faster than the others.",
        "compile": "Most time fighting the compiler. Syntax errors, not logic. Slow down while\n"
                   "           typing — a 20%% slower first pass usually beats three compile cycles.",
        "debug":  "Most time after it compiles. Logic and edge cases. Try writing the test you'd\n"
                  "           add BEFORE the implementation on the next rep.",
    }
    print(f"    Largest share: {top} ({all_shares[top]:.0f}%). {verdicts[top]}")
    if "write" in all_shares and "compile" in all_shares:
        wc = all_shares["write"] + all_shares["compile"]
        print(f"\n    write + compile = {wc:.0f}% of your time. That combined number IS your")
        print("    syntax fluency. Watch it fall. Under 40% by week 10 is the target.")


def sparkline(values):
    if not values:
        return ""
    blocks = "▁▂▃▄▅▆▇█"
    lo, hi = min(values), max(values)
    if hi == lo:
        return blocks[3] * len(values)
    return "".join(blocks[int((v - lo) / (hi - lo) * (len(blocks) - 1))] for v in values)


def main():
    rows = read_log()
    if not rows:
        print(f"No reps logged yet ({LOG}). Run `make drill`.")
        return

    print("\n" + "=" * 70)
    print("  TIME CURVE — oldest to newest. Want: falling, then flat.")
    print("=" * 70)
    by_kata = defaultdict(list)
    for r in rows:
        by_kata[r["module"]].append(r)

    for kata in sorted(by_kata):
        reps = by_kata[kata]
        mins = [r["minutes"] for r in reps]
        target = TARGETS.get(kata, 15)
        recent = mins[-3:]
        avg_recent = sum(recent) / len(recent)
        flag = "ok " if avg_recent <= target else "..."
        print(f"  {flag} {kata:<18} {sparkline(mins):<14} "
              f"first {mins[0]:>5.1f}  last {mins[-1]:>5.1f}  target {target:>2}  n={len(mins)}")

    # C and Python are reported separately and never combined. C1's bar is the
    # clean-first-*compile* rate; a Python kata has no compile step, so "clean" there means
    # "ran first try, no traceback". Averaging the two produces a number that is not
    # evidence for either capability. progress.py:clean_rate() draws the same line.
    for label, want, note in (
            ("CLEAN FIRST COMPILE — the C syntax-fluency proxy.", False,
             "  40% by week 4, 55% by week 6, 70% by week 10.  (C1)"),
            ("CLEAN FIRST RUN — the Python equivalent.", True,
             "  No traceback on the first run. Reported apart from C on purpose.  (Y2, Y3)")):
        subset = [r for r in rows if r["module"].endswith("_py") == want]
        if not subset:
            continue
        print("\n" + "=" * 70)
        print(f"  {label}")
        print(note)
        print("=" * 70)
        weeks = defaultdict(list)
        for r in subset:
            monday = r["date"] - timedelta(days=r["date"].weekday())
            weeks[monday].append(r)
        for wk in sorted(weeks):
            reps = weeks[wk]
            clean = sum(1 for r in reps if r["clean"])
            pct = round(100 * clean / len(reps))
            bar = "#" * (pct // 5)
            print(f"  week of {wk}  {len(reps):>2} reps  {pct:>3}% clean  {bar}")
        overall = round(100 * sum(1 for r in subset if r["clean"]) / len(subset))
        print(f"\n  Overall: {overall}% clean across {len(subset)} reps.")

    phase_report(read_splits())

    print("\n" + "=" * 70)
    print("  COVERAGE — what you're avoiding.")
    print("=" * 70)
    all_katas = sorted(
        d for d in os.listdir(KATAS)
        if os.path.isdir(os.path.join(KATAS, d)) and not d.startswith(".")
    ) if os.path.isdir(KATAS) else []
    today = date.today()
    for kata in all_katas:
        reps = by_kata.get(kata, [])
        if not reps:
            print(f"  !!  {kata:<18} never attempted")
        else:
            days = (today - reps[-1]["date"]).days
            mark = "!! " if days > 14 else "   "
            print(f"  {mark} {kata:<18} {len(reps):>2} reps, last {days}d ago")

    print("\n" + "=" * 70)
    print("  If the time curve is flat and the clean rate isn't rising, you are not")
    print("  improving, whatever it feels like. That's what this report is for.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
