#!/usr/bin/env python3
"""drill.py — run one kata rep, with phase splits.

  python3 tools/drill.py start [KATA] [VARIANT]   pick, wipe src/, start the clock
  python3 tools/drill.py lap [PHASE]              record a split; auto-advances if no name
  python3 tools/drill.py done                     stop the clock, log the rep
  python3 tools/drill.py status                   what's in progress

The four phases, in order. Call `make lap` at each transition:

  design    start -> the first line of code you type
  write     first line -> your first compile attempt
  compile   first compile attempt -> it compiles clean
  debug     clean compile -> tests pass

The breakdown is the diagnosis. See `make report`.

Selection with no arguments: worst recent time first, then longest since last rep, then
never attempted. Will not repeat a kata within 3 days if alternatives exist. Only katas
that actually have a frozen header and test suite are eligible — see is_built().

TARGETS below is the one copy of the per-kata target time. report.py, check_log.py,
progress.py and schedule.py all import it from here, and schedule.py fails the build if
any target is longer than the calendar block that kata is scheduled into.
"""
import json
import os
import random
import re
import subprocess
import sys
import time
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KATAS = os.path.join(ROOT, "practice", "katas")
LOG = os.path.join(ROOT, "logs", "log.tsv")
SPLITS = os.path.join(ROOT, "logs", "splits.tsv")
STATE = os.path.join(ROOT, "logs", ".drill_state.json")

TARGETS = {
    "bitops": 8, "mem_primitives": 10, "register_map": 12, "debouncer": 12,
    "rollover_timer": 12, "ring_buffer": 15, "fsm": 15, "pool_allocator": 20,
    "protocol_parser": 20, "fixed_point_pid": 20, "concurrency_sim": 25,
    "test_harness_py": 25,
}

PHASES = ["design", "write", "compile", "debug"]

CONSTRAINT_CARDS = [
    "No dynamic allocation anywhere.",
    "Single return per function. No goto.",
    "Budget 2 KB RAM total. State your budget in a header comment.",
    "Add a peek() to the API without breaking the frozen tests.",
    "Must be safe against a single-producer ISR.",
    "Zero branches in the hot path.",
    "No standard library at all.",
    "Write it on paper first, then type it in. Timer runs during the paper phase.",
    "Name every variable in full words. No i, n, tmp, buf.",
    "Write the test you'd add before you write the implementation.",
]


def katas():
    if not os.path.isdir(KATAS):
        return []
    return sorted(
        d for d in os.listdir(KATAS)
        if os.path.isdir(os.path.join(KATAS, d)) and not d.startswith(".")
    )


def is_built(kata):
    """A kata is drillable once its frozen test suite exists — and, for C, a header.

    Every kata directory ships with a BRIEF and VARIANTS from day zero, so "the
    directory exists" is not the same as "you can do a rep against it". The adaptive
    picker used to rank never-attempted katas first, which meant Saturday of week 1
    would happily hand you a module whose header and tests you had not written yet.
    """
    tests = os.path.join(KATAS, kata, "tests")
    if not os.path.isdir(tests) or not os.listdir(tests):
        return False
    if kata.endswith("_py"):
        return any(f.endswith(".py") for f in os.listdir(tests))
    inc = os.path.join(KATAS, kata, "include")
    return (os.path.isdir(inc) and any(f.endswith(".h") for f in os.listdir(inc))
            and any(f.endswith(".c") for f in os.listdir(tests)))


def built_katas():
    return [k for k in katas() if is_built(k)]


def src_dir(kata):
    return os.path.join(KATAS, kata, "src")


def variants_for(kata):
    path = os.path.join(KATAS, kata, "VARIANTS.md")
    found = []
    if os.path.exists(path):
        with open(path) as fh:
            for line in fh:
                m = re.match(r"^(v\d+)\s+(.*)", line.strip())
                if m:
                    found.append((m.group(1), m.group(2)))
    return found or [("v1", "(no VARIANTS.md found)")]


def read_log():
    rows = []
    if not os.path.exists(LOG):
        return rows
    with open(LOG) as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 5 or parts[0] == "date":
                continue
            try:
                rows.append({
                    "date": parts[0], "module": parts[1], "variant": parts[2],
                    "minutes": float(parts[3]), "clean": parts[4].strip().lower() in ("y", "yes", "1", "true"),
                    "note": parts[5] if len(parts) > 5 else "",
                })
            except ValueError:
                continue
    return rows


def pick(rows):
    available = built_katas()
    if not available:
        sys.exit(
            "No kata has a header and a test suite yet, so there is nothing to drill\n"
            "cold. Build the day-0 four first — see SETUP.md, then:\n"
            "  make newkata NAME=bitops"
        )

    today = date.today()
    recent = set()
    for r in rows[-40:]:
        try:
            d = datetime.strptime(r["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        if (today - d).days < 3:
            recent.add(r["module"])

    pool = [k for k in available if k not in recent] or available

    def score(kata):
        mine = [r for r in rows if r["module"] == kata]
        if not mine:
            return (0, 0)           # never attempted -> highest priority
        last = mine[-1]
        target = TARGETS.get(kata, 15)
        over = last["minutes"] / target
        dirty = 0 if last["clean"] else 0.5
        try:
            days = (today - datetime.strptime(last["date"], "%Y-%m-%d").date()).days
        except ValueError:
            days = 0
        # A module one good rep away from meeting its bar is worth more than a module
        # that is merely stale. Saturday is the only slack in the rotation, so this is
        # where a nearly-there kata gets finished off.
        close = 0.4 if near_bar(mine, target) else 0.0
        return (1, -(over + dirty + close + days / 14.0))

    pool.sort(key=score)
    kata = pool[0]
    variant, desc = pick_variant(kata, rows)
    return kata, variant, desc


def near_bar(reps, target):
    """True when two of the last three reps already clear the bar for this module.

    The bar is three consecutive clean reps at target across three variants. Two out of
    three means one more good rep finishes it, and the picker should notice.
    """
    tail = reps[-2:]
    return (len(tail) == 2 and all(r["clean"] and r["minutes"] <= target for r in tail)
            and len({r["variant"] for r in tail}) == 2)


def pick_variant(kata, rows):
    """The variant you have done least recently, not a coin flip.

    `make drill KATA=x` used to pick uniformly at random, which meant free practice
    drifted toward whatever came up twice and left three variants untouched for weeks.
    Least-recently-used spreads it, and still varies because the *kata* choice varies.
    """
    vs = variants_for(kata)
    seen = {}
    for i, r in enumerate(rows):
        if r["module"] == kata:
            seen[r["variant"]] = i
    unseen = [(v, d) for v, d in vs if v not in seen]
    if unseen:
        return random.choice(unseen)
    return min(vs, key=lambda vd: seen.get(vd[0], -1))


def stub_for(kata):
    header = None
    inc = os.path.join(KATAS, kata, "include")
    if os.path.isdir(inc):
        hs = [f for f in os.listdir(inc) if f.endswith(".h")]
        if hs:
            header = hs[0]
    if kata.endswith("_py"):
        return f"{kata}.py", '"""Implementation. Written cold, every rep."""\n'
    name = (header[:-2] if header else kata) + ".c"
    inc_line = f'#include "{header}"\n' if header else ""
    return name, inc_line + "\n/* Your implementation. Nothing else was here when you started. */\n"


def cmd_start(argv):
    rows = read_log()
    if len(argv) >= 1:
        kata = argv[0]
        if kata not in katas():
            sys.exit(f"Unknown kata: {kata}. Have: {', '.join(katas())}")
        if not is_built(kata):
            sys.exit(
                f"{kata} has no frozen contract yet — you owe it a header and a test\n"
                f"suite before it can be drilled cold. A rep against an empty suite is\n"
                f"not a rep.\n"
                f"  make newkata NAME={kata}     then write include/ and tests/\n"
                f"Built and ready: {', '.join(built_katas()) or 'none yet'}"
            )
        vs = variants_for(kata)
        if len(argv) >= 2:
            variant = argv[1]
            if variant not in dict(vs):
                sys.exit(f"{kata} has no {variant}. Have: {', '.join(v for v, _ in vs)}")
            desc = dict(vs)[variant]
        else:
            variant, desc = pick_variant(kata, rows)
    else:
        kata, variant, desc = pick(rows)

    src = os.path.join(KATAS, kata, "src")
    if os.path.isdir(src):
        for f in os.listdir(src):
            os.remove(os.path.join(src, f))
    else:
        os.makedirs(src, exist_ok=True)

    fname, body = stub_for(kata)
    with open(os.path.join(src, fname), "w") as fh:
        fh.write(body)

    card = random.choice(CONSTRAINT_CARDS) if random.random() < 0.35 else None

    with open(STATE, "w") as fh:
        json.dump({"kata": kata, "variant": variant, "start": time.time(),
                   "card": card, "laps": [], "last": time.time()}, fh)

    target = TARGETS.get(kata, 15)
    print("=" * 66)
    print(f"  {kata}  {variant}")
    print(f"  {desc}")
    print("-" * 66)
    if card:
        print(f"  CONSTRAINT CARD: {card}")
        print("-" * 66)
    print(f"  Target: {target} min, clean, first compile.")
    print(f"  Wrote empty stub: katas/{kata}/src/{fname}")
    print(f"  Read BRIEF.md if you need the API. Do not read anything else.")
    print(f"  Clock is running. `make test` when ready, `make done` when passing.")
    print(f"  Call `make lap` at each transition: design -> write -> compile -> debug.")
    print("=" * 66)


def cmd_lap(argv):
    if not os.path.exists(STATE):
        sys.exit("No drill in progress. Run `make drill` first.")
    with open(STATE) as fh:
        st = json.load(fh)
    laps = st.get("laps", [])
    if argv:
        phase = argv[0]
    elif len(laps) < len(PHASES):
        phase = PHASES[len(laps)]
    else:
        phase = f"extra{len(laps) - len(PHASES) + 1}"
    now = time.time()
    mins = round((now - st.get("last", st["start"])) / 60.0, 2)
    laps.append({"phase": phase, "minutes": mins})
    st["laps"], st["last"] = laps, now
    with open(STATE, "w") as fh:
        json.dump(st, fh)
    total = round((now - st["start"]) / 60.0, 1)
    nxt = PHASES[len(laps)] if len(laps) < len(PHASES) else "done"
    print(f"  {phase:<8} {mins:>6.2f} min   (total {total} min)   next: {nxt}")


def cmd_done():
    if not os.path.exists(STATE):
        sys.exit("No drill in progress. Run `make drill` first.")
    with open(STATE) as fh:
        st = json.load(fh)
    now = time.time()
    minutes = round((now - st["start"]) / 60.0, 1)
    target = TARGETS.get(st["kata"], 15)

    laps = st.get("laps", [])
    if laps:
        remaining = round((now - st.get("last", st["start"])) / 60.0, 2)
        if remaining > 0.05:
            phase = PHASES[len(laps)] if len(laps) < len(PHASES) else "final"
            laps.append({"phase": phase, "minutes": remaining})

    print(f"\n{st['kata']} {st['variant']} — {minutes} min (target {target}).")
    if laps:
        print("  where the time went:")
        for lap in laps:
            pct = round(100 * lap["minutes"] / minutes) if minutes else 0
            bar = "#" * max(1, pct // 4)
            print(f"    {lap['phase']:<8} {lap['minutes']:>6.2f} min  {pct:>3}%  {bar}")
    clean = input("Clean? compiled first try, no sanitizer findings [y/N]: ").strip().lower()
    clean = "y" if clean in ("y", "yes") else "n"
    note = input("One line: a design decision or a bug you hit: ").strip()

    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    new = not os.path.exists(LOG)
    with open(LOG, "a") as fh:
        if new:
            fh.write("date\tmodule\tvariant\tminutes\tclean\tnote\n")
        fh.write(f"{date.today().isoformat()}\t{st['kata']}\t{st['variant']}\t{minutes}\t{clean}\t{note}\n")

    notes = os.path.join(KATAS, st["kata"], "NOTES.md")
    if note:
        with open(notes, "a") as fh:
            fh.write(f"- {date.today().isoformat()} {st['variant']} ({minutes}m): {note}\n")

    if laps:
        new_s = not os.path.exists(SPLITS)
        with open(SPLITS, "a") as fh:
            if new_s:
                fh.write("date\tmodule\tvariant\tphase\tminutes\n")
            for lap in laps:
                fh.write(f"{date.today().isoformat()}\t{st['kata']}\t{st['variant']}"
                         f"\t{lap['phase']}\t{lap['minutes']}\n")

    verdict = "under target" if minutes <= target else "over target"
    print(f"Logged. {verdict}.")

    # Snapshot the implementation before it is deleted by the next rep. This is the only
    # place a working solution is ever kept, and it is kept for exactly one purpose:
    # `make hunt` mutates an old one so you get practice debugging code you did not write
    # today. Gitignored, like src/ — the implementation is still disposable, this is just
    # a slower bin. See tools/bughunt.py.
    try:
        import bughunt
        snap = bughunt.save_snapshot(st["kata"], st["variant"], src_dir(st["kata"]))
        if snap:
            print(f"Snapshot kept for `make hunt` ({os.path.relpath(snap, ROOT)}).")
    except Exception:
        pass                         # a snapshot failure must never cost you the log

    # Ask here, before the state file goes, because this is the moment you are most
    # likely to have been surprised by something — and a card written now is worth
    # several written next Sunday from memory. card.py reads the state file to know
    # which kata you were on, so the prompt has to come first.
    add = input("Anything surprise you? Add a deck card [y/N]: ").strip().lower()
    if add in ("y", "yes"):
        subprocess.call([sys.executable, os.path.join(ROOT, "tools", "card.py")])

    os.remove(STATE)
    print("Commit it.")


def cmd_status():
    if not os.path.exists(STATE):
        print("Nothing in progress.")
        return
    with open(STATE) as fh:
        st = json.load(fh)
    mins = round((time.time() - st["start"]) / 60.0, 1)
    laps = st.get("laps", [])
    print(f"{st['kata']} {st['variant']} — {mins} min elapsed.")
    for lap in laps:
        print(f"  {lap['phase']:<8} {lap['minutes']:>6.2f} min")
    nxt = PHASES[len(laps)] if len(laps) < len(PHASES) else "done"
    print(f"  current phase: {nxt}")
    if st.get("card"):
        print(f"Constraint: {st['card']}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "start"
    if cmd == "start":
        cmd_start(sys.argv[2:])
    elif cmd == "lap":
        cmd_lap(sys.argv[2:])
    elif cmd == "done":
        cmd_done()
    elif cmd == "status":
        cmd_status()
    else:
        sys.exit(__doc__)
