#!/usr/bin/env python3
"""today.py — print today's assignment from CURRICULUM.md.

Weeks 1-6 come from the Stage 0 week table (one row per week).
Weeks 7-10 come from the per-day tables under each "### Week N" heading.

Create the start date on day 1:
    date +%F > logs/.start_date
"""
import importlib.util, os, re, sys
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUR = os.path.join(ROOT, "plan", "CURRICULUM.md")
START = os.path.join(ROOT, "logs", ".start_date")
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _schedule():
    """The day shapes come from schedule.py, not from a second copy in here.

    This file used to hardcode "90 min: 10 kata / 60 main / 12 deck / 8 log", which
    is the same information timers() already holds. Two copies drift the first time
    a block changes length — so read the one that generates the calendar.
    """
    spec = importlib.util.spec_from_file_location(
        "_schedule", os.path.join(ROOT, "tools", "schedule.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SCHED = _schedule()


def print_blocks(day, week):
    blocks = SCHED.timers(day, week)
    total = sum(b[1] for b in blocks)
    print(f"\n  {total} min today:")
    for name, mins, what in blocks:
        print(f"    {mins:>4} min  {name:<18} {what}")

if not os.path.exists(START):
    sys.exit("No start date. Run:  date +%F > logs/.start_date")

with open(START) as fh:
    start = datetime.strptime(fh.read().strip(), "%Y-%m-%d").date()

elapsed = (date.today() - start).days
if elapsed < 0:
    sys.exit(f"Plan starts {start}.")

week = elapsed // 7 + 1
today = DAYS[date.today().weekday()]
text = open(CUR).read()

def rule(ch="="):
    print("  " + ch * 66)

if week > 10:
    print("\n  Ten weeks done. Run `make report` and reread the week 10 checks.\n")
    sys.exit()

print("\n" + "=" * 70)
print(f"  WEEK {week}  ·  {today}, day {elapsed + 1} of 70")
print("=" * 70)

if week <= 6:
    print("  PHASE: Mimic Stage 0.  Main block is the workbook.")
    row = re.search(rf"^\|\s*{week}\s*\|(.+?)\|(.+?)\|(.+?)\|\s*$", text, re.M)
    if row:
        sessions, katas, deck = (g.strip() for g in row.groups())
        rule("-")
        print(f"  Mimic        {sessions}")
        print(f"  Kata pool    {katas}")
        print(f"  Deck focus   {deck}")
        rule("-")
    print_blocks(today, week)
    if today == "Sat":
        print("\n  Saturday's rep has no assigned module on purpose. `make drill` with no")
        print("  arguments picks your worst recent time, then the longest since you last")
        print("  touched it. It is the day that catches what you have been avoiding.")
    if today in ("Sat", "Sun") and week >= 4:
        print("\n  Consider swapping one weekend to Mimic M4.1 (EMG datasets, Python, no hardware).")
    if week == 6:
        print("\n  !! WEEK 6 GATE: Stage 0 exit tagged, 55%+ clean rate, 25+ reps.")
        print("  !! Applications go out at the end of this week.")
else:
    print("  PHASE: this repo. Mimic is paused.")
    m = re.search(rf"^### Week {week} — (.+?)$(.*?)(?=^### |^---|\Z)", text, re.M | re.S)
    if not m:
        m = re.search(rf"^## Week {week} — (.+?)$(.*?)(?=^## |^---|\Z)", text, re.M | re.S)
    if m:
        print(f"  {m.group(1).strip()}")
        body = m.group(2)
        found = False
        for line in body.splitlines():
            if re.match(rf"^\|\s*{today}\s*\|", line):
                cells = [c.strip() for c in line.strip("|").split("|")]
                rule("-")
                print(f"  Main block   {cells[1]}")
                rule("-")
                found = True
                break
        if not found and today in ("Sat", "Sun"):
            for line in body.splitlines():
                if re.match(r"^\|\s*Weekend\s*\|", line):
                    cells = [c.strip() for c in line.strip("|").split("|")]
                    rule("-")
                    print(f"  Weekend      {cells[1]}")
                    rule("-")
                    break
    print_blocks(today, week)
    if today == "Sat":
        print("\n  Saturday's rep has no assigned module on purpose — `make drill` with no")
        print("  arguments picks whatever you have been avoiding.")

# The build sessions live in weeks 1 and 2 only; after that there is nothing to build.
_plan = SCHED.build_plan()
if today == "Sun" and week in _plan:
    mins, katas = _plan[week]
    print(f"\n  !! BUILD SESSION today ({mins} min): {', '.join(katas)}")
    print("  !! The header and the test suite. You write every case — that is the point.")
    print("  !! See the Build plan section at the top of plan/CALENDAR.md.")

print("\n  Next:  make drill\n")
