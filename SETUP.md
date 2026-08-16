# Setup

**Do not build all fifteen katas before you start.** Build the ones week 1 needs during the
prep week, start on day 1, and take the rest in five Sunday sessions across the first five
weeks.

Fifteen katas, each needing a real test suite — and for the C ones a compiling header too —
is around fifteen hours.
Spent up front that is two weeks of building the gym before lifting anything, which is the most
common way a plan like this dies. Spread one-per-week instead and you get the opposite problem: a
running dependency where one missed Sunday leaves the next week with nothing to drill. A batch
first, five more batches, then never again.

---

## Before day 1 — about twenty minutes

The repo is set up and the tooling works. What is left is picking a start date:

```bash
echo 2026-08-24 > logs/.start_date # the Monday you're starting, even if that is not today
make dates                         # plan/CALENDAR.dated.md — 98 days, real dates
make today                         # a prep day, then week 1 from day 1 on
```

Set that date to the Monday you intend to start, not to today. `make today` reads it and
knows where you are relative to it: the seven days before it are the prep week and it prints
the module due that day, and on day 1 it rolls over to the calendar on its own.

Two calendars, on purpose. `plan/CALENDAR.md` is committed and carries relative labels
(`Day 1 · Mon`); the start date is gitignored, so stamping it into a committed file would
mean `make check-generated` failing on every machine but yours. `make dates` writes the
dated view to a gitignored file beside it. `make calendar` regenerates the committed one
and you only need it after editing `tools/schedule.py`.

One dependency, needed **from the prep week**, because two of the six suites built there are
pytest ones and the Python katas are drilled from week 1:

```bash
python3 -m pip install pytest      # or: sudo apt install python3-pytest
```

**One thing to source early, because it has a lead time.** T24's evidence bar is an instrument
driver class in the harness repo, and criterion 8 of
[`projects/hil-harness/BRIEF.md`](projects/hil-harness/BRIEF.md) needs a *programmable* SCPI
instrument on the bench — a scope, a bench supply or a meter with a USB/LAN command interface.
It first bites in **week 11**, but that is not when you want to discover you do not have one.
Everything else in the plan runs on the machine you already have.

Then check the machine is ready. This should pass on a clean tree, and it is the same set CI
runs:

```bash
make check                         # all seven checks
```

---

## The prep week — the seven days before day 1

Build the katas week 1 calls for, **one a day**. Which ones, in which order, and on which day
is **not written down here on purpose** — it is derived from the rotation and printed by the
commands below:

```bash
make check-calendar     # prints the whole build plan, then verifies it
make today              # during the prep week: the one module due today, and its checks
```

One a day rather than one weekend, and that is a deliberate reversal. Six modules is six and
a half hours; as a weekend it is the largest single session in the plan sitting on the two
days of the week you have least control over, and it leaves no room for the reading that has
to come first — the deck is 162 unseen cards and a card about a semaphore is not a card the
Leitner schedule can help you with until you have read about semaphores. Spread across the
week it is about an hour a day, and the other hour is the reading.

The order is by the day the calendar first needs each module, so an interrupted prep week
costs you Wednesday rather than Monday. The last day carries no module: it is the buffer, and
the eve of day 1.

Scaffold each one with `make newkata NAME=<module>`, then, in this order:

1. **Write the contract, deliberately** — you live with it for weeks.
   - **C module:** `practice/katas/<name>/include/<name>.h`.
   - **Python module** (`<name>_py`): there is no header and no `include/`. The contract is the
     API written out in `BRIEF.md`, and the frozen suite is what enforces it. The prep week
     includes two of these, so this is not a footnote.
2. **List the cases** in `BRIEF.md` under "Tests it must pass," before writing any of them.
3. **Write the cases** in `tests/`. Yourself.
4. **Check it took.** `make drill KATA=<name>` refuses a module whose suite is still the
   scaffolded placeholder, so if it refuses, step 3 is not finished.

About an hour each; `ring_buffer`, `protocol_parser` and `concurrency_sim` are budgeted at
ninety minutes, and the printed plan says so per module.

**And then the checks, which are the half that gets skipped.** `make check-frozen` for a C
module or `make test MODULE=<name>` for a `*_py` one, then `make drill KATA=<name>` — which
must *start* a rep rather than refuse one — then `git commit`. There is nothing to write into
`logs/log.tsv`: a build is not a rep, and the first row in that file belongs to day 1. The
only log the prep week owes is `logs/ai-use.tsv`.

**Be honest about the size of this.** Six modules and around six and a half hours is the
largest block of building in the plan, and it is the only session not capped by
`make check-calendar`, because none of its days are calendar days. It is also the
highest-stakes work here: those suites are frozen for fourteen weeks, so a rushed suite is a
rushed fourteen weeks. That is the whole argument for taking a week over it.

> **This is not setup overhead.** Writing the API and the test suite before the implementation is
> the single most-interviewed skill in both tracks. You are doing rep zero of "how would you test
> this," which is a top-three question. Treat it as the work, not as preparation for the work.

**The AI rule applies here and it is the rule that matters most.** AI may write the test runner
and the assert macros — that plumbing is already in the generated file. AI may not write a single
test case. If it does, you have outsourced the exact thing you are selling.

---

## The rest of the builds — five Sunday sessions, weeks 1 to 5

**The build order is not written down here, on purpose.** It is derived from the calendar's
kata rotation and printed in the **Build plan** section at the top of
[plan/CALENDAR.md](plan/CALENDAR.md). A kata cannot be drilled before it exists, so the build
order is a *consequence* of the schedule, not a second list to keep in sync with it. Change when
a kata first appears and its build session moves with it.

```bash
make check-calendar     # proves the schedule and the build plan agree. CI runs it too.
```

That command prints the whole plan and then verifies it: nothing scheduled that is never built,
nothing built that is never scheduled, no variant named that does not exist, no Sunday so long
it will not realistically happen, no kata whose target time is longer than the block it is
scheduled into, and no kata that owns a capability's evidence bar without enough slots to reach
it.

One session a week for five weeks, and that is a running dependency — miss a Sunday and the
next week's rotation is short. It is the price of a Sunday that also carries two long reps:
bigger sessions put the day over its cap, and `make check-calendar` says so. Weeks 1 to 5 are
the heavy weeks of the fourteen, and after week 5 there is nothing left to build. The
generated calendar prints the real hours per week; don't trust a number typed into a
document, including this one.

**Every kata ships with a written `BRIEF.md` and `VARIANTS.md`.** For each one you owe the
tests, and for the C ones the header as well. Every BRIEF teaches the module from the ground
up — the problem in plain language, a diagram, the API line by line, and a set of paper
questions to answer before you type — and ends with a "Tests it must pass" table listing the
cases in prose, each with the bug it protects against. Turning that table into actual test
cases is your job and nobody else's; it is the single most-interviewed skill in both tracks.

Some katas do not follow the standard build:

- **`concurrency_sim`** compiles under ThreadSanitizer rather than ASan, because the two cannot
  coexist in one binary. `make test` handles the switch for you.
- **The three `*_py` katas** — `binary_frame_py`, `log_parser_py`, `cli_tool_py` — have no
  header. There is no `include/` directory and nothing to compile: the contract is the API
  written out in the BRIEF, and the frozen pytest suite is what enforces it. `make
  check-frozen` skips them; `make test MODULE=<name>` runs them under pytest.
- **`test_harness_py`** has no build session at all. Week 9's main block is the harness work,
  and this kata is the artifact those days produce — giving it a
  separate slot would mean writing the same suite twice. It is the one module whose build *is*
  the main work. `make check-calendar` still checks it, and at day resolution rather than week
  resolution: the exemption fails if the kata is ever scheduled on or before the Friday its
  build finishes.

If a build session slips, `make drill` with no arguments falls back to whatever katas are
actually built — it will not hand you a module whose header and tests do not exist yet. You lose
the calendar's rotation, not the day.

## One thing to write before week 3

`practice/rehearsal/STORIES.md` ships as a skeleton and **the stories have to be yours.** The
weekly rehearsal slots start on week 3's Saturday, so the file needs filling in before then —
week 2's weekend block says so. An unwritten story wanders, and the B group is where the
research says test-and-integration candidates fail most.

---

## Day 1

Read [DAILY.md](DAILY.md) once — it explains what a calendar line like `make drill
KATA=bitops VARIANT=v1` actually does, and what you owe the log at each end of a session. The
prep week's buffer day is the slot for it.

Then `make today`. Then `make drill`. Then the main block on Mimic S0.

Do not spend another evening on the repo. The plan is finished; the only thing left that matters
is the first rep, and it should happen on day 1.
