#!/usr/bin/env python3
"""schedule.py — generate CALENDAR.md, all 98 days, with timers and kata assignments.

  python3 tools/schedule.py                 to stdout, dated if logs/.start_date exists
  python3 tools/schedule.py 2026-08-17      to stdout, dated from that Monday
  python3 tools/schedule.py --write         write plan/CALENDAR.md      (always relative)
  python3 tools/schedule.py --dates         write plan/CALENDAR.dated.md (gitignored)
  python3 tools/schedule.py --check         prove the schedule is internally consistent

Start on a Monday. If logs/.start_date exists it is used automatically.

CALENDAR.md is committed and carries relative day labels; CALENDAR.dated.md is your
local view with real dates. Mixing the two is what `--write` used to do, and it broke
`make check-generated` on any machine with a different start date.

This file is the single source for: the kata rotation, the day shapes, the main-block
text for every week, and — derived from the rotation — the kata build plan. Nothing
here should be copied into a document; documents should point at the generated
calendar instead.
"""
import importlib.util
import os
import re
import sys
import textwrap
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "plan", "CALENDAR.md")
# The dated view. Gitignored: your start date is yours, not the repo's. See the
# note at the bottom of this file for why the two are separate files.
OUT_DATED = os.path.join(ROOT, "plan", "CALENDAR.dated.md")
START_FILE = os.path.join(ROOT, "logs", ".start_date")

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Fourteen weeks, not ten. The kata bar — three consecutive clean reps at target across
# three variants — needs 12 to 17 reps on a module, and ten weeks could only ever hand out
# three to ten. Simulated over the old rotation, no C capability retired in more than 48%
# of runs and six retired in 0%. Ten weeks bought the time curve and not the bar.
#
# The four extra weeks buy reps, and the phases stretch to fill them rather than new
# material being invented: Mimic Stage 0 gets eight weeks instead of six, the harness two
# instead of one, and interview simulation two instead of one.
WEEKS = 14

# Wed and Sun are LONG rep days. Mon/Tue/Thu/Fri are SPRINT. Saturday is adaptive and
# gets a long block, because the picker may hand you anything.
LONG_DAYS = {"Wed", "Sun"}


def _targets():
    """Per-kata target minutes, read from drill.py so there is only one copy."""
    spec = importlib.util.spec_from_file_location(
        "_drill", os.path.join(ROOT, "tools", "drill.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.TARGETS


TARGETS = _targets()

# The block a kata gets has to be longer than the time you are trying to beat, or the
# calendar is asking for something the timer forbids. `--check` enforces block >=
# target for every scheduled rep, so these two numbers and drill.py's TARGETS can
# never drift apart silently again.
# Every block is STRICTLY longer than the target of anything scheduled into it, and check #7
# enforces the strict version. Equal is not good enough and used to be allowed: ring_buffer
# has a 15-minute target and sat in a 15-minute block, so the timer rang exactly at target.
# You could never log an over-target rep — the rule says stop when it rings — which censors
# the time curve at the target for the one kata whose curve matters most.
SPRINT_BLOCK = 18     # Mon, Tue, Thu, Fri — the short C modules
LONG_BLOCK = 28       # Wed, Sun, and Saturday's adaptive rep — the ones that need real time
PY_BLOCK = 28         # the Python rep, beside the C one

# A weekday is this long, and the main block is whatever is left after the fixed slots.
# Writing it as a total rather than hardcoding "90 - BLOCK - 20" in two places means
# adding a slot changes one number instead of silently making every day longer.
# Rehearsal starts in week 3: STORIES.md is written at the end of week 2 (see WEEKEND[2]),
# and a take against an unwritten story is not a take.
#
# The B group's bar is three takes rated strong on three DIFFERENT days, per story. With
# 11 stories that is 33 takes minimum, and check #9 fails the build if the calendar stops
# providing them. Adding B11 without adding slots is exactly how this broke the first time:
# the arithmetic had closed at ten stories and nothing was watching it.
REHEARSAL_FROM = 3
SUNDAY_TAKES = 3
SAT_TAKES = 1
SAT_TAKES_LATE = 2      # from week 11: the run-up to the simulation weeks
SAT_LATE_FROM = 11


def rehearsal_takes(day, week):
    """How many behavioural takes a given day schedules. One place, so check #9 and the
    rendered calendar can never disagree about the total."""
    if week < REHEARSAL_FROM:
        return 0
    if day == "Sun":
        return SUNDAY_TAKES
    if day == "Sat":
        return SAT_TAKES_LATE if week >= SAT_LATE_FROM else SAT_TAKES
    return 0


def rehearse_text(n):
    if n == 1:
        return "make rehearse  (one story, out loud, timed)"
    return f"make rehearse x{n}  ({n} stories, out loud, timed)"


# The architecture drill — `make design`, which is E30's bar and B11's material.
#
# This had NO slot at all: `make design` appeared zero times in seventy days, so the one
# capability with a mechanism built for it alone could not be met by anyone following the
# plan, and B11 had nothing to defend. Check #10 now fails the build if that recurs.
#
# FOUR slots, not the three the bar asks for. progress.py:designs_met() scores the LAST
# three, so the extra one is there to absorb a weak first attempt — the same reasoning
# that gives the rehearsal arithmetic its slack, applied to the mechanism that had none.
#
# 45 minutes because that is the round's real length, and Sunday because at 103 minutes it
# is the lightest day in the plan. This is genuinely new time — about 18 minutes a week
# averaged over the ten — rather than something taken off Mimic or the harness, both of
# which are producing evidence of their own.
DESIGN_BLOCK = 45
DESIGN_WEEKS = (6, 8, 10, 12)


# Stage 0 runs to week 8 now, so the gate that used to sit at week 6 moves with it. Both
# are derived from MIMIC rather than typed twice: the gate is the last Mimic week, because
# it is the week the exit tag has to exist by.
MIMIC_WEEKS = 8
GATE_WEEK = MIMIC_WEEKS

# The gate's rep floor, as a share of what the calendar actually schedules by then. A fixed
# number here goes stale every time the rotation changes, which is how it came to read "25+"
# against a calendar handing out 96.
GATE_REP_SHARE = 0.75

WEEKDAY_TOTAL = 115
FIXED_TAIL = 20       # Deck (12) + Log and commit (8)

# Stage 0 over eight weeks instead of six. The same twelve sessions, given the room the
# ten-week plan compressed out of them — S3 and S12 were each sharing a week with something
# else, and they are the two that bite.
MIMIC = {
    1: "S0 bench, toolchain, repo · S1 motor forensics and bolting it down",
    2: "S2 power topology and first soldering",
    3: "S3 encoder, interrupts, x4 decoding",
    4: "S4 open loop, both directions · S5 the fixed-rate loop, rate proven",
    5: "S6 units, convert at the boundary · S7 telemetry and the bandwidth budget",
    6: "S8 P only, stability boundary · S9 step-response metrics",
    7: "S10 D then I · S11 safety envelope and real PWM",
    8: "S12 the refactor, host-side tests, exit gate",
}

WEEKEND = {
    1: "S0/S1 overflow. Get the motor bolted down before anything else.",
    2: "S2 power. Draw the topology before you wire it. Solder. Then fill in "
       "practice/rehearsal/STORIES.md — the rehearsal slots start next week.",
    3: "S3 overflow. First logic-analyzer capture goes in docs/.",
    4: "S4/S5 overflow. Prove the loop rate, measured rather than intended.",
    5: "SWAP: Mimic M4.1 — EMG features on public datasets. Python, no hardware.",
    6: "S8/S9 tuning runs. Save every plot, including the bad ones.",
    7: "S10/S11 overflow. The safety envelope gets its own demonstration.",
    8: "S12 tests + exit gate evidence. Tag v0.0-stage0-exit.",
    9: "Device abstraction over a fake transport. Same tests pass on both.",
    10: "pyserial against the real board. Port discovery by USB serial number.",
    11: "Dockerise the harness. GitHub Actions, self-hosted runner.",
    12: "Harness repo published. README states what it verifies and what it cannot.",
    13: "Full mock loop: take-home, then defend it out loud. Record both.",
    14: "make report. Compare the week 1 and week 14 curves. Write the retro.",
}

# Weeks 9-14. Weeks 1-8 are Mimic; these are the ones with a programme of their own.
MAIN_LATE = {
    9: {"Mon": "pytest itself: discovery, assertions, exit codes. 20 tests on a pure function",
        "Tue": "Fixtures, scope, teardown that survives a failing test. conftest.py",
        "Wed": "parametrize. Then verification vs validation, test plan structure",
        "Thu": "Traceability, IEC 62304 classes, one test case per requirement",
        "Fri": "make prompt x3. Score each against the rubric"},
    10: {"Mon": "pyserial: open, write, read with timeout, frame responses. Talk to the board",
         "Tue": "Fixture that opens/closes the port and resets the device between tests",
         "Wed": "Flashing from the harness. Test isolation",
         "Thu": "Fault injection: truncated frames, bad CRC, impossible lengths. Assert recovery",
         "Fri": "Trace each test to a Stage 0 requirement. Requirement IDs in test names"},
    11: {"Mon": "Instrument driver over SCPI and PyVISA: timeout, error-queue drain, *OPC?",
         "Tue": "Log every result against the firmware build hash. T24 and T21 evidence",
         "Wed": "Green CI run against real hardware. Screenshot it",
         "Thu": "README: what it verifies, what it cannot catch, how tests trace to requirements",
         "Fri": "make prompt x3. Then the full protocol and hardware verbal set"},
    12: {"Mon": "Draft one OQ protocol for the rig: pass/fail criteria traced to a requirement",
         "Tue": "Reduce a raw capture: summary table, one plot, a written verdict. T28",
         "Wed": "make prompt x4. Score each",
         "Thu": "make rehearse x4. Sourced from Mimic NOTES and the tuning history",
         "Fri": "make rehearse x3  (S=B3, then S=B4, then S=B10). Record one, watch it back"},
    13: {"Mon": "Timed 2-hour mock take-home, AI-free: state machine, debugging, bit masking",
         "Tue": "Debrief the take-home out loud as if defending it. Record. Watch it back",
         "Wed": "Full deck pass. Every card box 4+ or it goes back to daily",
         "Thu": "make rehearse x2  (S=B10, timed). Then --stats: every story ready?",
         "Fri": "Mock verbal round: 20 cards cold, out loud, no reveal. Then make prompt x2"},
    14: {"Mon": "Second mock take-home, unseen shape: a failing suite you have to make green",
         "Tue": "Defend it live. Then make hunt on the oldest snapshot you have",
         "Wed": "Full deck pass, no filter. Anything below box 4 goes back to daily",
         "Thu": "make rehearse x4 across your weakest stories. Record two",
         "Fri": "Final mock verbal round, then make progress and read it honestly"},
}

DECK = {
    1: "bitops, memory", 2: "interrupts, memory", 3: "volatile, static, const",
    4: "memory, timing", 5: "protocols, timing", 6: "sync, rtos",
    7: "state machines, debug", 8: "debug, protocols",
    9: "v&v, traceability, test design", 10: "test infra, pytest",
    11: "ci, instruments", 12: "process, defects", 13: "python, bytes",
    14: "full deck, no filter",
}

# Not topics — the final week's instruction to stop filtering. check_decks.py validates that
# every other name here is a real topic in a deck, and skips these two.
#
# The focus is a THEME, not a filter: `make review` with no argument draws from everything due
# across all three decks. Nothing here changes what a deck pass shows you. See DAILY.md.
DECK_NOT_A_TOPIC = {"full deck", "no filter"}

# ------------------------------------------------------------------ rotation ---
#
# THE ROTATION IS GENERATED, not written out. What a human edits is INTRO below — the
# week each kata is first drilled — plus how many reps each one is owed.
#
# It used to be two hand-written dicts of week -> day -> (kata, variant), and they encoded
# a rep budget nobody had checked against the bar. Simulating the real rotation showed the
# result: no C capability retired in more than 48% of runs and six retired in 0%, because
# three consecutive clean reps at target needs 12-17 reps on a module and the calendar
# handed out three. Hand-maintaining that arithmetic across 15 katas and 14 weeks is not
# something anyone should do twice.
#
# So: say what each kata is owed, say when it may first appear, and let the generator place
# them. Variants cycle in order, which is what guarantees any three consecutive reps of a
# module use three different variants — the other half of the retirement bar.

# Reps owed. A kata that owns a capability's evidence bar needs enough to actually reach
# it; one that is reinforcement needs enough to be worth having built.
#
# 14 is measured, not guessed. Simulating a rep as `target x max(floor, 2.2 x 0.87^n)` with
# lognormal noise and a clean-first-compile rate rising to 95%, the chance that the last
# three reps are all clean and at target passes 80% at fourteen reps. It is uniform across
# katas because the curve is expressed in multiples of each kata's own target. Sensitivity:
# twelve if you improve fast (-18%/rep), seventeen if you improve slowly (-10%/rep).
REPS_FOR_BAR = 14
REPS_REINFORCEMENT = 4

# Overrides, where a kata is reinforcement but still worth more than the floor.
REPS_OVERRIDE = {"cli_tool_py": 5}

# No module goes longer than this without a rep, if it still has reps owed. A kata you have
# not touched in a fortnight is not being reinforced, it is being relearned.
#
# Without this, need-per-week alone decided everything, and a reinforcement module — four reps
# against a bar-owner's fourteen — was never the one "furthest behind pace". It lost every
# contest until the bar-owners finished, so its remaining reps piled up in weeks 12-14:
# protocol_parser ran day 10, then day 80. Seventy days is not a gap between reps, it is three
# separate first attempts, and it wasted the build session three times over.
#
# Ten days, measured rather than picked: at 14 the worst gap in the plan is still 18 days, at
# 12 it is 21, and at 10 it is 14 — which is the point where every module's second rep lands
# while the first is still yours. It costs the bar-owners nothing; they average a rep every
# seven days anyway and rarely trip it.
MAX_GAP_DAYS = 10

# The week each kata may first be drilled. Hand-authored, and the only ordering decision
# left: it is what makes week 1 the fundamentals and week 6 the concurrency work, and the
# build plan is still derived from it exactly as before — a kata cannot be drilled before
# the session that builds it.
INTRO = {
    "bitops": 1, "mem_primitives": 1, "ring_buffer": 1, "fsm": 1,
    "binary_frame_py": 1, "log_parser_py": 1,
    "register_map": 2, "protocol_parser": 2,
    "pool_allocator": 3,
    "debouncer": 4,
    "fixed_point_pid": 5, "rollover_timer": 5,
    "cli_tool_py": 6, "concurrency_sim": 6,
    "test_harness_py": 10,
}

# What each weekday holds, as a list of (kind, block). "c" is a C kata, "py" a Python one.
#
# Tuesday carries two short C reps and Sunday two long ones; every other weekday carries a
# C rep beside a Python rep. That is eight C slots and four Python slots a week, which is
# what the rep budget above needs — the old shape gave six and three and could not close.
DAY_SLOTS = {
    "Mon": [("c", SPRINT_BLOCK), ("py", PY_BLOCK)],
    "Tue": [("c", SPRINT_BLOCK), ("c", SPRINT_BLOCK)],
    "Wed": [("c", LONG_BLOCK), ("py", PY_BLOCK)],
    "Thu": [("c", SPRINT_BLOCK), ("py", PY_BLOCK)],
    "Fri": [("c", SPRINT_BLOCK), ("py", PY_BLOCK)],
    "Sun": [("c", LONG_BLOCK), ("c", LONG_BLOCK)],
}


def is_py(kata):
    return kata.endswith("_py")


def reps_wanted():
    """{kata: reps owed}. Bar-owners get the measured number, the rest the floor."""
    owning = set(_katas_that_own_a_bar())
    out = {}
    for kata in sorted(TARGETS):
        out[kata] = REPS_OVERRIDE.get(
            kata, REPS_FOR_BAR if kata in owning else REPS_REINFORCEMENT)
    return out


def _rotation():
    """{(week, day_index): [(kata, variant, block)]} for the whole plan.

    Greedy, deterministic and stable: at each slot take the eligible kata furthest behind
    the pace it needs to finish on time, breaking ties by whichever has waited longest and
    then by name. Eligible means introduced, the right language, and a target that fits the
    block. A kata is not repeated within two days if anything else can fill the slot.
    """
    want = reps_wanted()
    done = {k: 0 for k in want}
    last = {k: -99 for k in want}
    out = {}
    for week in range(1, WEEKS + 1):
        for i, day in enumerate(DAYS):
            slots = DAY_SLOTS.get(day, [])
            if not slots:
                continue
            placed = []
            for kind, block in slots:
                n = (week - 1) * 7 + i

                def eligible(want_py):
                    return [k for k in want
                            if INTRO.get(k, 99) <= week
                            and is_py(k) == want_py
                            and TARGETS[k] <= block
                            and done[k] < want[k]
                            and k not in placed]

                # The slot's language is a preference, not a rule. There are more Python
                # slots than Python reps owed, and without this the surplus sat empty in
                # the last three weeks while the C side was still short — 9 wasted slots
                # and 12 missing reps at the same time. A C kata that fits the block takes
                # the slot instead.
                pool = eligible(kind == "py") or eligible(kind != "py")
                if not pool:
                    continue
                fresh = [k for k in pool if n - last[k] >= 2] or pool
                weeks_left = max(1, WEEKS - week + 1)

                def urgency(k):
                    # Three tiers, in order.
                    #
                    # 1. A kata that has just been introduced gets its first rep promptly.
                    #    Without this, need-per-week alone deferred every low-rep module —
                    #    debouncer, protocol_parser, concurrency_sim — to week 11, eight
                    #    weeks after the session that built it. That wastes the build,
                    #    breaks the deck focus it was paired with, and makes `first_use`
                    #    disagree with INTRO, which the build plan is derived from.
                    # 2. Anything gone stale jumps the queue. Tier 1 only ever fixed the
                    #    FIRST rep; reps two onward were still deferred to the end of the
                    #    plan, so the same module got three cold starts instead of one
                    #    start and three reps. See MAX_GAP_DAYS.
                    # 3. Otherwise, furthest behind the pace it needs to finish on time.
                    gap = n - last[k]
                    return (done[k] == 0, gap >= MAX_GAP_DAYS,
                            (want[k] - done[k]) / weeks_left, gap, k)

                kata = max(fresh, key=urgency)
                variants = variants_in(kata) or ["v1"]
                variant = variants[done[kata] % len(variants)]
                out.setdefault((week, i), []).append((kata, variant, block))
                placed.append(kata)
                done[kata] += 1
                last[kata] = n
    return out


_ROTATION = None


def rotation():
    """The generated rotation, built once. Lazy because _rotation() reads the bar
    ownership out of progress.py, which imports this module back."""
    global _ROTATION
    if _ROTATION is None:
        _ROTATION = _rotation()
    return _ROTATION

PHASE = {**{w: "MIMIC STAGE 0" for w in range(1, 9)},
         9: "TEST ENGINEERING", 10: "THE HARNESS", 11: "THE HARNESS",
         12: "FINISH AND WRITE UP",
         13: "INTERVIEW SIMULATION", 14: "INTERVIEW SIMULATION"}

# --------------------------------------------------------------- build plan ---
#
# THE BUILD PLAN IS DERIVED FROM THE ROTATION ABOVE. Do not write it out by hand
# anywhere. A kata cannot be drilled before it exists, so the only thing a human
# should have to edit is KATA, and the build order follows from it. If you move a
# kata's first appearance earlier, its build session moves with it automatically.
#
# `python3 tools/schedule.py --check` proves the two agree. CI runs it.
#
# Sessions, as (build week, latest first-use this session covers, label). Week 0 is
# the Day 0 weekend, before the calendar starts.
#
# Five smaller sessions rather than three large ones, and that is a change forced by the
# arithmetic rather than a preference. Sunday now carries two long reps instead of one, so
# a session big enough to cover three katas puts the day over the cap below — week 1 came
# out at 301 minutes against a 300-minute limit, and the check said so. Smaller sessions
# spread over weeks 1-5 keep every Sunday well under it.
#
# The cost is real and worth naming: a build session is a running dependency, and five of
# them in a row means five Sundays where missing one leaves the next week's rotation short.
# It is still finite, it is still front-loaded, and after week 5 there is nothing left to
# build. Fourteen weeks is what makes that affordable; in ten it would not have been.
SESSIONS = [
    (0, 1, "Day 0 weekend"),
    (1, 2, "Week 1 Sunday"),
    (2, 3, "Week 2 Sunday"),
    (3, 4, "Week 3 Sunday"),
    (4, 5, "Week 4 Sunday"),
    (5, 99, "Week 5 Sunday"),
]

# Roughly what it costs to write one API contract plus a real test suite. The suite
# is the expensive half and it is the point — it is rep zero of "how would you test
# this." Anything you can write in twenty minutes is too shallow to rep against.
BUILD_MIN = {"ring_buffer": 90, "concurrency_sim": 90, "protocol_parser": 90}
BUILD_MIN_DEFAULT = 60

# Katas that are NOT built in a build session. {kata: (week, weekday, why)} — the
# point in the calendar by which the build is finished. Exempt from the build-session
# plan, but NOT from the check: the kata's first rep must fall strictly after that
# day. Week granularity would not be enough here; week 9's main block runs Mon-Fri
# and the kata does not exist until Friday closes.
EXEMPT = {
    "test_harness_py": (9, "Fri",
        "It is built by week 9's main block rather than by a build session. Week 9 is "
        "five consecutive days on pytest itself — discovery, assertions, fixtures, "
        "conftest.py, parametrize — and this kata is the artifact those five days "
        "produce. Giving it its own build slot would mean writing the same suite "
        "twice. This is a deliberate exception, not an oversight: it is the one "
        "module whose build IS the main work."),
}

# A Sunday longer than this is not a session, it's a lost weekend. This is measured
# against the WHOLE day, not just the build block — a five-and-a-half hour Sunday is
# a five-and-a-half hour Sunday however it is labelled.
SUNDAY_MAX_MIN = 300

# Notes appended to a kata in the build listing, where the build differs.
BUILD_NOTE = {
    "concurrency_sim": "builds under -fsanitize=thread, not address",
    "test_harness_py": "pytest, not compiled",
}


def block_for(day):
    """Minutes the kata timer gets on a given weekday."""
    return LONG_BLOCK if day in LONG_DAYS or day == "Sat" else SPRINT_BLOCK


def all_slots():
    """[(week, day_index, kata, variant, block)] across the whole plan, in order.

    A weekday holds more than one rep and they are not interchangeable — a Python slot and
    a C slot have different blocks and different eligible katas — so this walks the
    generated rotation rather than any per-day dict. Every check consumes this.
    """
    out = []
    for (week, i), slots in sorted(rotation().items()):
        for kata, variant, block in slots:
            out.append((week, i, kata, variant, block))
    return out


def first_use():
    """(week, weekday) each kata is first drilled. {kata: (w, d)}."""
    seen = {}
    for week, i, k, _, _ in all_slots():
        seen.setdefault(k, (week, i))
    return seen


def first_use_week():
    return {k: wd[0] for k, wd in first_use().items()}


def build_plan():
    """{build_week: (minutes, [katas])}, derived from first_use() and SESSIONS."""
    plan = {w: [] for w, _, _ in SESSIONS}
    for kata, week in sorted(first_use_week().items(), key=lambda kv: (kv[1], kv[0])):
        if kata in EXEMPT:
            continue
        for build_week, covers_through, _ in SESSIONS:
            if week <= covers_through:
                plan[build_week].append(kata)
                break
    return {w: (sum(BUILD_MIN.get(k, BUILD_MIN_DEFAULT) for k in ks), ks)
            for w, ks in plan.items() if ks}


def build_text(katas):
    """The build instruction for one session. Branches on language.

    "Write the header first" is wrong for a `*_py` kata — it has no header and no
    `include/`, its contract is the API in the BRIEF. The day-0 session builds two of
    them, so the generic wording was wrong on the very first instruction a new user
    reads. newkata.py already branches; this had not.
    """
    parts = [f"{k} ({BUILD_NOTE[k]})" if k in BUILD_NOTE else k for k in katas]
    py = [k for k in katas if k.endswith("_py")]
    if not py:
        first = "Write the header first"
    elif len(py) == len(katas):
        first = "Write the API into the BRIEF first — these have no header"
    else:
        has = "has" if len(py) == 1 else "have"
        first = (f"Write the contract first — the header for the C ones, and the API in "
                 f"the BRIEF for {', '.join(py)}, which {has} none")
    return (f"BUILD x{len(katas)}: " + ", ".join(parts)
            + f". {first}, then list the cases in the BRIEF, then write "
              "them. Every BRIEF ships with a 'What to test' section.")


def timers(day, week):
    """Return the timer blocks for a given weekday."""
    plan = build_plan()
    if day == "Sat":
        # No fixed kata here on purpose. The adaptive picker takes worst-recent-time
        # first, then longest-since-last-rep, then never-attempted — so Saturday is
        # the day that catches whatever you have been quietly avoiding. It gets a long
        # block because the picker may legitimately hand you concurrency_sim.
        blocks = [("Kata — adaptive", LONG_BLOCK,
                   "make drill   (no argument — picks your weakest built module)"),
                  ("Main block", 100, main_for(week, day))]
        n = rehearsal_takes("Sat", week)
        if n:
            blocks.append(("Rehearsal", 10 * n, rehearse_text(n)))
        return blocks
    if day == "Sun":
        blocks = [("Kata — LONG rep", block, f"make drill KATA={k} VARIANT={v}")
                  for k, v, block in rotation().get((week, DAYS.index("Sun")), [])]
        blocks += [("Weekly review", 20, "make report, then fill logs/WEEKLY_REVIEW.md"),
                   ("Deck — full pass", 15, "make review 30")]
        if week in plan:
            mins, katas = plan[week]
            blocks.append(("Kata build", mins, build_text(katas)))
        else:
            # T1 — "how would you test X" — is the highest-frequency T&I question and
            # one of the four listed reasons candidates get rejected.
            blocks.append(("Design prompt", 10, "make prompt  (T1 — ask for requirements first)"))
        # The architecture drill goes after the prompt and before the rehearsal, because
        # the three are one sequence: test a thing that exists, invent a thing, then
        # defend the thing you just invented. `make design` ends by telling you to run
        # `make rehearse S=B11`, and the rehearsal block below is where that take lands.
        if week in DESIGN_WEEKS:
            blocks.append(("Architecture drill", DESIGN_BLOCK,
                           "make design  (E30 — constraints first, numbers on the diagram)"))
        # Rehearsal runs on EVERY Sunday from REHEARSAL_FROM, build week or not. It used
        # to sit in the non-build branch only, which is part of how the B group quietly
        # became unreachable: the research says T&I candidates fail the behavioural round
        # more often than the technical one, so this is the wrong block to sacrifice to a
        # heavy Sunday. Check #9 proves the totals still close.
        n = rehearsal_takes("Sun", week)
        if n:
            blocks.append(("Rehearsal", 10 * n, rehearse_text(n)))
        return blocks
    slots = rotation().get((week, DAYS.index(day)), [])
    blocks = []
    for kata, variant, block in slots:
        if is_py(kata):
            label = "Kata — Python"
        elif block >= LONG_BLOCK:
            label = "Kata — LONG rep"
        else:
            label = "Kata — sprint"
        blocks.append((label, block, f"make drill KATA={kata} VARIANT={variant}"))
    kata_mins = sum(b[1] for b in blocks)
    main = WEEKDAY_TOTAL - kata_mins - FIXED_TAIL
    blocks += [("Main block", main, main_for(week, day)),
               ("Deck", 12, f"make review  ({DECK[week]})"),
               ("Log and commit", 8, "make done, log the session, git commit")]
    return blocks


def variants_in(kata):
    vf = os.path.join(ROOT, "practice", "katas", kata, "VARIANTS.md")
    have = []
    if os.path.exists(vf):
        with open(vf) as fh:
            for line in fh:
                m = re.match(r"^(v\d+)\s+", line.strip())
                if m:
                    have.append(m.group(1))
    return have


def check():
    """Prove the schedule is internally consistent. Returns a list of problems."""
    problems = []
    uses = first_use()
    week_of = first_use_week()
    plan = build_plan()
    built_at = {k: w for w, (_, ks) in plan.items() for k in ks}

    # 1. Nothing is drilled before it exists. Deriving the plan makes this true by
    # construction for ordinary katas, so what this really guards is the exempt path
    # and any kata that falls through both.
    for kata, use_week in sorted(week_of.items()):
        if kata in EXEMPT:
            build_week, build_day, _ = EXEMPT[kata]
            built = (build_week, DAYS.index(build_day))
            if built >= uses[kata]:
                w, d = uses[kata]
                problems.append(
                    f"{kata}: exempt and built by week {build_week} {build_day}, but "
                    f"first drilled week {w} {DAYS[d]} — the exemption does not hold"
                )
            continue
        if kata not in built_at:
            problems.append(f"{kata}: drilled from week {use_week} but never built")
        elif built_at[kata] >= use_week:
            problems.append(
                f"{kata}: built in week {built_at[kata]} but first drilled in week "
                f"{use_week} — it must exist the week before"
            )

    # 2. Nothing is built that is never drilled.
    for kata in sorted(built_at):
        if kata not in week_of:
            problems.append(f"{kata}: has a build slot but never appears in the rotation")

    # 3. Every kata directory on disk is accounted for, and vice versa.
    katas_dir = os.path.join(ROOT, "practice", "katas")
    on_disk = {d for d in os.listdir(katas_dir)
               if os.path.isdir(os.path.join(katas_dir, d))} if os.path.isdir(katas_dir) else set()
    for kata in sorted(on_disk - set(week_of)):
        problems.append(f"{kata}: exists on disk but is never scheduled")
    for kata in sorted(set(week_of) - on_disk):
        problems.append(f"{kata}: scheduled but there is no practice/katas/{kata}/")

    # 4. Every variant the rotation names exists in that kata's VARIANTS.md.
    for week, i, kata, variant, _ in all_slots():
        if variant not in variants_in(kata):
            problems.append(
                f"week {week} {DAYS[i]}: {kata} {variant} is not in "
                f"practice/katas/{kata}/VARIANTS.md"
            )

    # 5. An exemption must name a kata that is actually scheduled, or it is stale.
    for kata in sorted(EXEMPT):
        if kata not in week_of:
            problems.append(f"{kata}: listed in EXEMPT but never scheduled — stale exemption")

    # 6. No Sunday is so long it will not actually happen. Measured across the whole
    # day, because the build block is not the only thing on it.
    for build_week in sorted(plan):
        if build_week == 0:
            continue          # the Day 0 weekend is not a calendar day
        total = sum(b[1] for b in timers("Sun", build_week))
        if total > SUNDAY_MAX_MIN:
            problems.append(
                f"week {build_week} Sunday: {total} min ({total / 60:.1f} hr) including the "
                f"build session, over the {SUNDAY_MAX_MIN}-minute cap. Move a kata's first "
                f"use later, or add a session to SESSIONS."
            )

    # 7. The timer block must be at least as long as the target you are trying to
    # beat. Otherwise the calendar asks for a rep the timer rule forbids finishing,
    # and the retirement bar becomes unreachable without breaking the rules.
    for week, i, kata, _, block in all_slots():
        target = TARGETS.get(kata)
        if target is not None and target >= block:
            problems.append(
                f"week {week} {DAYS[i]}: {kata} has a {target}-minute target in a "
                f"{block}-minute block. The block has to be strictly longer, or the timer "
                f"rings exactly at target and no over-target rep can ever be logged. "
                f"Move it to a long day, or change its target."
            )
    for kata, target in sorted(TARGETS.items()):
        # A Python kata only ever appears in the Python block, so its ceiling is that
        # block and not the longest C one.
        ceiling = PY_BLOCK if kata.endswith("_py") else LONG_BLOCK
        if target >= ceiling:
            problems.append(
                f"{kata}: target {target} min exceeds the longest block it can be given "
                f"({ceiling} min), so no day in the calendar can hold it"
            )

    # 8. Any kata that owns a capability's evidence bar must be schedulable to
    # retirement: three reps, ending in three distinct variants. Katas whose
    # capabilities are scored some other way are exempt from this and are listed as
    # informational only.
    owning = _katas_that_own_a_bar()
    slots = all_slots()
    for kata in sorted(owning):
        seq = [v for _, _, k, v, _ in slots if k == kata]
        if len(seq) < 3:
            problems.append(
                f"{kata}: owns the evidence bar for {', '.join(owning[kata])} but has "
                f"{len(seq)} slot(s) in the rotation. Retirement needs three."
            )
        elif len(set(seq[-3:])) != 3:
            problems.append(
                f"{kata}: its last three slots are {', '.join(seq[-3:])} — retirement "
                f"needs three DIFFERENT variants"
            )

    # 9. The B group must be reachable, for the same reason check #8 exists for katas.
    # A story is ready at three takes rated strong on three DIFFERENT days, so N stories
    # need at least 3N takes across at least 3 days. This check is the one that was
    # missing when B11 was added: the arithmetic had closed at ten stories, nobody
    # recounted, and the calendar silently stopped being able to finish the group.
    stories = _story_ids()
    if stories:
        # Counted off the rendered calendar, not off rehearsal_takes() alone. The weeks 9
        # and 10 main blocks schedule takes too, and counting only the timer blocks made
        # the check believe the calendar was thinner than it is — 35 takes when it
        # actually asks for 44.
        takes, days = rehearsal_schedule()
        need = 3 * len(stories)
        if takes < need:
            problems.append(
                f"rehearsal: {len(stories)} stories need {need} takes rated STRONG to "
                f"reach three each, but the calendar schedules {takes} takes in total. "
                f"Add takes in rehearsal_takes(), or the B group cannot be finished."
            )
        if days < 3:
            problems.append(
                f"rehearsal: only {days} day(s) carry a take; a story needs three "
                f"different days."
            )

    # 10. A mechanism a capability is SCORED on has to appear in the calendar often enough
    # to reach its bar. Checks #8 and #9 are this same guard for katas and for rehearsal;
    # this is the version for the two rubric-scored mechanisms, and it is the one that was
    # missing. E30's bar is three architecture drills and `make design` appeared ZERO times
    # in seventy days — the capability was unreachable by anyone following the plan, every
    # other check passed, and nothing said a word.
    #
    # Only the rubric mechanisms are counted. The deck has no per-session unit to count
    # against a bar expressed in Leitner boxes; katas are #8; rehearsal is #9, where the
    # count would also have to understand "make rehearse S=B3, then S=B4, then S=B10",
    # which the counter below reads as one session.
    sessions = mechanism_sessions()
    for cmd, (need, cids) in sorted(_rubric_mechanism_needs().items()):
        have = sessions.get(cmd, 0)
        if have < need:
            problems.append(
                f"`make {cmd}`: the calendar schedules it {have} time(s), but it is the "
                f"evidence bar for {', '.join(cids)}, which needs {need}. Add slots in "
                f"timers(), or that capability cannot be met by following the plan."
            )

    return problems


def mechanism_sessions():
    """{make-command: how many times the whole plan asks you to run it}.

    One block can ask for several — `make prompt x3` is three sessions, not one — so this
    reads the multiplier rather than counting lines. It deliberately does not try to parse
    a block that lists several invocations in prose; check #10 only consults it for the
    two mechanisms whose blocks use the `xN` form.
    """
    counts = {}
    for week in range(1, WEEKS + 1):
        for day in DAYS:
            for _, _, what in timers(day, week):
                for cmd, mult in re.findall(r"make ([a-z-]+)(?:\s+x(\d+))?", what):
                    counts[cmd] = counts.get(cmd, 0) + (int(mult) if mult else 1)
    return counts


def rehearsal_schedule():
    """(takes, days carrying at least one) across the whole rendered plan."""
    takes = days = 0
    for week in range(1, WEEKS + 1):
        for day in DAYS:
            n = 0
            for _, _, what in timers(day, week):
                for _, mult in re.findall(r"make (rehearse)(?:\s+x(\d+))?", what):
                    n += int(mult) if mult else 1
            takes += n
            days += 1 if n else 0
    return takes, days


# What share of takes you should expect to rate STRONG. The B-group bar is three strong
# takes on three different days per story, and check #9 can only count takes scheduled —
# so this is the factor between the two. It is a planning assumption, not a measurement,
# which is why falling below it is a note rather than a failure.
STRONG_RATE = 0.75


def rep_shortfall():
    """{kata: (scheduled, owed)} for anything the rotation cannot give its full budget.

    The weekday shape fixes the supply at len(DAY_SLOTS-days) * WEEKS slots. reps_wanted()
    is the demand. When demand exceeds supply the greedy placer silently drops the tail,
    and until this existed nothing compared the two: check #8 only asks for three slots and
    three distinct trailing variants, which a kata twelve reps short still passes.

    Deliberately an advisory rather than a problem. Saturday is fourteen unassigned reps
    over the plan and the adaptive picker spends them worst-first, so a small shortfall is
    what that slack is for. A large one means the day shape can no longer fund the bar, and
    the number below is how you tell the two apart.
    """
    got = {}
    for _, _, kata, _, _ in all_slots():
        got[kata] = got.get(kata, 0) + 1
    return {k: (got.get(k, 0), n) for k, n in sorted(reps_wanted().items())
            if got.get(k, 0) < n}


def advisories():
    """Things worth knowing that are not build failures. Printed by `make check-calendar`.

    Check #9 proves the calendar schedules at least 3N takes for N stories. That is the
    arithmetic floor and it assumes every single take is rated strong, which no one
    manages. This says how much real slack there is.
    """
    notes = []
    short = rep_shortfall()
    if short:
        total = sum(n - g for g, n in short.values())
        notes.append(
            "rep budget: " + ", ".join(f"{k} {g}/{n}" for k, (g, n) in short.items())
            + f". The weekday shape supplies {len(all_slots())} slots and reps_wanted() "
            f"asks for {sum(reps_wanted().values())}, so {total} rep(s) fall off the end. "
            f"Saturday's {WEEKS} adaptive reps are the designed slack and the picker spends "
            f"them worst-first, so a shortfall this size closes itself. If it grows, either "
            f"lower a rep budget or add a slot to DAY_SLOTS — do not ignore it."
        )
    stories = _story_ids()
    if stories:
        takes, _ = rehearsal_schedule()
        need = 3 * len(stories)
        comfortable = need / STRONG_RATE
        if takes < comfortable:
            notes.append(
                f"rehearsal: {takes} takes scheduled for {len(stories)} stories. The bar "
                f"is {need} rated STRONG, so this only closes if {need / takes:.0%} of "
                f"takes are strong. Budget for ~{comfortable:.0f} — the shortfall comes "
                f"out of free practice, which `make rehearse` allows any day."
            )
    return notes


def _rubric_mechanism_needs():
    """{make-command: (sessions needed, [capability ids])} for the rubric-scored bars.

    Read out of progress.py — the thresholds and the bar assignment both live there, and a
    second copy here is exactly the kind of drift the rest of this file exists to prevent.
    """
    try:
        mod = _progress_module()
        need = {"design prompts": ("prompt", mod.PROMPTS_FOR_T1),
                "architecture drills": ("design", mod.DESIGNS_FOR_E30)}
        out = {}
        for cid, rec in sorted(mod.ownership().items()):
            bar = mod.bar_for(cid, rec["owners"])
            if bar in need:
                cmd, n = need[bar]
                out.setdefault(cmd, [n, []])[1].append(cid)
        return out
    except Exception as exc:                                  # pragma: no cover
        print(f"note: could not read bars from progress.py ({exc})", file=sys.stderr)
        return {}


def _story_ids():
    """The B-group story ids, read from STORIES.md via rehearse.py.

    Same principle as _katas_that_own_a_bar(): ask the tool that owns the definition
    rather than keeping a second count here that can drift.
    """
    try:
        spec = importlib.util.spec_from_file_location(
            "_rehearse", os.path.join(ROOT, "tools", "rehearse.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return [s[0] for s in mod.load()]
    except Exception as exc:                                  # pragma: no cover
        print(f"note: could not read stories from rehearse.py ({exc})", file=sys.stderr)
        return []


def _progress_module():
    """progress.py, loaded. It owns which mechanism is a capability's bar, and both
    check #8 and check #10 ask it rather than keeping a second opinion."""
    spec = importlib.util.spec_from_file_location(
        "_progress", os.path.join(ROOT, "tools", "progress.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _katas_that_own_a_bar():
    """{kata: [capability ids]} for katas that a capability is actually scored on.

    Read out of progress.py rather than restated here, so this check follows the
    scoring rules instead of a second opinion about them.
    """
    try:
        mod = _progress_module()
        own = mod.ownership()
        out = {}
        for cid, rec in sorted(own.items()):
            if mod.bar_for(cid, rec["owners"]) != "kata":
                continue
            for k in rec["katas"]:
                out.setdefault(k, []).append(cid)
        return out
    except Exception as exc:                                  # pragma: no cover
        print(f"note: could not read ownership from progress.py ({exc})", file=sys.stderr)
        return {}


def report_check():
    uses = first_use_week()
    plan = build_plan()
    print("build plan, derived from the rotation:\n")
    for week, _, label in SESSIONS:
        if week not in plan:
            continue
        mins, katas = plan[week]
        print(f"  {label}  ({mins} min)")
        for k in katas:
            note = f"  [{BUILD_NOTE[k]}]" if k in BUILD_NOTE else ""
            print(f"      {k:<18} first drilled week {uses[k]}{note}")
    for kata, (build_week, build_day, why) in sorted(EXEMPT.items()):
        print(f"\n  EXEMPT: {kata} — built by week {build_week} {build_day}, "
              f"first drilled week {uses.get(kata, '?')}")
        for line in textwrap.wrap(why, 72):
            print(f"      {line}")

    problems = check()
    print()
    for n in advisories():
        print(f"note: {n}")
    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("schedule and build plan agree.")
    return 0


def main_for(week, day):
    if day in ("Sat", "Sun"):
        return WEEKEND[week]
    if week <= MIMIC_WEEKS:
        return f"Mimic: {MIMIC[week]}"
    return MAIN_LATE[week][day]


def render(start=None):
    L = []
    a = L.append
    a("# Calendar")
    a("")
    a(f"{WEEKS * 7} days. Every day has fixed katas, a fixed main block, and timer durations.")
    a("Set a timer for each block. When it rings, move on even if you aren't finished —")
    a("running over on the main block is how the kata and deck slots get eaten.")
    a("")
    a("**Generated by `make calendar` from `tools/schedule.py`. Do not edit this file.**")
    a("")
    a(f"**Sprint days (Mon, Tue, Thu, Fri):** {SPRINT_BLOCK}-minute kata. Short modules only.")
    a(f"**Long-rep days (Wed, Sun):** {LONG_BLOCK}-minute kata. The modules that need real time.")
    a(f"**Saturday:** a {LONG_BLOCK}-minute adaptive rep, then the main block. Still no deck.")
    a("**Sunday:** one long rep, the weekly review, a full deck pass — then whatever the")
    # Both halves derived. The build-session weeks used to be the literal string "1–3" sitting
    # next to a derived DESIGN_WEEKS, and it went stale the moment SESSIONS grew to five.
    a("week owes: a kata build session in weeks "
      + ", ".join(str(w) for w in sorted(w for w in build_plan() if w))
      + ", an architecture drill in weeks "
      + ", ".join(str(w) for w in DESIGN_WEEKS) + ".")
    a("")
    a("Every block is at least as long as the kata's target time in `tools/drill.py`, and")
    a("`make check-calendar` fails if that ever stops being true. A target you cannot reach")
    a("inside the block is a target the timer rule forbids you from hitting.")
    a("")
    a("Saturday is the one day with no assigned module. `make drill` with no arguments")
    a("picks by worst recent time, then longest since last rep, then never attempted —")
    a("so Saturday is the day that catches whatever you have been avoiding. It is also")
    a("the slack in the rotation: every kata's spare reps live here.")
    a("")
    plan = build_plan()
    load = {w: sum(sum(b[1] for b in timers(d, w)) for d in DAYS) for w in range(1, WEEKS + 1)}
    # Derived, not asserted. This used to name one "steady state" week and describe every
    # week from there on as identical, which stopped being true the moment the weeks
    # carrying an architecture drill were a different length from the ones that aren't.
    # Taking the most common load as the baseline and listing the exceptions keeps the
    # sentence true whatever gets added next.
    build_weeks = sorted(w for w in plan if w)
    rest = [w for w in range(1, WEEKS + 1) if w not in build_weeks]
    lo, hi = min(load[w] for w in rest), max(load[w] for w in rest)
    a(f"Weekly load: {lo / 60:.1f} to {hi / 60:.1f} hours once the build sessions are done.")
    a("Weeks " + ", ".join(str(w) for w in build_weeks) + " carry them and run "
      + ", ".join(f"{load[w] / 60:.1f}" for w in build_weeks) + " hours — heavy once,")
    a("instead of a little heavy for five. Weeks "
      + ", ".join(str(w) for w in DESIGN_WEEKS) + " carry a "
      + f"{DESIGN_BLOCK}-minute architecture drill.")
    a(f"About {sum(load.values()) / 60:.0f} hours over the {WEEKS * 7} days.")
    a("")
    a("---")
    a("")

    # The build plan, derived. This is the only place it is written down.
    uses = first_use_week()
    a("## Build plan")
    a("")
    a("**Generated from the rotation — do not edit this by hand, and do not copy it")
    a("anywhere else.** A kata has to exist before the first day that calls for it, so the")
    a("build order is a consequence of the schedule rather than a second list to keep in")
    a("sync. Change when a kata first appears and its build session moves with it.")
    a("`python3 tools/schedule.py --check` proves the two agree; CI runs it on every push.")
    a("")
    a("Several sessions, not one a week. A weekly build slot is a running dependency: miss")
    a("one Sunday and the next week's rotation has nothing to draw from. After the last")
    a("session there is nothing left to build.")
    a("")
    a("| Built during | Modules | First drilled | Time |")
    a("|---|---|---|---|")
    for build_week, _, label in SESSIONS:
        if build_week not in plan:
            continue
        mins, katas = plan[build_week]
        mods = ", ".join(f"`{k}`" for k in katas)
        span = sorted(uses[k] for k in katas)
        when = f"week {span[0]}" if span[0] == span[-1] else f"weeks {span[0]}–{span[-1]}"
        a(f"| {label} | {mods} | {when} | {mins // 60} hr {mins % 60 or ''}".rstrip()
          + (" min |" if mins % 60 else " |"))
    a("")
    for kata, (build_week, build_day, why) in sorted(EXEMPT.items()):
        a(f"**`{kata}` is not in the table above, deliberately.** {why}")
        a("")
        a(f"So it is built by week {build_week} {build_day} and first drilled in week "
          f"{uses.get(kata, '?')} — inside the same week, rather than the week before like "
          f"everything else. That is the one place the usual rule does not apply. It is "
          f"checked separately rather than waived, and at day resolution rather than week "
          f"resolution: `--check` fails if the kata is ever scheduled on or before "
          f"week {build_week} {build_day}.")
        a("")
    a("---")
    a("")

    for week in range(1, WEEKS + 1):
        a(f"## Week {week} — {PHASE[week]}")
        a("")
        if week <= MIMIC_WEEKS:
            a(f"**Mimic this week:** {MIMIC[week]}")
        a(f"**Deck focus:** {DECK[week]}")
        a("")
        if week == GATE_WEEK:
            # Derived, not typed. This said "25+" while plan/CURRICULUM.md said "60+", and the
            # rotation actually delivers 96 scheduled reps by here — so both numbers were
            # relics that would only fire after the kata slot had already been gutted.
            due = sum(1 for w, _, _, _, _ in all_slots() if w <= GATE_WEEK)
            a("> **GATE WEEK.** Stage 0 exit tagged `v0.0-stage0-exit`, clean-first-compile")
            a(f"> above 55%, and {int(due * GATE_REP_SHARE)}+ logged kata reps — the calendar")
            a(f"> schedules {due} by the end of this week. If that one is failing, the kata slot")
            a("> has been getting eaten, which is the exact failure mode this plan exists to stop.")
            a("")
        for i, day in enumerate(DAYS):
            n = (week - 1) * 7 + i + 1
            if start:
                d = start + timedelta(days=n - 1)
                label = f"**{d.strftime('%a %d %b')}**  ·  day {n}"
            else:
                label = f"**Day {n} · {day}**"
            blocks = timers(day, week)
            total = sum(b[1] for b in blocks)
            a(f"### {label}  ({total} min)")
            a("")
            a("| Timer | Block | What |")
            a("|---|---|---|")
            for name, mins, what in blocks:
                a(f"| **{mins} min** | {name} | {what} |")
            a("")
        a("---")
        a("")

    a("## Rules for the timer")
    a("")
    a("0. **Call `make lap` at each transition** — when you start typing, when you first compile,")
    a("   and when it compiles clean. Four seconds, and it turns a total into a diagnosis.")
    a("1. **Start the kata timer before you read anything.** `make drill` starts its own clock;")
    a("   the block timer is separate and it is the one that stops you.")
    a("2. **When the kata timer rings, stop.** Log the rep as unfinished. An unfinished rep is")
    a("   data. A rep that ate the main block is a lost day.")
    a("3. **The deck block is not optional and not negotiable.** Twelve minutes, out loud.")
    a("4. **Overran the main block?** Take it out of tomorrow's main block, never out of the")
    a("   kata or deck.")
    a("5. **Missed a day?** Skip it, don't stack it. Two 90-minute days back to back produces")
    a("   one good session and one bad one.")
    return "\n".join(L)


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(report_check())

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    start = None
    if args:
        start = datetime.strptime(args[0], "%Y-%m-%d").date()
    elif os.path.exists(START_FILE):
        with open(START_FILE) as fh:
            start = datetime.strptime(fh.read().strip(), "%Y-%m-%d").date()
    if start and start.weekday() != 0:
        print(f"note: {start} is a {DAYS[start.weekday()]}. Starting on a Monday is cleaner.\n",
              file=sys.stderr)

    # Two different facts, two different files, and they must not be mixed.
    #
    # The seventy-day SHAPE is a repo fact: committed, identical for anyone who
    # clones this, and rendered with relative labels (Day 1 · Mon). The Monday you
    # personally started is not a repo fact — logs/.start_date is gitignored on
    # purpose. Stamping your dates into the committed file made `make
    # check-generated` fail on every machine with a different start date, CI
    # included, since CI has none. So --write always renders relative, and the
    # dated view is a separate gitignored file you can open or paste into a real
    # calendar.
    if "--write" in sys.argv:
        with open(OUT, "w") as fh:
            fh.write(render(None) + "\n")
        print(f"Wrote {OUT} — relative day labels, because this file is committed.")
        if start:
            print("Real dates:  make dates")
    elif "--dates" in sys.argv:
        if not start:
            sys.exit("No start date, so there are no dates to stamp. Either:\n"
                     "  date +%F > logs/.start_date          the Monday you're starting\n"
                     "  python3 tools/schedule.py --dates 2026-08-17")
        with open(OUT_DATED, "w") as fh:
            fh.write(render(start) + "\n")
        print(f"Wrote {OUT_DATED} — gitignored. Yours, not the repo's.")
    else:
        print(render(start))
