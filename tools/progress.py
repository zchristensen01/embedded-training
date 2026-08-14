#!/usr/bin/env python3
"""progress.py — score the capability list and write the public progress report.

  python3 tools/progress.py            print the summary
  python3 tools/progress.py --write    also write logs/PROGRESS.md and logs/progress.json
  python3 tools/progress.py --check    exit non-zero if the spec and the coverage map
                                       disagree, or a capability has no mechanism

This is the file a website can read. `logs/progress.json` is stable, machine-shaped
output: every capability, who owns it, whether its evidence bar is met, and the
numbers behind that. `logs/PROGRESS.md` is the same thing rendered for a human.

Nothing here is self-reported. A capability moves to "met" only when the evidence bar
in plan/INTERVIEW_REQUIREMENTS.md is met by something in logs/ or by deck state:

  C  kata    three consecutive clean reps at or under target, across three variants
  C1 log     the clean-first-compile rate itself, over enough reps to mean something
  E  deck    80% of the cards tagged with that ID are in box 4 or 5, min 3 (see
             DECK_PROPORTION — it used to be all of them, which punished adding cards)
  H  deck    same as E, where a card owns it. Bench items are Mimic's and say so
  T  deck    same as E. Project items need the harness repo and say so
  T1 prompts enough scored answers, and the recent ones scoring at the bar
  B  story   three takes rated strong, on three different days

The ownership map is parsed out of plan/COVERAGE.md rather than duplicated here, and
the capability list out of plan/INTERVIEW_REQUIREMENTS.md, so this file holds no
third copy of either. The count of capabilities is not hardcoded anywhere: --check
proves the two files describe exactly the same set.
"""
import argparse
import glob
import importlib.util
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQ = os.path.join(ROOT, "plan", "INTERVIEW_REQUIREMENTS.md")
COV = os.path.join(ROOT, "plan", "COVERAGE.md")
DECKS = os.path.join(ROOT, "practice", "decks")
DECK_STATE = os.path.join(DECKS, ".state.json")
LOG = os.path.join(ROOT, "logs", "log.tsv")
PROMPTS = os.path.join(ROOT, "logs", "design-prompts")
DESIGNS = os.path.join(ROOT, "logs", "architecture")
OUT_MD = os.path.join(ROOT, "logs", "PROGRESS.md")
OUT_JSON = os.path.join(ROOT, "logs", "progress.json")

GROUPS = {"C": "C language and syntax fluency", "Y": "Python fluency",
          "E": "Embedded concepts", "H": "Hardware, signals and debugging",
          "T": "Test and integration", "B": "Behavioural and narrative"}

# Every capability-ID regex below is built from GROUPS rather than spelling the letters
# out. Adding a group used to mean finding five separate `[CEHTB]` character classes,
# and missing one did not fail loudly: a group the regex cannot see is absent from both
# sides of `--check`, so the spec and the coverage map agree about nothing and the check
# passes while scoring zero capabilities. One source, derived.
GRP = "[" + "".join(GROUPS) + "]"

MASTERED_BOX = 4          # a deck card counts once it reaches box 4

# How many of a capability's cards have to be at MASTERED_BOX for it to be met.
#
# This was "all of them", which made the bar wildly uneven and pointed the incentive the
# wrong way. H7 has one card and needed one; T11 has nine and needed nine; Y1 has twenty
# and needed twenty. Worse, *adding a good card to a capability made that capability
# harder to meet* — so the system that tells you to run `make card` whenever something
# surprises you was quietly punishing you for doing it.
#
# A proportion with a floor fixes both. The floor matters because 80% of two cards is two,
# and a capability resting on one or two cards should not be meetable on a single lucky
# card; the min() matters because a capability cannot need more cards than it has.
DECK_PROPORTION = 0.8
DECK_FLOOR = 3

# C1's bar is stated in the spec as a rate, not as a retired kata: "70%+ clean-first-
# compile rate over 20 logged reps". It is the only capability measured across every
# module rather than on one of them, so it gets its own arm below.
C1_CLEAN_RATE = 0.70
C1_MIN_REPS = 20

# T1's bar is "Rubric score 12+/16, requirements asked first" — a score, not a count.
# The count is still there because T1 is a skill measured across subjects rather than
# on one answer, but a stack of unscored files no longer meets it.
PROMPTS_FOR_T1 = 10
PROMPT_SCORE_BAR = 12
PROMPT_RECENT = 3         # the most recent N answers must all clear the bar

# E30's bar is three designs, not ten. T1's subject rotates across 60 subjects and
# the skill is breadth; an architecture round is one deep 45-minute exercise and three of
# them scored at the bar is a real claim. Same rubric denominator, same recency rule.
DESIGNS_FOR_E30 = 3
DESIGN_SCORE_BAR = 12
DESIGN_PUSHBACK_MIN = 1   # axis 8 must be non-zero — see designs_met()


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def drill_targets():
    return _load("_drill", os.path.join(ROOT, "tools", "drill.py")).TARGETS


def rehearsal():
    """rehearse.py owns the definition of a ready story. Don't write a second one."""
    return _load("_rehearse", os.path.join(ROOT, "tools", "rehearse.py"))


def capabilities():
    """{id: statement} from the master checklist tables in the spec."""
    caps = {}
    for line in open(REQ):
        m = re.match(rf"^\|\s*({GRP}\d+)\s*\|\s*(.+?)\s*\|", line)
        if m:
            caps[m.group(1)] = m.group(2)
    return caps


def _expand_ids(label):
    """'B5' -> ['B5'];  'B5-B9' / 'B5–B9' -> ['B5','B6',...,'B9']."""
    m = re.match(rf"^({GRP})(\d+)\s*[–—-]\s*{GRP}?(\d+)$", label.strip())
    if m:
        g, lo, hi = m.group(1), int(m.group(2)), int(m.group(3))
        return [f"{g}{n}" for n in range(lo, hi + 1)]
    m = re.match(rf"^({GRP}\d+)$", label.strip())
    return [m.group(1)] if m else []


def ownership():
    """{id: {'owners': set, 'katas': [..], 'note': str}} parsed from COVERAGE.md.

    Owner cells are prose, not a schema. Real shapes in the file include `**D + K**`,
    `**D** + M0 S3`, `**K** \\`ring_buffer\\` + M0 incidental`, `**M0/M1**`,
    `**R**, sourced from **M0 S12 + P**` and `**Design prompts** (\\`make prompt\\`)`.
    So: take the whole cell, not just what is inside the bold markers, and pick the
    owner tokens out of it. Matching only `**X**` misses every combined cell, which
    is most of them.

    This is the brittlest thing in the repo. What keeps it honest is `--check`, which
    proves every capability in the spec has exactly one row here and vice versa — so
    a reworded cell that stops parsing is a CI failure, not a silent zero.
    """
    own = {}
    for line in open(COV):
        m = re.match(rf"^\|\s*({GRP}\d+(?:\s*[–—-]\s*{GRP}?\d+)?)\s[^|]*\|"
                     r"\s*(.+?)\s*\|\s*(.*?)\s*\|", line)
        if not m:
            continue
        label, cell, note = m.groups()
        flat = cell.replace("*", "")
        owners = set()
        for tok, code in (("Design prompts", "PROMPT"), ("Architecture drill", "DESIGN"),
                          ("Deferred", "DEFER"), ("M0", "M0"), ("M1", "M1")):
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


def bar_for(cid, owners):
    """Which single mechanism decides whether this capability is met.

    A capability often has several mechanisms; only one of them is the *bar*. The
    spec's "Scoring yourself" section sets it per group: C is the kata log, E is deck
    boxes, B is rated takes. Requiring every listed mechanism instead would mean E1 —
    a verbal question whose bar is "said aloud with the trap named" — could not be
    met until a kata was also retired, which is stricter than the spec.

    Order matters, and one ordering bug lived here for a while: Mimic used to be
    tested before the kata, so E23 and E24 — both `**K** + M0` — were reported as
    proved at the bench when this repo owns the kata that proves them. A kata in this
    repo always outranks work tracked elsewhere.
    """
    if "DEFER" in owners:
        return "deferred"
    if cid == "C1":
        return "clean rate"
    if cid[0] == "C":
        return "kata" if "K" in owners else ("deck" if "D" in owners else "")
    # Y is a fluency group like C, so it takes C's precedence rather than the default
    # below: a kata outranks a deck card. Without this arm Y2 and Y3 — whose bars are
    # logged reps against binary_frame_py and log_parser_py — would fall through to the
    # generic "D before K" order and be scored on the deck instead, which measures
    # whether you can *say* the answer rather than whether you can write it cold.
    if cid[0] == "Y":
        return "kata" if "K" in owners else ("deck" if "D" in owners else "")
    if cid[0] == "B":
        return "rehearsal"
    if "PROMPT" in owners:
        return "design prompts"
    if "DESIGN" in owners:
        return "architecture drills"
    if "D" in owners:
        return "deck"
    if "K" in owners:
        return "kata"
    if "P" in owners:
        return "HIL project"
    if owners & {"M0", "M1"}:
        return "Mimic"
    return ""


def cards_needed(n):
    """How many of a capability's n cards must be at MASTERED_BOX for it to be met.

    One definition, because check_decks.py reports it and score() enforces it, and a
    second copy would drift. See DECK_PROPORTION for why it is a proportion.
    """
    return max(min(DECK_FLOOR, n), -(-int(DECK_PROPORTION * 100) * n // 100))


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


def scored_answers(directory):
    """[(path, score_or_None)] for every rubric-scored answer in a directory.

    The score is the rubric total the file carries. Both `make prompt` and `make design`
    write their rubric into the file with a blank total; you fill it in. An unscored
    answer counts toward the volume but never toward the bar.

    Both rubrics are out of 16 on purpose, so one parse serves both. They are different
    rubrics — one asks how you would test a thing, the other asks you to design one — and
    they live in different directories for exactly that reason.
    """
    out = []
    for path in sorted(glob.glob(os.path.join(directory, "*.md"))):
        score, gate = None, None
        try:
            text = open(path).read()
            m = re.search(r"Total:\s*(\d+)\s*/\s*16", text)
            if m:
                score = int(m.group(1))
            g = re.search(r"axis 8\):\s*(\d+)\s*/\s*2", text)
            if g:
                gate = int(g.group(1))
        except OSError:
            pass
        out.append((path, score, gate))
    return out


def prompt_answers():
    return scored_answers(PROMPTS)


def design_answers():
    return scored_answers(DESIGNS)


def deck_state():
    if os.path.exists(DECK_STATE):
        try:
            return json.load(open(DECK_STATE))
        except ValueError:
            return {}
    return {}


_KATA_REPS = None


def kata_reps():
    """Parsed once per process. score() and render_md() both want it, and re-reading meant
    parsing the file twice and printing the same warning twice. The log does not change
    under a running command."""
    global _KATA_REPS
    if _KATA_REPS is not None:
        return _KATA_REPS
    rows, bad = defaultdict(list), 0
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
            bad += 1
    if bad:
        print(f"warning: logs/log.tsv: skipped {bad} unparseable row(s). "
              f"Run `make check-log`.", file=sys.stderr)
    _KATA_REPS = rows
    return rows


def kata_retired(reps, target):
    """PRACTICE_SYSTEM's bar: three consecutive clean reps at target, three variants."""
    tail = reps[-3:]
    return (len(tail) == 3 and all(r["clean"] and r["minutes"] <= target for r in tail)
            and len({r["variant"] for r in tail}) == 3)


def clean_rate(reps):
    """(rate, n) across every C kata rep, ignoring Mimic/project and Python modules.

    C1's bar is the clean-*first-compile* rate, and a Python kata has no compile step —
    `clean` there means "ran first try, no traceback", which is a different claim about a
    different skill. Counting both in one number measures neither. Python fluency has its
    own bar in the Y group; this one is C's alone.
    """
    allr = [r for k, v in reps.items() for r in v
            if k not in ("mimic", "project") and not k.endswith("_py")]
    if not allr:
        return 0.0, 0
    return sum(1 for r in allr if r["clean"]) / len(allr), len(allr)


def score():
    caps, own = capabilities(), ownership()
    cards, st = deck_cards(), deck_state()
    reps, targets = kata_reps(), drill_targets()
    reh = rehearsal()
    takes = reh.read_log()
    prompts = prompt_answers()
    designs = design_answers()
    rate, nreps = clean_rate(reps)

    by_cap_cards = defaultdict(list)
    for card_id, cids in cards:
        for cid in cids:
            by_cap_cards[cid].append(card_id)

    results = {}
    for cid, statement in sorted(caps.items(), key=lambda kv: (kv[0][0], int(kv[0][1:]))):
        o = own.get(cid, {"owners": set(), "katas": [], "note": ""})
        owners, katas = o["owners"], o["katas"]
        bar = bar_for(cid, owners)
        mechanisms, detail = [], []
        card_ids = by_cap_cards.get(cid, [])

        # Every mechanism that touches this capability, for context. Cards tagged with
        # a capability whose bar is something else are real practice but not evidence,
        # and they say so rather than silently counting for nothing.
        if "K" in owners:
            mechanisms.append("kata" + (f" ({', '.join(katas)})" if katas else ""))
            for k in katas:
                detail.append(f"{k}: {len(reps.get(k, []))} rep(s)")
        if card_ids:
            suffix = "" if bar == "deck" else ", reinforcement"
            mechanisms.append(f"deck ({len(card_ids)} card{'s' if len(card_ids) > 1 else ''}"
                              f"{suffix})")
            if bar == "deck":
                detail.append("boxes " + ",".join(
                    str(st.get(i, {}).get("box", 0)) for i in card_ids))
        elif "D" in owners:
            mechanisms.append("deck (0 cards)")
        if "R" in owners:
            mechanisms.append("rehearsal")
            n = len([r for r in takes if r["story"] == cid])
            detail.append(f"{n} take(s)")
        if "PROMPT" in owners:
            mechanisms.append(f"design prompts ({len(prompts)} written)")
        if "DESIGN" in owners:
            mechanisms.append(f"architecture drills ({len(designs)} written)")
        if "P" in owners:
            mechanisms.append("HIL project")
            detail.append("evidence lives in the harness repo")
        if owners & {"M0", "M1"}:
            mechanisms.append("Mimic")
            detail.append("bench evidence lives in Mimic, not here")

        def deck_met():
            if not card_ids:
                return False
            at_box = sum(1 for i in card_ids
                         if st.get(i, {}).get("box", 0) >= MASTERED_BOX)
            return at_box >= cards_needed(len(card_ids))

        def kata_met():
            return bool(katas) and all(
                kata_retired(reps.get(k, []), targets.get(k, 15)) for k in katas)

        def prompts_met():
            scored = [s for _, s, _ in prompts[-PROMPT_RECENT:] if s is not None]
            return (len(prompts) >= PROMPTS_FOR_T1
                    and len(scored) == PROMPT_RECENT
                    and all(s >= PROMPT_SCORE_BAR for s in scored))

        def designs_met():
            # Two gates, not one. Seven perfect axes total 14/16, so a total-only bar can
            # be met with axis 8 — "held the position under pushback" — scored zero, which
            # is the half of E30 the research actually calls out as the rejection point.
            recent = designs[-DESIGNS_FOR_E30:]
            scored = [s for _, s, _ in recent if s is not None]
            pushed = [g for _, _, g in recent if g is not None and g >= DESIGN_PUSHBACK_MIN]
            return (len(designs) >= DESIGNS_FOR_E30
                    and len(scored) == DESIGNS_FOR_E30
                    and all(s >= DESIGN_SCORE_BAR for s in scored)
                    and len(pushed) == DESIGNS_FOR_E30)

        if bar == "deferred":
            mechanisms.append("deferred")
            detail.append("out of scope by decision — see plan/COVERAGE.md")
            done = None
        elif bar == "clean rate":
            done = nreps >= C1_MIN_REPS and rate >= C1_CLEAN_RATE
            mechanisms.append("the kata log")
            detail.append(f"{round(100 * rate)}% clean over {nreps} rep(s); "
                          f"bar is {round(100 * C1_CLEAN_RATE)}% over {C1_MIN_REPS}")
        elif bar == "kata":
            done = kata_met()
        elif bar == "deck":
            done = deck_met()
        elif bar == "rehearsal":
            done = reh.ready(cid, takes)
        elif bar == "design prompts":
            done = prompts_met()
            scored = [s for _, s, _ in prompts if s is not None]
            detail.append(f"{len(scored)} scored, bar is the last {PROMPT_RECENT} "
                          f"at {PROMPT_SCORE_BAR}+/16")
        elif bar == "architecture drills":
            done = designs_met()
            scored = [s for _, s, _ in designs if s is not None]
            detail.append(f"{len(scored)} scored, bar is {DESIGNS_FOR_E30} at "
                          f"{DESIGN_SCORE_BAR}+/16 with axis 8 non-zero")
        else:
            done = None                # tracked outside this repo, or nothing owns it

        results[cid] = {
            "id": cid, "group": cid[0], "statement": statement,
            "owners": sorted(owners), "mechanisms": mechanisms, "bar": bar,
            "done": done, "detail": detail, "cards": len(card_ids),
        }
    return results


def gaps(results):
    """Capabilities with no mechanism at all — the thing that must never be true."""
    return [r for r in results.values() if not r["mechanisms"]]


def consistency():
    """Problems that make the score itself untrustworthy. Returns a list of strings.

    The count of capabilities is deliberately not hardcoded. What is checked instead
    is that the spec and the coverage map describe the same set, and that each group
    is numbered 1..n with no gaps and no duplicates — so a row deleted from either
    file, or a typo'd ID, is a CI failure rather than a quietly smaller total.
    """
    problems = []
    caps, own = capabilities(), ownership()

    if not caps:
        return [f"{os.path.relpath(REQ, ROOT)}: no capabilities parsed — the spec is "
                f"empty or its tables changed shape"]

    for cid in sorted(set(caps) - set(own)):
        problems.append(f"{cid}: in the spec but has no row in plan/COVERAGE.md")
    for cid in sorted(set(own) - set(caps)):
        problems.append(f"{cid}: has a row in plan/COVERAGE.md but is not in the spec")

    by_group = defaultdict(list)
    for cid in caps:
        by_group[cid[0]].append(int(cid[1:]))
    # Every group heading in the spec must be a group this file knows about. Deriving GRP
    # from GROUPS stopped the five ID regexes drifting apart, but it does NOT catch the
    # inverse: add a `## Z — ...` section to the spec and forget GROUPS, and Z is invisible
    # to every regex, so it is absent from BOTH sides of the comparison below and --check
    # passes while scoring nothing. Verified: injecting Z1 into both files still reported
    # "all 99 capabilities are in both files". This assertion is the missing direction.
    headings = set(re.findall(r"^##\s+([A-Z])\s+—\s", open(REQ).read(), re.M))
    unknown = headings - set(GROUPS)
    if unknown:
        problems.append(
            f"group heading(s) {', '.join(sorted(unknown))} in the spec are not in "
            f"tools/progress.py:GROUPS, so nothing can see them. Add them there."
        )

    for g in sorted(GROUPS):
        nums = sorted(by_group.get(g, []))
        if not nums:
            problems.append(f"group {g}: no capabilities found in the spec")
            continue
        if nums != list(range(1, len(nums) + 1)):
            problems.append(
                f"group {g}: numbered {nums} — must run 1..{len(nums)} with no gaps "
                f"or duplicates"
            )
    return problems


def render_md(results):
    L = []
    a = L.append
    total = len(results)
    scorable = [r for r in results.values() if r["done"] is not None]
    done = [r for r in scorable if r["done"]]
    deferred = [r for r in results.values() if r["bar"] == "deferred"]
    elsewhere = [r for r in results.values()
                 if r["done"] is None and r["bar"] != "deferred"]

    a("# Progress")
    a("")
    a(f"Generated by `make progress` on {date.today().isoformat()}. Do not edit by hand.")
    a("")
    a(f"**{len(done)} of {len(scorable)} scorable capabilities met.** "
      f"{len(elsewhere)} more are tracked outside this repo — bench work in Mimic and "
      f"artifacts in the harness — and are *not* verified here; "
      f"{len(deferred)} deferred by decision. {total} total.")
    a("")
    a("A capability is met only when its evidence bar is met and logged — three clean "
      "kata reps at target across three variants, most of a capability's deck cards in box "
      f"{MASTERED_BOX} or higher, or three strong takes of a story on three different "
      "days. Nothing here is a rating of how well something is known.")
    a("")
    a("The kata and rubric bars are measured: a clock, a compiler and a score out of 16. "
      f"The deck bar is graded by you, one card at a time — box {MASTERED_BOX} means you "
      "called yourself correct on four separate days, spaced out, with a wrong answer "
      "sending the card back to the start. That is real evidence and it is not the same "
      "kind of evidence. `plan/COVERAGE.md` says which bars are which.")
    a("")
    a("\"Tracked outside this repo\" means exactly that: the mechanism that would prove "
      "it lives somewhere this repo cannot see, so it is reported rather than counted. "
      "It is not a claim that the work is done.")
    a("")

    reps = kata_reps()
    a("## Katas")
    a("")
    if reps:
        rate, n = clean_rate(reps)
        a(f"{n} reps logged, {round(100 * rate)}% clean on first compile.")
        a("")
        a("| Module | Reps | Best clean | Last | Target | Trend |")
        a("|---|---|---|---|---|---|")
        targets = drill_targets()
        for k in sorted(reps):
            v = reps[k]
            cl = [r["minutes"] for r in v if r["clean"]]
            first, last = v[0]["minutes"], v[-1]["minutes"]
            arrow = "falling" if last < first else ("flat" if last == first else "rising")
            best = f"{min(cl):g} min" if cl else "—"
            a(f"| `{k}` | {len(v)} | {best} | {last:g} min | "
              f"{targets.get(k, 15)} min | {arrow} |")
        a("")
    else:
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
            elif r["bar"] == "deferred":
                status = "deferred"
            elif r["done"] is None:
                status = "tracked outside this repo"
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

    if args.check:
        problems = consistency()
        if problems:
            print(f"{len(problems)} problem(s) between the spec and the coverage map:")
            for p in problems:
                print(f"  - {p}")
            return 1
        results = score()
        missing = gaps(results)
        if missing:
            print(f"{len(missing)} capability/capabilities with no mechanism:")
            for r in missing:
                print(f"  - {r['id']}  {r['statement']}")
            return 1
        print(f"all {len(results)} capabilities are in both files and have a mechanism.")
        return 0

    results = score()
    missing = gaps(results)
    scorable = [r for r in results.values() if r["done"] is not None]
    done = [r for r in scorable if r["done"]]
    deferred = sum(1 for r in results.values() if r["bar"] == "deferred")
    print(f"\n  {len(done)}/{len(scorable)} scorable capabilities met "
          f"({len(results)} total, {len(results) - len(scorable) - deferred} tracked "
          f"outside this repo, {deferred} deferred)")
    for g, title in GROUPS.items():
        rows = [r for r in results.values() if r["group"] == g]
        met = sum(1 for r in rows if r["done"])
        ext = sum(1 for r in rows if r["done"] is None)
        bar = "#" * met + "." * (len(rows) - met - ext) + "~" * ext
        print(f"    {g}  {met:>2}/{len(rows):<2} {bar}   {title}")
    if missing:
        print(f"\n  {len(missing)} with NO mechanism: {', '.join(r['id'] for r in missing)}")
    print("\n  '#' met   '.' in progress   '~' tracked outside this repo\n")

    if args.write:
        os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
        with open(OUT_MD, "w") as fh:
            fh.write(render_md(results) + "\n")
        payload = {
            "generated": date.today().isoformat(),
            "totals": {"all": len(results), "scorable": len(scorable),
                       "met": len(done), "deferred": deferred,
                       "tracked_elsewhere": len(results) - len(scorable) - deferred},
            "capabilities": list(results.values()),
        }
        with open(OUT_JSON, "w") as fh:
            json.dump(payload, fh, indent=2)
        print(f"  Wrote {os.path.relpath(OUT_MD, ROOT)} and "
              f"{os.path.relpath(OUT_JSON, ROOT)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
