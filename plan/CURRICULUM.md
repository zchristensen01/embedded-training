# The plan

Fourteen weeks. Stage 0 finished at week 8, the HIL harness built in weeks 10–11, weeks
13–14 spent proving it under interview conditions.

This file explains **why** the fourteen weeks are shaped the way they are. It deliberately does
not restate what happens on each day — that is generated into
[`plan/CALENDAR.md`](CALENDAR.md) from `tools/schedule.py`, and a second copy here would
drift within a fortnight. It already did once. `make today` reads the same generator, so
the calendar and the daily prompt cannot disagree.

---

## Hours

**14.1 to 15.0 hours a week once the build sessions are done.** Five weekdays at 115
minutes, a Saturday of about two and a quarter hours, and a Sunday of about two hours and ten
minutes. Every weekday carries two reps: a C kata beside a Python one, except Tuesday, which
carries two short C reps. Sunday carries two long ones. Four Sundays — weeks 6, 8, 10 and 12
— run to nearly three hours, because they also carry the architecture drill that E30 is
scored on.

**That volume is not a preference, it is the bar.** Three consecutive clean reps at target
across three variants needs twelve to seventeen reps on a module. At the old ten-week volume
no C capability retired in more than half of simulated runs and six retired in none; at this
one they all land between 76% and 86%.

**Weeks 1–5 are heavier** — roughly 15 to 16.5 hours each — because they carry the kata build
sessions. That is deliberate: building one kata a week for five weeks is a running
dependency, and a single missed Sunday leaves the following week's rotation with nothing to
draw from. Five front-loaded Sundays, on top of the prep week that builds week 1's six
before day 1, and then it is over and there is nothing left to build.

The exact figures are computed by the generator and printed at the top of
[`plan/CALENDAR.md`](CALENDAR.md), so they are always the real ones.

If you can only give 60 minutes on a weekday, cut the main block — never the kata drill and
never the deck. Those two are what produce interview performance, and they are under half an
hour combined.

### The four kata modes

A ring buffer does not fit in ten minutes, and pretending it does just teaches you to abandon
reps halfway. So there are four block shapes:

- **Sprint blocks — Mon, Tue, Thu, Fri.** A short C module, in a block sized to beat its target.
  Tuesday carries two of them.
- **Long-rep blocks — Wed, Sun.** The C modules that need real time. Sunday carries two.
- **Python blocks — Mon, Wed, Thu, Fri.** 28 minutes, alongside the C rep rather than instead
  of it. Interleaved on purpose: an interview loop does not block by language, and working out
  which kind of problem you are looking at before solving it is part of the skill.
- **Saturday** is adaptive: no assigned module, a long block, and `make drill` with no
  arguments picks by worst recent time, then longest since last rep, then never attempted.
  It is the day that catches what you have been quietly avoiding, and it is where every
  kata's spare reps live.

**Every block is at least as long as that kata's target time in `tools/drill.py`, and
`make check-calendar` fails if that stops being true.** A twelve-minute target inside a
ten-minute block is a target the timer rule forbids you from hitting, which is exactly the
kind of quiet contradiction this repo is supposed to catch.

### Where the hours land

| Weeks | Mimic | This repo |
|---|---|---|
| 1–5 | weekday main blocks + Saturday | C kata, **Python kata**, deck, log, review, **build session** |
| 6–8 | weekday main blocks + Saturday | C kata, Python kata, deck, log, review, prompt, **architecture drill**, rehearsal |
| 9–14 | paused | all of it |

**Weeks 1–8: Mimic gets roughly 48 hours.** That is what Stage 0 realistically costs given
the depth of the workbook, and it is the whole reason the split is weighted this way. The
ten-week plan gave it 36 and compressed two sessions into shared weeks.

**Weeks 9–14: Mimic pauses.** Not abandoned — paused. Stage 1 restarts afterwards. The
harness and the test material come first, because test and integration is the shorter path
from where these skills already are.

---

## Weeks 1–8 — Stage 0

Main block is the Mimic workbook, following its own session order. The job here is to not
let it absorb the other two and a half hours.

**The kata rotation is generated, not hand-written.** `tools/schedule.py` holds what each
kata is owed and the week it may first appear; the rotation falls out of that, and the build
plan falls out of the rotation. Change when a module is introduced and everything downstream
moves with it.

**Week 5's Saturday swaps to M4.1 EMG dataset work** — Python, no hardware. It is already in
the calendar.

### Week 8 gate — both must be true

1. Mimic's Stage 0 exit gate, all ten criteria, tagged `v0.0-stage0-exit`.
2. From this repo: clean-first-compile rate above 55%, and the logged-rep floor printed in the
   gate block of [`plan/CALENDAR.md`](CALENDAR.md). It is derived from the rotation rather than
   restated here, because a number typed into a document is a number that goes stale.

If (1) slips, push everything a week. If (2) is failing, the robot has been eating the kata
slot — that is the exact failure mode this plan is built to prevent, and it is why the gate
names a number from the log rather than a feeling.

---

## Weeks 9–12 — Test engineering, the harness, and the write-up

Mimic pauses. The main block moves to this repo.

**Week 9 — test engineering.** Five consecutive days of pytest: discovery, assertions and
exit codes; fixtures, scope and teardown that survives a failing test; `parametrize`; then
verification vs validation, traceability and IEC 62304. Those five days are also what build
the `test_harness_py` kata, which is why that one module has no separate build session.

It is no longer *from zero*. The Python katas have been running in their own daily block
since week 1, so week 9 starts from someone who can already write the language and is
learning the test framework — which is the right order, and was the point of moving Python
earlier.

**Weeks 10–11 — the harness, against your own Stage 0 board.** pyserial, a fixture that
resets the device between tests, flashing from the harness, fault injection, requirement IDs
in test names, then the instrument driver and a green CI run against real hardware. This is
the flagship and it must point at the Stage 0 board: one story instead of two, because you
wrote the firmware and then built the rig that regression-tests it in CI on every commit.
Two weeks rather than one, because a week of it produced a harness and no write-up. Spec in
[`projects/hil-harness/BRIEF.md`](../projects/hil-harness/BRIEF.md).

**Week 12 — finish and write it up.** A README that states what the harness verifies and what
it cannot catch. One drafted OQ protocol, and a raw capture reduced to a summary, a plot and
a written verdict — T26 and T28, which have no other home. Then the behavioural work:
`STORIES.md` filled from Mimic's `NOTES.md` and the tuning history, and the first heavy block
of takes.

---

## Weeks 13–14 — interview simulation

Two passes, not one. Week 13 is a timed two-hour mock take-home with no AI, debriefed out
loud the next day as if defending it; a full deck pass; the ten-minute presentation, timed,
twice; a cold verbal round. Week 14 repeats it against an unseen shape — a failing suite you
have to make green, which is the one take-home format nothing else here trains — and ends
with `make report` and `make progress` against week 1, and the retro.

The second pass is the point. One mock tells you how it went; two tell you whether the first
lesson stuck.

---

## Mid-point check — end of week 6

Answer honestly in `logs/WEEKLY_REVIEW.md`:

- Clean-first-compile rate above 40%? If not, the kata slot is being skipped or rushed.
- Is the AI-use log shrinking?
- Are deck answers actually being said **out loud**? Silent review is a weaker, different skill.
- Is Mimic on pace to reach S8 by the end of week 6?

Adjusting here is normal. Pretending it is on track when it isn't costs the whole fourteen
weeks.

---

## What this plan does not buy

Worth being explicit about, because a plan that claims to produce everything produces nothing.

- **Stages 1–5 of Mimic.** Fourteen weeks buys Stage 0 plus one Stage 4 software session. Stage 1's
  CAN and FreeRTOS work is where firmware C fluency and RTOS evidence would come from, and it
  lands after this window. It restarts in week 11.
- **Hands-on RTOS.** `concurrency_sim` gets the questions answered well. It does not amount to
  RTOS experience and should never be described as such.
- **LeetCode.** Ten problems, in C, deferred by decision — see C12 in
  [`COVERAGE.md`](COVERAGE.md). Largely absent outside FAANG-scale embedded teams and the
  lowest-value hour available here.
- **Debugging unfamiliar C.** *Closed — `make hunt` is the mechanism.* The research says take-homes hand you a codebase; every mechanism
  here starts from an empty editor. It is written up as a known gap in
  [`INTERVIEW_REQUIREMENTS.md`](INTERVIEW_REQUIREMENTS.md) rather than quietly ignored.
- **Firmware-role depth.** Fourteen weeks of drilling produces fluency and evidence, not years of
  shipped product. What it produces is the ability to demonstrate the fluency under
  observation, which is the specific thing the research says candidates are rejected for.
