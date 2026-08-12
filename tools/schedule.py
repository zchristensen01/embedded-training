#!/usr/bin/env python3
"""schedule.py — generate CALENDAR.md, all 70 days, with timers and kata assignments.

  python3 tools/schedule.py                 relative day labels (Day 1, Day 2, ...)
  python3 tools/schedule.py 2026-08-17      real dates, starting that Monday
  python3 tools/schedule.py --write         write to CALENDAR.md instead of stdout

Start on a Monday. If logs/.start_date exists it is used automatically.
"""
import os
import re
import sys
import textwrap
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "plan", "CALENDAR.md")
START_FILE = os.path.join(ROOT, "logs", ".start_date")

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Wed and Sun are LONG rep days (25 min). Mon/Tue/Thu/Fri are SPRINT (10 min).
LONG_DAYS = {"Wed", "Sun"}

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
    2: "S2 power. Draw the topology before you wire it. Solder.",
    3: "S3/S4 overflow. First logic-analyzer capture goes in docs/.",
    4: "SWAP: Mimic M4.1 — EMG features on public datasets. Python, no hardware.",
    5: "S8/S9 tuning runs. Save every plot, including the bad ones.",
    6: "S12 tests + exit gate evidence. Tag v0.0-stage0-exit.",
    7: "Device abstraction over a fake transport. Same tests pass on both.",
    8: "Dockerise the harness. GitHub Actions, self-hosted runner.",
    9: "Publish. Harness repo public. Site updated with the Stage 0 sequence.",
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
        "Thu": "Fill rehearsal/STORIES.md from Mimic's NOTES. Then make rehearse x4",
        "Fri": "make rehearse B3, B4, B10. Record one. Watch it back"},
    10: {"Mon": "Timed 2-hour mock take-home, AI-free: state machine, debugging, bit masking",
         "Tue": "Debrief the take-home out loud as if defending it. Record. Watch it back",
         "Wed": "Full deck pass. Every card box 4+ or it goes back to daily",
         "Thu": "make rehearse B10 twice, timed. Then --stats: every story ready?",
         "Fri": "Second application wave — embedded and firmware roles"},
}

DECK = {
    1: "types, pointers, strings", 2: "interrupts, memory", 3: "volatile, static, const",
    4: "registers, alignment", 5: "protocols, timing", 6: "sync, RTOS",
    7: "V&V, traceability, test design", 8: "test infra, pytest", 9: "hardware, debug",
    10: "full deck, no filter",
}

# Deterministic rotation. Sprint katas on Mon/Tue/Thu/Fri, long katas on Wed/Sun.
KATA = {
 1: {"Mon":("bitops","v1"),"Tue":("mem_primitives","v1"),"Wed":("ring_buffer","v1"),
     "Thu":("bitops","v2"),"Fri":("mem_primitives","v2"),"Sun":("fsm","v1")},
 2: {"Mon":("mem_primitives","v3"),"Tue":("bitops","v3"),"Wed":("ring_buffer","v2"),
     "Thu":("register_map","v1"),"Fri":("mem_primitives","v4"),"Sun":("protocol_parser","v1")},
 3: {"Mon":("register_map","v2"),"Tue":("bitops","v4"),"Wed":("ring_buffer","v3"),
     "Thu":("register_map","v3"),"Fri":("mem_primitives","v5"),"Sun":("pool_allocator","v1")},
 4: {"Mon":("register_map","v4"),"Tue":("debouncer","v1"),"Wed":("protocol_parser","v2"),
     "Thu":("register_map","v5"),"Fri":("bitops","v5"),"Sun":("fsm","v2")},
 5: {"Mon":("debouncer","v2"),"Tue":("register_map","v6"),"Wed":("fixed_point_pid","v1"),
     "Thu":("rollover_timer","v1"),"Fri":("bitops","v6"),"Sun":("ring_buffer","v4")},
 6: {"Mon":("register_map","v7"),"Tue":("debouncer","v3"),"Wed":("pool_allocator","v2"),
     "Thu":("rollover_timer","v2"),"Fri":("mem_primitives","v7"),"Sun":("concurrency_sim","v1")},
 7: {"Mon":("bitops","v1"),"Tue":("register_map","v1"),"Wed":("concurrency_sim","v2"),
     "Thu":("mem_primitives","v1"),"Fri":("debouncer","v4"),"Sun":("test_harness_py","v1")},
 8: {"Mon":("register_map","v3"),"Tue":("bitops","v3"),"Wed":("test_harness_py","v2"),
     "Thu":("rollover_timer","v3"),"Fri":("debouncer","v5"),"Sun":("ring_buffer","v6")},
 9: {"Mon":("bitops","v5"),"Tue":("mem_primitives","v5"),"Wed":("fsm","v3"),
     "Thu":("register_map","v5"),"Fri":("debouncer","v6"),"Sun":("protocol_parser","v3")},
10: {"Mon":("ring_buffer","v3"),"Tue":("register_map","v4"),"Wed":("test_harness_py","v3"),
     "Thu":("rollover_timer","v4"),"Fri":("mem_primitives","v6"),"Sun":("concurrency_sim","v4")},
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
# the Day 0 weekend, before the calendar starts. Two sessions rather than one a week
# on purpose: a weekly build slot is a running dependency, and one missed Sunday
# leaves the next week's rotation with nothing to draw from.
SESSIONS = [
    (0, 1, "Day 0 weekend"),
    (1, 4, "Week 1 Sunday"),
    (2, 99, "Week 2 Sunday"),
]

# Roughly what it costs to write one API contract plus a real test suite. The suite
# is the expensive half and it is the point — it is rep zero of "how would you test
# this." Anything you can write in twenty minutes is too shallow to rep against.
BUILD_MIN = {"ring_buffer": 90, "concurrency_sim": 90, "protocol_parser": 90}
BUILD_MIN_DEFAULT = 60

# Katas that are NOT built in a build session. {kata: (week that builds it, why)}.
# Exempt from the build-session plan, but NOT from the check: the week named here
# still has to land no later than the week the kata is first drilled.
EXEMPT = {
    "test_harness_py": (7,
        "It is built by week 7's main block rather than by a build session. Week 7 is "
        "five consecutive days of pytest from zero — discovery, assertions, fixtures, "
        "conftest.py, parametrize — and this kata is the artifact those five days "
        "produce. Giving it its own build slot would mean writing the same suite "
        "twice. This is a deliberate exception, not an oversight: it is the one "
        "module whose build IS the main work."),
}

# A build session longer than this is not a session, it's a lost weekend. The check
# warns rather than fails — you may genuinely want one heavy weekend.
SESSION_MAX_MIN = 300

# Notes appended to a kata in the build listing, where the build differs.
BUILD_NOTE = {
    "concurrency_sim": "builds under -fsanitize=thread, not address",
    "test_harness_py": "pytest, not compiled",
}


def first_use():
    """Week each kata is first drilled, derived from KATA. {kata: week}."""
    seen = {}
    for week in sorted(KATA):
        for day in DAYS:
            if day not in KATA[week]:
                continue
            k, _ = KATA[week][day]
            seen.setdefault(k, week)
    return seen


def build_plan():
    """{build_week: (minutes, [katas])}, derived from first_use() and SESSIONS."""
    plan = {w: [] for w, _, _ in SESSIONS}
    for kata, week in sorted(first_use().items(), key=lambda kv: (kv[1], kv[0])):
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
    if day == "Sat":
        # No fixed kata here on purpose. The adaptive picker takes worst-recent-time
        # first, then longest-since-last-rep, then never-attempted — so Saturday is
        # the day that catches whatever you have been quietly avoiding.
        return [("Kata — sprint", 10, "make drill   (no argument — picks your weakest module)"),
                ("Main block", 120, main_for(week, day))]
    if day == "Sun":
        k, v = KATA[week]["Sun"]
        blocks = [("Kata — LONG rep", 25, f"make drill KATA={k} VARIANT={v}"),
                  ("Weekly review", 20, "make report, then fill logs/WEEKLY_REVIEW.md"),
                  ("Deck — full pass", 15, "make review 30")]
        plan = build_plan()
        if week in plan:
            # Weeks 1-2 are already the two heavy Sundays; don't stack more on them.
            mins, katas = plan[week]
            blocks.append(("Kata build", mins, build_text(katas)))
        else:
            # T1 and the B group were the two thinnest-covered things in the plan.
            # T1 — "how would you test X" — is the highest-frequency T&I question and
            # one of the four listed reasons candidates get rejected, and it had two
            # slots in seventy days. The B group is where the research says T&I
            # candidates fail MORE often than on the technical round, and ten stories
            # at three takes each is thirty takes against about ten scheduled.
            # A weekly slot for each from week 3 costs 20 minutes and fixes both.
            blocks.append(("Design prompt", 10, "make prompt  (T1 — ask for requirements first)"))
            blocks.append(("Rehearsal", 10, "make rehearse  (one story, out loud, timed)"))
        return blocks
    k, v = KATA[week][day]
    if day in LONG_DAYS:
        return [("Kata — LONG rep", 25, f"make drill KATA={k} VARIANT={v}"),
                ("Main block", 45, main_for(week, day)),
                ("Deck", 12, f"make review  ({DECK[week]})"),
                ("Log and commit", 8, "make done, log the session, git commit")]
    return [("Kata — sprint", 10, f"make drill KATA={k} VARIANT={v}"),
            ("Main block", 60, main_for(week, day)),
            ("Deck", 12, f"make review  ({DECK[week]})"),
            ("Log and commit", 8, "make done, log the session, git commit")]


def check():
    """Prove the schedule and the build plan agree. Returns a list of problems."""
    problems = []
    uses = first_use()
    plan = build_plan()
    built_at = {k: w for w, (_, ks) in plan.items() for k in ks}

    # 1. Nothing is drilled before it exists. Deriving the plan makes this true by
    # construction for ordinary katas, so what this really guards is the exempt path
    # and any kata that falls through both.
    for kata, use_week in sorted(uses.items()):
        if kata in EXEMPT:
            build_week, _ = EXEMPT[kata]
            if build_week > use_week:
                problems.append(
                    f"{kata}: exempt and built in week {build_week}, but first drilled "
                    f"in week {use_week} — the exemption does not hold"
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
        if kata not in uses:
            problems.append(f"{kata}: has a build slot but never appears in the rotation")

    # 3. Every kata directory on disk is accounted for, and vice versa.
    katas_dir = os.path.join(ROOT, "practice", "katas")
    on_disk = {d for d in os.listdir(katas_dir)
               if os.path.isdir(os.path.join(katas_dir, d))} if os.path.isdir(katas_dir) else set()
    for kata in sorted(on_disk - set(uses)):
        problems.append(f"{kata}: exists on disk but is never scheduled")
    for kata in sorted(set(uses) - on_disk):
        problems.append(f"{kata}: scheduled but there is no practice/katas/{kata}/")

    # 4. Every variant the rotation names exists in that kata's VARIANTS.md.
    for week in sorted(KATA):
        for day, (kata, variant) in KATA[week].items():
            vf = os.path.join(katas_dir, kata, "VARIANTS.md")
            have = set()
            if os.path.exists(vf):
                with open(vf) as fh:
                    for line in fh:
                        m = re.match(r"^(v\d+)\s+", line.strip())
                        if m:
                            have.add(m.group(1))
            if variant not in have:
                problems.append(
                    f"week {week} {day}: {kata} {variant} is not in "
                    f"practice/katas/{kata}/VARIANTS.md"
                )

    # 5. An exemption must name a kata that is actually scheduled, or it is stale.
    for kata in sorted(EXEMPT):
        if kata not in uses:
            problems.append(f"{kata}: listed in EXEMPT but never scheduled — stale exemption")

    # 6. No session is so long it will not actually happen.
    for build_week, (mins, katas) in sorted(plan.items()):
        if mins > SESSION_MAX_MIN:
            label = next(l for w, _, l in SESSIONS if w == build_week)
            problems.append(
                f"{label}: {mins} min ({mins / 60:.1f} hr) across {len(katas)} modules, "
                f"over the {SESSION_MAX_MIN}-minute cap. Move a kata's first use later, "
                f"or add a session to SESSIONS."
            )

    return problems


def report_check():
    uses = first_use()
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
    for kata, (build_week, why) in sorted(EXEMPT.items()):
        print(f"\n  EXEMPT: {kata} — built week {build_week}, "
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
    a("**Sprint days (Mon, Tue, Thu, Fri):** 10-minute kata. Short modules only.")
    a("**Long-rep days (Wed, Sun):** 25-minute kata. The modules that need real time.")
    a("**Saturday:** a 10-minute adaptive rep, then the 2-hour main block. Still no deck.")
    a("**Sunday:** the lightest day — one long rep, the weekly review, a full deck pass.")
    a("")
    a("Saturday is the one day with no assigned module. `make drill` with no arguments")
    a("picks by worst recent time, then longest since last rep, then never attempted —")
    a("so Saturday is the day that catches whatever you have been avoiding.")
    a("")
    load = {w: sum(sum(b[1] for b in timers(d, w)) for d in DAYS) for w in range(1, 11)}
    a(f"Weekly load: about {load[3] / 60:.1f} hours, every week from week 3 on. Weeks 1 and 2")
    a(f"carry the build sessions on top of that — {load[1] / 60:.1f} and {load[2] / 60:.1f} "
      f"hours. They are the two heavy")
    a("weeks of the ten, and they are heavy once instead of a little heavy for five.")
    a("")
    a("---")
    a("")

    # The build plan, derived. This is the only place it is written down.
    uses = first_use()
    plan = build_plan()
    a("## Build plan")
    a("")
    a("**Generated from the rotation — do not edit this by hand, and do not copy it")
    a("anywhere else.** A kata has to exist before the first day that calls for it, so the")
    a("build order is a consequence of the schedule rather than a second list to keep in")
    a("sync. Change when a kata first appears and its build session moves with it.")
    a("`python3 tools/schedule.py --check` proves the two agree; CI runs it on every push.")
    a("")
    a("Two sessions, not one a week. A weekly build slot is a running dependency: miss one")
    a("Sunday and the next week's rotation has nothing to draw from. After week 2 there is")
    a("nothing left to build.")
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
    for kata, (build_week, why) in sorted(EXEMPT.items()):
        a(f"**`{kata}` is not in the table above, deliberately.** {why}")
        a("")
        a(f"So it is built in week {build_week} and first drilled in week "
          f"{uses.get(kata, '?')} — inside the same week, rather than the week before like "
          f"everything else. That is the one place the usual rule does not apply. It is "
          f"checked separately rather than waived, so if week {build_week}'s main block "
          f"ever moves later than its first rep, `--check` will say so.")
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
            a("> above 55%, 25+ logged reps. **Applications go out Sunday.**")
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
    args = [a for a in sys.argv[1:] if a != "--write"]
    start = None
    if args:
        start = datetime.strptime(args[0], "%Y-%m-%d").date()
    elif os.path.exists(START_FILE):
        with open(START_FILE) as fh:
            start = datetime.strptime(fh.read().strip(), "%Y-%m-%d").date()
    if start and start.weekday() != 0:
        print(f"note: {start} is a {DAYS[start.weekday()]}. Starting on a Monday is cleaner.\n",
              file=sys.stderr)
    text = render(start)
    if "--write" in sys.argv:
        with open(OUT, "w") as fh:
            fh.write(text + "\n")
        print(f"Wrote {OUT}")
    else:
        print(text)
