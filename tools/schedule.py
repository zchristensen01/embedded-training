#!/usr/bin/env python3
"""schedule.py — generate CALENDAR.md, all 70 days, with timers and kata assignments.

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
SPRINT_BLOCK = 15     # Mon, Tue, Thu, Fri — katas with a target of 12 min or less
LONG_BLOCK = 28       # Wed, Sun, and Saturday's adaptive rep — everything else
PY_BLOCK = 25         # the Python rep, every weekday, alongside the C one

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
SAT_TAKES_LATE = 2      # weeks 8-10: the run-up to the interview-simulation week
SAT_LATE_FROM = 8


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


WEEKDAY_TOTAL = 115
FIXED_TAIL = 20       # Deck (12) + Log and commit (8)

MIMIC = {
    1: "S0 bench, toolchain, repo · S1 motor forensics and bolting it down",
    2: "S2 power topology and first soldering · S3 encoder, interrupts, x4 decoding",
    3: "S4 open loop, both directions · S5 the fixed-rate loop, rate proven",
    4: "S6 units, convert at the boundary · S7 telemetry and the bandwidth budget",
    5: "S8 P only, stability boundary · S9 step-response metrics · S10 D then I",
    6: "S11 safety envelope and real PWM · S12 the refactor, tests, exit gate",
}

WEEKEND = {
    1: "S0/S1 overflow. Get the motor bolted down before anything else.",
    2: "S2 power. Draw the topology before you wire it. Solder. Then fill in "
       "practice/rehearsal/STORIES.md — the rehearsal slots start next week.",
    3: "S3/S4 overflow. First logic-analyzer capture goes in docs/.",
    4: "SWAP: Mimic M4.1 — EMG features on public datasets. Python, no hardware.",
    5: "S8/S9 tuning runs. Save every plot, including the bad ones.",
    6: "S12 tests + exit gate evidence. Tag v0.0-stage0-exit.",
    7: "Device abstraction over a fake transport. Same tests pass on both.",
    8: "Dockerise the harness. GitHub Actions, self-hosted runner.",
    9: "Harness repo published. README states what it verifies and what it cannot.",
    10: "make report. Compare the week 1 and week 10 curves. Write the retro.",
}

MAIN_LATE = {
    7: {"Mon": "pytest from zero: discovery, assertions, exit codes. 20 tests on a pure function",
        "Tue": "Fixtures, scope, teardown that survives a failing test. conftest.py",
        "Wed": "parametrize. Then verification vs validation, test plan structure",
        "Thu": "Traceability, IEC 62304 classes, one test case per requirement",
        "Fri": "make prompt x3. Score each against the rubric"},
    8: {"Mon": "pyserial: open, write, read with timeout, frame responses. Talk to the board",
        "Tue": "Fixture that opens/closes the port and resets the device between tests",
        "Wed": "Flashing from the harness. Test isolation",
        "Thu": "Fault injection: truncated frames, bad CRC, impossible lengths. Assert recovery",
        "Fri": "Trace each test to a Stage 0 requirement. Requirement IDs in test names"},
    9: {"Mon": "Green CI run against real hardware. Screenshot it",
        "Tue": "README: what it verifies, what it cannot catch, how tests trace to requirements",
        "Wed": "make prompt x4. Then the full protocol and hardware verbal set",
        "Thu": "make rehearse x4. Sourced from Mimic's NOTES and the tuning history",
        "Fri": "make rehearse S=B3, then S=B4, then S=B10. Record one. Watch it back"},
    10: {"Mon": "Timed 2-hour mock take-home, AI-free: state machine, debugging, bit masking",
         "Tue": "Debrief the take-home out loud as if defending it. Record. Watch it back",
         "Wed": "Full deck pass. Every card box 4+ or it goes back to daily",
         "Thu": "make rehearse S=B10 twice, timed. Then --stats: every story ready?",
         "Fri": "Mock verbal round: 20 cards cold, out loud, no reveal. Then make prompt x2"},
}

DECK = {
    1: "types, pointers, strings", 2: "interrupts, memory", 3: "volatile, static, const",
    4: "registers, alignment", 5: "protocols, timing", 6: "sync, RTOS",
    7: "V&V, traceability, test design", 8: "test infra, pytest", 9: "hardware, debug",
    10: "full deck, no filter",
}

# Deterministic rotation. Sprint katas on Mon/Tue/Thu/Fri, long katas on Wed/Sun.
#
# Two constraints shape this and both are checked:
#   1. A sprint day's block is SPRINT_BLOCK, so only katas with a target that fits may
#      appear there. Same for long days.
#   2. Retirement needs three CONSECUTIVE clean reps at target across three different
#      variants, so any kata that owns a capability's evidence bar needs at least three
#      slots ending in three distinct variants. `--check` proves it.
#
# `protocol_parser` is the one long kata with two slots rather than three. That is
# deliberate: E21 is its only capability and E21's bar is the deck, not the kata, so
# nothing is blocked by not being able to retire it. Saturday's adaptive rep is where
# the slack for every kata lives.
KATA = {
 1: {"Mon":("bitops","v1"),"Tue":("mem_primitives","v1"),"Wed":("ring_buffer","v1"),
     "Thu":("bitops","v2"),"Fri":("mem_primitives","v2"),"Sun":("fsm","v1")},
 2: {"Mon":("mem_primitives","v3"),"Tue":("bitops","v3"),"Wed":("ring_buffer","v2"),
     "Thu":("register_map","v1"),"Fri":("mem_primitives","v4"),"Sun":("protocol_parser","v1")},
 3: {"Mon":("register_map","v2"),"Tue":("bitops","v4"),"Wed":("fsm","v2"),
     "Thu":("register_map","v3"),"Fri":("mem_primitives","v5"),"Sun":("pool_allocator","v1")},
 4: {"Mon":("register_map","v4"),"Tue":("debouncer","v1"),"Wed":("protocol_parser","v2"),
     "Thu":("register_map","v5"),"Fri":("bitops","v5"),"Sun":("ring_buffer","v3")},
 5: {"Mon":("debouncer","v2"),"Tue":("register_map","v6"),"Wed":("fixed_point_pid","v1"),
     "Thu":("rollover_timer","v1"),"Fri":("bitops","v6"),"Sun":("pool_allocator","v2")},
 6: {"Mon":("register_map","v7"),"Tue":("debouncer","v3"),"Wed":("pool_allocator","v3"),
     "Thu":("rollover_timer","v2"),"Fri":("mem_primitives","v6"),"Sun":("concurrency_sim","v1")},
 7: {"Mon":("bitops","v7"),"Tue":("register_map","v1"),"Wed":("fixed_point_pid","v2"),
     "Thu":("mem_primitives","v7"),"Fri":("debouncer","v4"),"Sun":("test_harness_py","v1")},
 8: {"Mon":("register_map","v3"),"Tue":("bitops","v3"),"Wed":("test_harness_py","v2"),
     "Thu":("rollover_timer","v3"),"Fri":("debouncer","v5"),"Sun":("fixed_point_pid","v3")},
 9: {"Mon":("bitops","v5"),"Tue":("mem_primitives","v5"),"Wed":("fsm","v3"),
     "Thu":("rollover_timer","v4"),"Fri":("debouncer","v6"),"Sun":("concurrency_sim","v2")},
10: {"Mon":("mem_primitives","v6"),"Tue":("register_map","v4"),"Wed":("test_harness_py","v3"),
     "Thu":("rollover_timer","v5"),"Fri":("bitops","v6"),"Sun":("concurrency_sim","v3")},
}

# The Python rotation, running alongside KATA on weekdays from week 1.
#
# Two modules own an evidence bar and therefore need three slots ending in three distinct
# variants, exactly like the C katas: binary_frame_py (Y2) and log_parser_py (Y3).
# cli_tool_py owns no bar — it reinforces T17 and T20, whose bars sit on the HIL project —
# so it gets fewer slots, the same way protocol_parser does on the C side.
#
# Three days a week, not five. Python runs Mon/Wed/Fri; Tuesday and Thursday are left clear
# at 90 minutes. That is what keeps this a second rep rather than a second full rotation.
KATA_PY = {
 1: {"Mon":("binary_frame_py","v1"),"Wed":("log_parser_py","v1"),"Fri":("binary_frame_py","v2")},
 2: {"Mon":("log_parser_py","v2"),"Wed":("binary_frame_py","v3"),"Fri":("log_parser_py","v3")},
 3: {"Mon":("binary_frame_py","v4"),"Wed":("log_parser_py","v4"),"Fri":("binary_frame_py","v5")},
 4: {"Mon":("log_parser_py","v5"),"Wed":("binary_frame_py","v6"),"Fri":("log_parser_py","v6")},
 5: {"Mon":("binary_frame_py","v7"),"Wed":("log_parser_py","v7"),"Fri":("binary_frame_py","v1")},
 6: {"Mon":("log_parser_py","v1"),"Wed":("cli_tool_py","v1"),"Fri":("binary_frame_py","v2")},
 7: {"Mon":("log_parser_py","v2"),"Wed":("cli_tool_py","v2"),"Fri":("binary_frame_py","v3")},
 8: {"Mon":("log_parser_py","v3"),"Wed":("cli_tool_py","v3"),"Fri":("binary_frame_py","v4")},
 9: {"Mon":("log_parser_py","v4"),"Wed":("cli_tool_py","v4"),"Fri":("binary_frame_py","v5")},
10: {"Mon":("log_parser_py","v5"),"Wed":("cli_tool_py","v5"),"Fri":("binary_frame_py","v6")},
}

PHASE = {**{w: "MIMIC STAGE 0" for w in range(1, 7)},
         7: "TEST ENGINEERING", 8: "THE HARNESS", 9: "FINISH AND WRITE UP",
         10: "INTERVIEW SIMULATION"}

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
# the Day 0 weekend, before the calendar starts. Several sessions rather than one a
# week on purpose: a weekly build slot is a running dependency, and one missed Sunday
# leaves the next week's rotation with nothing to draw from. Three sessions after day
# zero, front-loaded and finite, keeps the heaviest Sunday under the cap below.
SESSIONS = [
    (0, 1, "Day 0 weekend"),
    (1, 3, "Week 1 Sunday"),
    (2, 5, "Week 2 Sunday"),
    (3, 99, "Week 3 Sunday"),
]

# Roughly what it costs to write one API contract plus a real test suite. The suite
# is the expensive half and it is the point — it is rep zero of "how would you test
# this." Anything you can write in twenty minutes is too shallow to rep against.
BUILD_MIN = {"ring_buffer": 90, "concurrency_sim": 90, "protocol_parser": 90}
BUILD_MIN_DEFAULT = 60

# Katas that are NOT built in a build session. {kata: (week, weekday, why)} — the
# point in the calendar by which the build is finished. Exempt from the build-session
# plan, but NOT from the check: the kata's first rep must fall strictly after that
# day. Week granularity would not be enough here; week 7's main block runs Mon-Fri
# and the kata does not exist until Friday closes.
EXEMPT = {
    "test_harness_py": (7, "Fri",
        "It is built by week 7's main block rather than by a build session. Week 7 is "
        "five consecutive days of pytest from zero — discovery, assertions, fixtures, "
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
    """[(week, day_index, kata, variant, block)] across BOTH rotations, in order.

    KATA and KATA_PY both key on weekday and a weekday holds one of each, so they cannot
    be merged into a single day-keyed dict — the Python rep would overwrite the C one.
    Every check that used to walk KATA walks this instead, or it silently stops seeing
    half the schedule the moment a Python kata is the thing that is wrong.
    """
    out = []
    for week in sorted(set(KATA) | set(KATA_PY)):
        for i, day in enumerate(DAYS):
            if day in KATA.get(week, {}):
                k, v = KATA[week][day]
                out.append((week, i, k, v, block_for(day)))
            if day in KATA_PY.get(week, {}):
                k, v = KATA_PY[week][day]
                out.append((week, i, k, v, PY_BLOCK))
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
    parts = [f"{k} ({BUILD_NOTE[k]})" if k in BUILD_NOTE else k for k in katas]
    return (f"BUILD x{len(katas)}: " + ", ".join(parts)
            + ". Write the header first, then list the cases in the BRIEF, then write "
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
        k, v = KATA[week]["Sun"]
        blocks = [("Kata — LONG rep", LONG_BLOCK, f"make drill KATA={k} VARIANT={v}"),
                  ("Weekly review", 20, "make report, then fill logs/WEEKLY_REVIEW.md"),
                  ("Deck — full pass", 15, "make review 30")]
        if week in plan:
            mins, katas = plan[week]
            blocks.append(("Kata build", mins, build_text(katas)))
        else:
            # T1 — "how would you test X" — is the highest-frequency T&I question and
            # one of the four listed reasons candidates get rejected.
            blocks.append(("Design prompt", 10, "make prompt  (T1 — ask for requirements first)"))
        # Rehearsal runs on EVERY Sunday from REHEARSAL_FROM, build week or not. It used
        # to sit in the non-build branch only, which is part of how the B group quietly
        # became unreachable: the research says T&I candidates fail the behavioural round
        # more often than the technical one, so this is the wrong block to sacrifice to a
        # heavy Sunday. Check #9 proves the totals still close.
        n = rehearsal_takes("Sun", week)
        if n:
            blocks.append(("Rehearsal", 10 * n, rehearse_text(n)))
        return blocks
    k, v = KATA[week][day]
    kblock = LONG_BLOCK if day in LONG_DAYS else SPRINT_BLOCK
    label = "Kata — LONG rep" if day in LONG_DAYS else "Kata — sprint"
    blocks = [(label, kblock, f"make drill KATA={k} VARIANT={v}")]
    # The Python rep sits next to the C one, every weekday, from week 1. Not a separate
    # track and not a later phase: the two languages are interleaved deliberately, because
    # an interview loop does not block by language and identifying which problem you are
    # looking at before solving it is part of the skill.
    if day in KATA_PY.get(week, {}):
        pk, pv = KATA_PY[week][day]
        blocks.append(("Kata — Python", PY_BLOCK, f"make drill KATA={pk} VARIANT={pv}"))
    # The main block is the remainder either way, so a day without a Python rep is simply
    # 25 minutes shorter rather than handing that time to Mimic.
    main = WEEKDAY_TOTAL - kblock - PY_BLOCK - FIXED_TAIL
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
        if target is not None and target > block:
            problems.append(
                f"week {week} {DAYS[i]}: {kata} has a {target}-minute target in a "
                f"{block}-minute block. Move it to a long day, or change its target."
            )
    for kata, target in sorted(TARGETS.items()):
        # A Python kata only ever appears in the Python block, so its ceiling is that
        # block and not the longest C one.
        ceiling = PY_BLOCK if kata.endswith("_py") else LONG_BLOCK
        if target > ceiling:
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
        takes = sum(rehearsal_takes(d, w) for w in range(1, 11) for d in DAYS)
        days = sum(1 for w in range(1, 11) for d in DAYS if rehearsal_takes(d, w))
        need = 3 * len(stories)
        if takes < need:
            problems.append(
                f"rehearsal: {len(stories)} stories need {need} takes to reach three "
                f"strong takes each, but the calendar schedules {takes}. Add takes in "
                f"rehearsal_takes(), or the B group cannot be finished."
            )
        if days < 3:
            problems.append(
                f"rehearsal: only {days} day(s) carry a take; a story needs three "
                f"different days."
            )

    return problems


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


def _katas_that_own_a_bar():
    """{kata: [capability ids]} for katas that a capability is actually scored on.

    Read out of progress.py rather than restated here, so this check follows the
    scoring rules instead of a second opinion about them.
    """
    try:
        spec = importlib.util.spec_from_file_location(
            "_progress", os.path.join(ROOT, "tools", "progress.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
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
    if week <= 6:
        return f"Mimic: {MIMIC[week]}"
    return MAIN_LATE[week][day]


def render(start=None):
    L = []
    a = L.append
    a("# Calendar")
    a("")
    a("Seventy days. Every day has a fixed kata, a fixed main block, and timer durations.")
    a("Set a timer for each block. When it rings, move on even if you aren't finished —")
    a("running over on the main block is how the kata and deck slots get eaten.")
    a("")
    a("**Generated by `make calendar` from `tools/schedule.py`. Do not edit this file.**")
    a("")
    a(f"**Sprint days (Mon, Tue, Thu, Fri):** {SPRINT_BLOCK}-minute kata. Short modules only.")
    a(f"**Long-rep days (Wed, Sun):** {LONG_BLOCK}-minute kata. The modules that need real time.")
    a(f"**Saturday:** a {LONG_BLOCK}-minute adaptive rep, then the main block. Still no deck.")
    a("**Sunday:** the light day — one long rep, the weekly review, a full deck pass.")
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
    load = {w: sum(sum(b[1] for b in timers(d, w)) for d in DAYS) for w in range(1, 11)}
    steady = min(w for w in range(1, 11) if w not in plan)
    heavy = sorted(w for w in range(1, 11) if w in plan)
    a(f"Weekly load: about {load[steady] / 60:.1f} hours, every week from week {steady} on.")
    a("Weeks " + ", ".join(str(w) for w in heavy) + " carry the build sessions on top of "
      "that — " + ", ".join(f"{load[w] / 60:.1f}" for w in heavy) + " hours. They are the")
    a("heavy weeks of the ten, and they are heavy once instead of a little heavy for five.")
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

    for week in range(1, 11):
        a(f"## Week {week} — {PHASE[week]}")
        a("")
        if week <= 6:
            a(f"**Mimic this week:** {MIMIC[week]}")
        a(f"**Deck focus:** {DECK[week]}")
        a("")
        if week == 6:
            a("> **GATE WEEK.** Stage 0 exit tagged `v0.0-stage0-exit`, clean-first-compile")
            a("> above 55%, 25+ logged reps. If the second one is failing, the kata slot has")
            a("> been getting eaten — that is the exact failure mode this plan exists to stop.")
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
