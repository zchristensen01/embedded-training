#!/usr/bin/env python3
"""today.py — print today's assignment.

Everything here comes from tools/schedule.py: the day shape, the main block, the Mimic
sessions, the deck focus and the build plan. This file used to parse plan/CURRICULUM.md
for the main-block text while the calendar rendered it from schedule.py, and the two
drifted — `make today` and plan/CALENDAR.md disagreed about week 9. One generator.

Create the start date on day 1:
    date +%F > logs/.start_date
"""
import importlib.util
import os
import sys
from datetime import date, datetime

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


def main():
    if not os.path.exists(START):
        sys.exit("No start date. Run:  date +%F > logs/.start_date")

    with open(START) as fh:
        start = datetime.strptime(fh.read().strip(), "%Y-%m-%d").date()

    elapsed = (date.today() - start).days
    if elapsed < 0:
        sys.exit(f"Plan starts {start}.")

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
