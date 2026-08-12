# Setup

**Do not build all twelve katas before you start.** Build four, start on day 1, and take the rest
in two sessions across the first two weeks.

Twelve katas, each needing a compiling header and a real test suite, is around twelve hours.
Spent up front that is two weeks of building the gym before lifting anything, which is the most
common way a plan like this dies. Spread one-per-week instead and you get the opposite problem: a
running dependency where one missed Sunday leaves the next week with nothing to drill. Four now,
then two batches, then never again.

---

## Day 0 — about twenty minutes

The repo is set up and the tooling works. What is left is picking a start date:

```bash
date +%F > logs/.start_date        # use the Monday you're starting
make calendar                      # stamps CALENDAR.md with real dates
make today                         # should now print week 1
```

One dependency, needed from week 6 when `test_harness_py` starts:

```bash
python3 -m pip install pytest      # or: sudo apt install python3-pytest
```

Then check the machine is ready. Both of these should pass on a clean tree:

```bash
make check-frozen                  # every frozen header and suite still compiles
make check-log                     # the practice log is well formed
```

---

## Day 0 weekend — about four hours

Scaffold and fill in the four katas week 1 calls for:

```bash
make newkata NAME=bitops
make newkata NAME=mem_primitives
make newkata NAME=ring_buffer
make newkata NAME=fsm
```

For each, in this order:

1. **Write `practice/katas/<name>/include/<name>.h`.** The contract. Deliberately — you live with it for weeks.
2. **List the cases** in `BRIEF.md` under "What to test," before writing any of them.
3. **Write the cases** in `tests/`. Yourself.

An hour each. `ring_buffer` will take longer; it's the most important one you own.

> **This is not setup overhead.** Writing the API and the test suite before the implementation is
> the single most-interviewed skill in both tracks. You are doing rep zero of "how would you test
> this," which is a top-three question. Treat it as the work, not as preparation for the work.

**The AI rule applies here and it is the rule that matters most.** AI may write the test runner
and the assert macros — that plumbing is already in the generated file. AI may not write a single
test case. If it does, you have outsourced the exact thing you are selling.

---

## The rest of the builds — two sessions, weeks 1 and 2

**The build order is not written down here, on purpose.** It is derived from the calendar's
kata rotation and printed in the **Build plan** section at the top of
[plan/CALENDAR.md](plan/CALENDAR.md). A kata cannot be drilled before it exists, so the build
order is a *consequence* of the schedule, not a second list to keep in sync with it. Change when
a kata first appears and its build session moves with it.

```bash
make check-calendar     # proves the schedule and the build plan agree. CI runs it too.
```

That command prints the whole plan and then verifies it: nothing scheduled that is never built,
nothing built that is never scheduled, no variant named that does not exist, and no session so
long it will not actually happen.

Two sessions rather than one a week. A weekly build slot is a running dependency — miss one
Sunday and the next week's rotation has nothing to draw from. Weeks 1 and 2 are the two heavy
weeks of the ten (about 15 and 14 hours against a normal 10.7), and after week 2 there is
nothing left to build.

**Every kata ships with a written `BRIEF.md` and `VARIANTS.md`.** For all twelve you owe exactly
two things: the header and the tests. Read the BRIEF's "What to test" section — it lists the
cases, in prose. Turning that list into actual test cases is your job and nobody else's; it is
the single most-interviewed skill in both tracks.

Two katas do not follow the standard build:

- **`concurrency_sim`** compiles under ThreadSanitizer rather than ASan, because the two cannot
  coexist in one binary. `make test` handles the switch for you.
- **`test_harness_py`** has no build session at all. Week 7's main block is five consecutive
  days of pytest from zero, and this kata is the artifact those days produce — giving it a
  separate slot would mean writing the same suite twice. It is the one module whose build *is*
  the main work. `make check-calendar` still checks it, so if week 7 ever moves later than the
  kata's first rep you will be told.

If a week's build slips, `make drill` with no arguments falls back to whatever katas exist. You
lose the calendar's rotation, not the day.

---

## Day 1

`make today`. Then `make drill`. Then the main block on Mimic S0.

Do not spend another evening on the repo. The plan is finished; the only thing left that matters
is the first rep, and it should happen this week.
