# Setup

**Do not build all fifteen katas before you start.** Build the ones week 1 needs, start on day 1,
and take the rest in three sessions across the first three weeks.

Fifteen katas, each needing a real test suite — and for the C ones a compiling header too —
is around fifteen hours.
Spent up front that is two weeks of building the gym before lifting anything, which is the most
common way a plan like this dies. Spread one-per-week instead and you get the opposite problem: a
running dependency where one missed Sunday leaves the next week with nothing to drill. A batch
now, three more batches, then never again.

---

## Day 0 — about twenty minutes

The repo is set up and the tooling works. What is left is picking a start date:

```bash
date +%F > logs/.start_date        # use the Monday you're starting
make dates                         # plan/CALENDAR.dated.md — 98 days, real dates
make today                         # should now print week 1
```

Two calendars, on purpose. `plan/CALENDAR.md` is committed and carries relative labels
(`Day 1 · Mon`); the start date is gitignored, so stamping it into a committed file would
mean `make check-generated` failing on every machine but yours. `make dates` writes the
dated view to a gitignored file beside it. `make calendar` regenerates the committed one
and you only need it after editing `tools/schedule.py`.

One dependency, needed **from day 0**, because the Python katas are drilled from week 1:

```bash
python3 -m pip install pytest      # or: sudo apt install python3-pytest
```

Then check the machine is ready. This should pass on a clean tree, and it is the same set CI
runs:

```bash
make check                         # all seven checks
```

---

## Day 0 weekend

Build the katas week 1 calls for. **Which ones is not written down here on purpose** — it is
derived from the rotation and printed by the command below, along with how long the session
should take:

```bash
make check-calendar     # prints the whole build plan, then verifies it
```

Scaffold each one with `make newkata NAME=<module>`, then, in this order:

1. **Write the contract, deliberately** — you live with it for weeks.
   - **C module:** `practice/katas/<name>/include/<name>.h`.
   - **Python module** (`<name>_py`): there is no header and no `include/`. The contract is the
     API written out in `BRIEF.md`, and the frozen suite is what enforces it. The day-0 build
     includes two of these, so this is not a footnote.
2. **List the cases** in `BRIEF.md` under "What to test," before writing any of them.
3. **Write the cases** in `tests/`. Yourself.
4. **Check it took.** `make drill KATA=<name>` refuses a module whose suite is still the
   scaffolded placeholder, so if it refuses, step 3 is not finished.

About an hour each; `ring_buffer`, `protocol_parser` and `concurrency_sim` are budgeted at
ninety minutes, and the printed plan says so per session.

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
tests, and for the C ones the header as well. Read the BRIEF's "What to test" section — it lists the
cases, in prose. Turning that list into actual test cases is your job and nobody else's; it is
the single most-interviewed skill in both tracks.

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
KATA=bitops VARIANT=v1` actually does, and what you owe the log at each end of a session.

Then `make today`. Then `make drill`. Then the main block on Mimic S0.

Do not spend another evening on the repo. The plan is finished; the only thing left that matters
is the first rep, and it should happen this week.
