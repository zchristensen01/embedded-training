#!/usr/bin/env python3
"""today.py — print today's assignment.

Everything here comes from tools/schedule.py: the day shape, the main block, the Mimic
sessions, the deck focus and the build plan. This file used to parse plan/CURRICULUM.md
for the main-block text while the calendar rendered it from schedule.py, and the two
drifted — `make today` and plan/CALENDAR.md disagreed about week 9. One generator.

The start date is day 1 — the Monday you intend to start, which may be in the future:
    echo 2026-08-24 > logs/.start_date

The seven days before it are the prep week, and this prints one of those instead: the
module due that day, its checks, and the day's deck count. It rolls over to week 1 on
day 1 by itself.
"""
import importlib.util
import os
import sys
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = os.path.join(ROOT, "logs", ".start_date")
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _schedule():
    spec = importlib.util.spec_from_file_location(
        "_schedule", os.path.join(ROOT, "tools", "schedule.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SCHED = _schedule()


def rule(ch="="):
    print("  " + ch * 66)


def prep(start, elapsed):
    """The days before day 1. `elapsed` is negative.

    This used to be a single `Plan starts <date>.` line for however long you had left.
    That was fine when the build was a weekend you read out of a document, and wrong now
    that it is a week with a module a day: a prep week nothing prints is a prep week that
    drifts away from the rotation it is derived from, which is the failure this repo's
    generators exist to prevent. Same source as every other day, so it cannot.
    """
    offset = elapsed + SCHED.PREP_DAYS         # 0-based day within the prep week
    if offset < 0:
        print(f"\n  Plan starts {start}, in {-elapsed} days.")
        print(f"  The prep week starts {start - timedelta(days=SCHED.PREP_DAYS)} "
              f"— see PREP_WEEK.md.\n")
        return

    kata, mins = SCHED.prep_day(offset)
    today = DAYS[date.today().weekday()]

    print("\n" + "=" * 70)
    print(f"  PREP WEEK  ·  {today}, day {offset + 1} of {SCHED.PREP_DAYS}"
          f"  ·  day 1 is {start}")
    print("=" * 70)

    rule("-")
    if kata:
        print(f"  Build        {kata}")
        print(f"  Why today    the calendar first drills it on "
              f"{_first_drilled(kata)}")
    else:
        print("  Build        nothing — buffer day")
    print(f"  Deck         {SCHED.PREP_DECK} cards"
          if kata else "  Deck         a full pass — tomorrow it is a timed block")
    print("  The rest     Mimic reading, and the concepts behind the cards you missed")
    rule("-")

    if kata:
        py = kata.endswith("_py")
        print(f"\n  {mins} min on {kata}:")
        print(f"    1. Read the whole BRIEF. practice/katas/{kata}/BRIEF.md")
        if py:
            print(f"    2. make newkata NAME={kata}")
            print("    3. Write the API into the BRIEF — a *_py kata has no header.")
        else:
            print(f"    2. make newkata NAME={kata}")
            print(f"    3. Write the contract: practice/katas/{kata}/include/{kata}.h")
        print("    4. List the cases in the BRIEF in your own words, then write them")
        print(f"       in practice/katas/{kata}/tests/. Every case is yours.")
        print("\n  Then, and this is the part that gets skipped:")
        if py:
            print(f"    make test MODULE={kata}      pytest collects the suite")
        else:
            print("    make check-frozen            the header parses, the suite compiles")
        print(f"    make drill KATA={kata}")
        print("        it REFUSES a placeholder suite. If it refuses, you are not done.")
        print("        If it starts a rep, Ctrl-C — you are not drilling this week.")
        print("    git commit                   the suite is frozen for fourteen weeks")
    else:
        print("\n  Buffer day. If a build slipped, today is where it goes. Otherwise:")
        print("    make check                   all seven, clean")
        print("    make list                    every module scaffolded?")
        print("    read DAILY.md start to finish — from tomorrow it is a reference you")
        print("      glance at, and today is the last day it is worth reading cold")

    # The buffer day takes the full default pass rather than the prep week's ten. It is the
    # eve of day 1 and the deck goes to a timed block tomorrow, so this is the dress
    # rehearsal for it. No count typed here on purpose — `make review` bare is whatever
    # review.py's default is, and that is the number a weekday will hand you.
    print(f"\n  make review N={SCHED.PREP_DECK}" if kata else "\n  make review")
    print("    Out loud, with the trap. A card you cannot answer is reading to do, not a")
    print("    card to fail — go and learn it, then write what you learned as a new card.")

    print("\n  Nothing to log. A build is not a rep, so logs/log.tsv stays untouched")
    print("  until day 1. The two exceptions: a row in logs/ai-use.tsv for any AI you")
    print("  used, and the commit.\n")


def _first_drilled(kata):
    w, d = SCHED.first_use().get(kata, (None, None))
    return f"week {w} {DAYS[d]}" if w is not None else "a later week"


def main():
    if not os.path.exists(START):
        sys.exit("No start date. It is the Monday you intend to start, which may be in\n"
                 "the future — the seven days before it are the prep week. Run:\n"
                 "  echo 2026-08-24 > logs/.start_date")

    with open(START) as fh:
        start = datetime.strptime(fh.read().strip(), "%Y-%m-%d").date()

    elapsed = (date.today() - start).days
    if elapsed < 0:
        prep(start, elapsed)
        return

    week = elapsed // 7 + 1
    today = DAYS[date.today().weekday()]

    if week > SCHED.WEEKS:
        print(f"\n  {SCHED.WEEKS} weeks done. Run `make report` and reread the week 10 checks.\n")
        return

    print("\n" + "=" * 70)
    print(f"  WEEK {week}  ·  {today}, day {elapsed + 1} of {SCHED.WEEKS * 7}  ·  {SCHED.PHASE[week]}")
    print("=" * 70)

    if start.weekday() != 0:
        print(f"  note: you started on a {DAYS[start.weekday()]}, so the week boundary and")
        print(f"        the weekday shape are out of step. Starting on a Monday is cleaner.")

    rule("-")
    if week <= SCHED.MIMIC_WEEKS:
        print(f"  Mimic        {SCHED.MIMIC[week]}")
    print(f"  Main block   {SCHED.main_for(week, today)}")
    print(f"  Deck focus   {SCHED.DECK[week]}")
    rule("-")

    blocks = SCHED.timers(today, week)
    print(f"\n  {sum(b[1] for b in blocks)} min today:")
    for name, mins, what in blocks:
        print(f"    {mins:>4} min  {name:<18} {what}")

    if today == "Sat":
        print("\n  Saturday's rep has no assigned module on purpose. `make drill` with no")
        print("  arguments picks your worst recent time, then the longest since you last")
        print("  touched it. It is the day that catches what you have been avoiding, and")
        print("  it is where every kata's spare reps live.")

    plan = SCHED.build_plan()
    if today == "Sun" and week in plan:
        mins, katas = plan[week]
        print(f"\n  !! BUILD SESSION today ({mins} min): {', '.join(katas)}")
        print("  !! The header and the test suite. You write every case — that is the point.")
        print("  !! See the Build plan section at the top of plan/CALENDAR.md.")

    if week == SCHED.GATE_WEEK:
        print(f"\n  !! WEEK {SCHED.GATE_WEEK} GATE: Stage 0 exit tagged, 55%+ clean rate, 25+ reps.")
        print("  !! If the clean rate is short, the kata slot has been getting eaten.")

    # The clock starts at the keyboard, so the reading is a real step and it comes first.
    # Printing `make drill` alone here was what taught the old habit of drilling and then
    # reading, which is now backwards.
    print("\n  Next:")
    print("    1. Set a timer for the first block.")
    print("    2. Read that kata's VARIANTS.md line and the API in its BRIEF.md.")
    print("       This is off the clock — the clock starts when you start typing.")
    print("    3. `make drill KATA=... VARIANT=...` exactly as printed above.\n")


if __name__ == "__main__":
    main()
