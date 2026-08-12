#!/usr/bin/env python3
"""progress.py — score the 78 capabilities and write the public progress report.

  python3 tools/progress.py            print the summary
  python3 tools/progress.py --write    also write logs/PROGRESS.md and logs/progress.json
  python3 tools/progress.py --check    exit non-zero if a capability has no mechanism

This is the file a website can read. `logs/progress.json` is stable, machine-shaped
output: every capability, who owns it, whether its evidence bar is met, and the
numbers behind that. `logs/PROGRESS.md` is the same thing rendered for a human.

Nothing here is self-reported. A capability moves to "done" only when the evidence
bar in plan/INTERVIEW_REQUIREMENTS.md is met by something in logs/ or by deck state:

  C  kata   three clean reps at or under target, across three different variants
  E  deck   every card tagged with that ID is in Leitner box 4 or 5
  H  deck   same as E, where a card owns it. Bench items are Mimic's and say so
  T  deck   same as E. Project items need the harness repo and say so
  B  story  three rated takes of that story in logs/rehearsal.tsv

The ownership map is parsed out of plan/COVERAGE.md rather than duplicated here, and
the capability list out of plan/INTERVIEW_REQUIREMENTS.md, so this file holds no
third copy of either.
"""
import argparse
import glob
import importlib.util
import json
import os
import re
from collections import defaultdict
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQ = os.path.join(ROOT, "plan", "INTERVIEW_REQUIREMENTS.md")
COV = os.path.join(ROOT, "plan", "COVERAGE.md")
DECKS = os.path.join(ROOT, "practice", "decks")
DECK_STATE = os.path.join(DECKS, ".state.json")
LOG = os.path.join(ROOT, "logs", "log.tsv")
REHEARSAL = os.path.join(ROOT, "logs", "rehearsal.tsv")
OUT_MD = os.path.join(ROOT, "logs", "PROGRESS.md")
OUT_JSON = os.path.join(ROOT, "logs", "progress.json")

GROUPS = {"C": "C language and syntax fluency", "E": "Embedded concepts",
          "H": "Hardware, signals and debugging", "T": "Test and integration",
          "B": "Behavioural and narrative"}

MASTERED_BOX = 4      # a deck card counts once it reaches box 4
STRONG_TAKES = 3      # a story counts at three rated takes
PROMPTS_FOR_T1 = 10   # T1 is a skill measured across subjects, not on one answer


def drill_targets():
    spec = importlib.util.spec_from_file_location("_d", os.path.join(ROOT, "tools", "drill.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.TARGETS


def capabilities():
    """{id: statement} for all 78, from the master checklist tables."""
    caps = {}
    for line in open(REQ):
        m = re.match(r"^\|\s*([CEHTB]\d+)\s*\|\s*(.+?)\s*\|", line)
        if m:
            caps[m.group(1)] = m.group(2)
    return caps


def _expand_ids(label):
    """'B5' -> ['B5'];  'B5-B9' / 'B5–B9' -> ['B5','B6',...,'B9']."""
    m = re.match(r"^([CEHTB])(\d+)\s*[–—-]\s*[CEHTB]?(\d+)$", label.strip())
    if m:
        g, lo, hi = m.group(1), int(m.group(2)), int(m.group(3))
        return [f"{g}{n}" for n in range(lo, hi + 1)]
    m = re.match(r"^([CEHTB]\d+)$", label.strip())
    return [m.group(1)] if m else []


def ownership():
    """{id: {'owners': set, 'katas': [..], 'note': str}} parsed from COVERAGE.md.

    Owner cells are prose, not a schema. Real shapes in the file include `**D + K**`,
    `**D** + M0 S3`, `**K** \\`ring_buffer\\` + M0 incidental`, `**M0/M1**`,
    `**R**, sourced from **M0 S12 + P**` and `**Design prompts** (\\`make prompt\\`)`.
    So: take the whole cell, not just what is inside the bold markers, and pick the
    owner tokens out of it. Matching only `**X**` misses every combined cell, which
    is most of them.
    """
    own = {}
    for line in open(COV):
        m = re.match(r"^\|\s*([CEHTB]\d+(?:\s*[–—-]\s*[CEHTB]?\d+)?)\s[^|]*\|"
                     r"\s*(.+?)\s*\|\s*(.*?)\s*\|", line)
        if not m:
            continue
        label, cell, note = m.groups()
        flat = cell.replace("*", "")
        owners = set()
        for tok, code in (("Design prompts", "PROMPT"), ("Deferred", "DEFER"),
                          ("M0", "M0"), ("M1", "M1")):
            if tok in flat:
                owners.add(code)
        # Single letters, only as standalone tokens, so the K in a kata name or the
        # D in a word is not mistaken for an owner code.
        for code in re.findall(r"(?<![A-Za-z`])([KDPR])(?![A-Za-z0-9_`])", flat):
            owners.add(code)
        katas = re.findall(r"`([a-z_0-9]+)`", cell)
        katas = [k for k in katas if not k.startswith("make ")]
        for cid in _expand_ids(label):
            own[cid] = {"owners": owners, "katas": katas, "note": note}
    return own


def deck_cards():
    """[(id_in_state, caps[])] for every card carrying a capability tag."""
    out = []
    for path in sorted(glob.glob(os.path.join(DECKS, "*.tsv"))):
        for i, line in enumerate(open(path)):
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            f = line.split("\t")
            if len(f) < 3:
                continue
            caps = [c.strip() for c in (f[4] if len(f) > 4 else "").split(",") if c.strip()]
            out.append((f"{os.path.basename(path)}:{i}", caps))
    return out


def prompt_answers():
    """Design-prompt answers written so far. T1 is the only capability they own."""
    return sorted(glob.glob(os.path.join(ROOT, "logs", "design-prompts", "*.md")))


def deck_state():
    if os.path.exists(DECK_STATE):
        try:
            return json.load(open(DECK_STATE))
        except ValueError:
            return {}
    return {}


def kata_reps():
    rows = defaultdict(list)
    if not os.path.exists(LOG):
        return rows
    for line in open(LOG):
        f = line.rstrip("\n").split("\t")
        if len(f) < 5 or f[0] == "date":
            continue
        try:
            rows[f[1]].append({"date": f[0], "variant": f[2], "minutes": float(f[3]),
                               "clean": f[4].strip().lower() == "y"})
        except ValueError:
            continue
    return rows


def story_takes():
    takes = defaultdict(list)
    if not os.path.exists(REHEARSAL):
        return takes
    for line in open(REHEARSAL):
        f = line.rstrip("\n").split("\t")
        if len(f) < 4 or f[0] == "date":
            continue
        takes[f[1].strip()].append(f)
    return takes


def kata_retired(reps, target):
    """PRACTICE_SYSTEM's bar: three consecutive clean reps at target, three variants."""
    tail = reps[-3:]
    return (len(tail) == 3 and all(r["clean"] and r["minutes"] <= target for r in tail)
            and len({r["variant"] for r in tail}) == 3)


def score():
    caps, own = capabilities(), ownership()
    cards, st = deck_cards(), deck_state()
    reps, takes, targets = kata_reps(), story_takes(), drill_targets()

    by_cap_cards = defaultdict(list)
    for card_id, cids in cards:
        for cid in cids:
            by_cap_cards[cid].append(card_id)

    results = {}
    for cid, statement in sorted(caps.items(), key=lambda kv: (kv[0][0], int(kv[0][1:]))):
        o = own.get(cid, {"owners": set(), "katas": [], "note": ""})
        owners, katas = o["owners"], o["katas"]
        mechanisms, detail = [], []
        card_ids = by_cap_cards.get(cid, [])

        # Every mechanism that touches this capability, for context.
        if "K" in owners:
            mechanisms.append("kata" + (f" ({', '.join(katas)})" if katas else ""))
            for k in katas:
                detail.append(f"{k}: {len(reps.get(k, []))} rep(s)")
        if "D" in owners:
            mechanisms.append(f"deck ({len(card_ids)} card(s))")
            if card_ids:
                detail.append("boxes " + ",".join(
                    str(st.get(i, {}).get("box", 0)) for i in card_ids))
        if "R" in owners:
            mechanisms.append("rehearsal")
            detail.append(f"{len(takes.get(cid, []))} take(s)")
        if "PROMPT" in owners:
            mechanisms.append(f"design prompts ({len(prompt_answers())} written)")
        if "P" in owners:
            mechanisms.append("HIL project")
            detail.append("evidence lives in the harness repo")
        if owners & {"M0", "M1"}:
            mechanisms.append("Mimic")
            detail.append("bench evidence lives in Mimic, not here")

        # But only ONE of them is the bar. plan/INTERVIEW_REQUIREMENTS.md's "Scoring
        # yourself" section sets it per group: C is the kata log, E is deck boxes, B
        # is rated takes. Requiring every listed mechanism instead would mean E1 —
        # a verbal question whose bar is "said aloud with the trap named" — could not
        # be met until a kata was also retired, which is stricter than the spec.
        def deck_met():
            return bool(card_ids) and all(
                st.get(i, {}).get("box", 0) >= MASTERED_BOX for i in card_ids)

        def kata_met():
            return bool(katas) and all(
                kata_retired(reps.get(k, []), targets.get(k, 15)) for k in katas)

        if "DEFER" in owners:
            mechanisms.append("deferred")
            detail.append("out of scope by decision — see plan/COVERAGE.md")
            done, bar = None, "deferred"
        elif cid[0] == "C":
            done = kata_met() if "K" in owners else (deck_met() if "D" in owners else None)
            bar = "kata"
        elif cid[0] == "B":
            done = len(takes.get(cid, [])) >= STRONG_TAKES
            bar = "rehearsal"
        elif "PROMPT" in owners:
            done = len(prompt_answers()) >= PROMPTS_FOR_T1
            bar = "design prompts"
        elif "D" in owners:
            done = deck_met()
            bar = "deck"
        elif "P" in owners:
            done, bar = None, "HIL project"          # proved in the harness repo
        elif owners & {"M0", "M1"}:
            done, bar = None, "Mimic"                # proved at the bench
        elif "K" in owners:
            done, bar = kata_met(), "kata"
        else:
            done, bar = None, ""

        results[cid] = {
            "id": cid, "group": cid[0], "statement": statement,
            "owners": sorted(owners), "mechanisms": mechanisms, "bar": bar,
            "done": done, "detail": detail, "cards": len(card_ids),
        }
    return results


def gaps(results):
    """Capabilities with no mechanism at all — the thing that must never be true."""
    return [r for r in results.values() if not r["mechanisms"]]


def render_md(results):
    L = []
    a = L.append
    total = len(results)
    scorable = [r for r in results.values() if r["done"] is not None]
    done = [r for r in scorable if r["done"]]
    external = [r for r in results.values() if r["done"] is None]

    a("# Progress")
    a("")
    a(f"Generated by `make progress` on {date.today().isoformat()}. Do not edit by hand.")
    a("")
    a(f"**{len(done)} of {len(scorable)} scorable capabilities met.** "
      f"{len(external)} more are proved outside this repo (bench work and the harness), "
      f"{total} total.")
    a("")
    a("A capability is met only when its evidence bar is met and logged — three clean "
      "kata reps at target across three variants, every tagged deck card in Leitner box "
      "4 or higher, or three rated takes of a story. Nothing here is self-assessed.")
    a("")

    reps = kata_reps()
    if reps:
        allr = [r for v in reps.values() for r in v]
        clean = sum(1 for r in allr if r["clean"])
        a("## Katas")
        a("")
        a(f"{len(allr)} reps logged, {round(100 * clean / len(allr))}% clean on first compile.")
        a("")
        a("| Module | Reps | Best clean | Last | Target | Trend |")
        a("|---|---|---|---|---|---|")
        targets = drill_targets()
        for k in sorted(reps):
            v = reps[k]
            cl = [r["minutes"] for r in v if r["clean"]]
            first, last = v[0]["minutes"], v[-1]["minutes"]
            arrow = "falling" if last < first else ("flat" if last == first else "rising")
            a(f"| `{k}` | {len(v)} | {min(cl):g} min |" if cl else f"| `{k}` | {len(v)} | — |"
              f" {last:g} min | {targets.get(k, 15)} min | {arrow} |")
        a("")
    else:
        a("## Katas")
        a("")
        a("No reps logged yet. `make drill` starts the first one.")
        a("")

    for g, title in GROUPS.items():
        rows = [r for r in results.values() if r["group"] == g]
        rows.sort(key=lambda r: int(r["id"][1:]))
        met = sum(1 for r in rows if r["done"])
        a(f"## {g} — {title}")
        a("")
        a(f"{met} of {len(rows)} met.")
        a("")
        a("| ID | Capability | Practised by | Status |")
        a("|---|---|---|---|")
        for r in rows:
            if r["done"] is True:
                status = "**met**"
            elif r["done"] is None:
                status = "outside this repo"
            else:
                status = "in progress"
            mech = ", ".join(r["mechanisms"]) or "**NO MECHANISM**"
            a(f"| {r['id']} | {r['statement']} | {mech} | {status} |")
        a("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    results = score()
    missing = gaps(results)

    if args.check:
        if missing:
            print(f"{len(missing)} capability/capabilities with no mechanism:")
            for r in missing:
                print(f"  - {r['id']}  {r['statement']}")
            return 1
        print(f"all {len(results)} capabilities have a mechanism.")
        return 0

    scorable = [r for r in results.values() if r["done"] is not None]
    done = [r for r in scorable if r["done"]]
    print(f"\n  {len(done)}/{len(scorable)} scorable capabilities met "
          f"({len(results)} total, {len(results) - len(scorable)} proved outside this repo)")
    for g, title in GROUPS.items():
        rows = [r for r in results.values() if r["group"] == g]
        met = sum(1 for r in rows if r["done"])
        ext = sum(1 for r in rows if r["done"] is None)
        bar = "#" * met + "." * (len(rows) - met - ext) + "~" * ext
        print(f"    {g}  {met:>2}/{len(rows):<2} {bar}   {title}")
    if missing:
        print(f"\n  {len(missing)} with NO mechanism: {', '.join(r['id'] for r in missing)}")
    print("\n  '#' met   '.' in progress   '~' proved outside this repo\n")

    if args.write:
        os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
        with open(OUT_MD, "w") as fh:
            fh.write(render_md(results) + "\n")
        payload = {
            "generated": date.today().isoformat(),
            "totals": {"all": len(results), "scorable": len(scorable), "met": len(done)},
            "capabilities": list(results.values()),
        }
        with open(OUT_JSON, "w") as fh:
            json.dump(payload, fh, indent=2)
        print(f"  Wrote {os.path.relpath(OUT_MD, ROOT)} and "
              f"{os.path.relpath(OUT_JSON, ROOT)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
