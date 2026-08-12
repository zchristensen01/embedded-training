# The plan

Ten weeks. Stage 0 finished at week 6, applications out at week 6, HIL harness built while the
hiring pipeline runs.

---

## Hours

**Budget: about 10.7 hours a week from week 3 on.** Five weekdays at 90 minutes, a 130-minute
Saturday, and a light 60-minute Sunday.

**Weeks 1 and 2 are the exception: about 15 and 14 hours.** They carry the two kata build
sessions. That is deliberate — building one kata a week for five weeks is a running dependency,
and a single missed Sunday leaves the following week's rotation with nothing to draw from. Two
heavy weekends, then it is over.

`plan/CALENDAR.md` has all seventy days already laid out with timer durations and a fixed kata per
day, so you never have to decide anything at 7am. Regenerate it with real dates using
`make calendar` once you've set a start date.

If you can only give 60 minutes on a weekday, cut the main block — never the kata drill and never
the deck. Those two are the parts that produce interview performance, and they're only 25 minutes
combined.

### Sprint weekday — Mon, Tue, Thu, Fri — 90 minutes

| Timer | What | Owner |
|---|---|---|
| 10 min | Kata drill, **short module**, timed and cold | This repo |
| 60 min | Main block | Mimic (weeks 1–6) or this repo (weeks 7–10) |
| 12 min | Deck review, **out loud** | This repo |
| 8 min | Log the rep, log the session, commit | Both |

### Long-rep weekday — Wednesday — 90 minutes

| Timer | What | Owner |
|---|---|---|
| 25 min | Kata drill, **long module** — ring buffer, allocator, FSM, concurrency | This repo |
| 45 min | Main block | Mimic or this repo |
| 12 min | Deck review, out loud | This repo |
| 8 min | Log and commit | Both |

The two kata modes exist because a ring buffer does not fit in ten minutes and pretending it does
just teaches you to abandon reps halfway. Short katas get four slots a week; long katas get two.

### Saturday — 130 minutes

| Timer | What |
|---|---|
| 10 min | Kata drill, **adaptive** — `make drill` with no arguments |
| 120 min | Main block |

Still no deck. Saturday is the only day with no assigned module, and that is the point: the
adaptive picker takes worst recent time first, then longest since last rep, then never
attempted — so Saturday is the day that catches whatever you have been quietly avoiding, rather
than following the plan.

### Sunday — 60 minutes, the light day

| Timer | What |
|---|---|
| 25 min | Kata, long module |
| 20 min | `make report`, then fill in `logs/WEEKLY_REVIEW.md` |
| 15 min | Full deck pass, `make review 30` |

**Weeks 1 and 2 only:** a kata build session is appended here, which is what makes those two
Sundays long. The modules and the timing come from the Build plan at the top of
`plan/CALENDAR.md`; it is generated from the rotation rather than written by hand, so it cannot
drift out of step with what the calendar asks you to drill. `make check-calendar` proves it.

### Where the hours land

| Weeks | Mimic | This repo | Total |
|---|---|---|---|
| 1–2 | ~7 hr/wk (weekday main blocks + Saturday) | ~8 hr/wk (kata, deck, log, review, **build session**) | ~15, ~14 |
| 3–6 | ~7 hr/wk (weekday main blocks + Saturday) | ~3.7 hr/wk (kata, deck, log, review) | ~10.7 |
| 7–9 | 0 | ~10.7 hr/wk | ~10.7 |
| 10 | 0 | ~10.7 hr/wk | ~10.7 |

**Weeks 1–6: Mimic gets about 42 hours.** That is what Stage 0 realistically costs given the depth of
the workbook. It is the whole reason the split is weighted this way.

**Weeks 7–10: Mimic pauses.** Not abandoned — paused. Stage 1 restarts after you're in a hiring
pipeline. The harness and the test material have to come first, because test & integration is the
faster door.

---

## Why week 6 is the application trigger

Mimic's own estimate is roughly a year for all five stages. "Largely done before I apply" and
"apply soon" cannot both be true, so applications go out when **Stage 0's exit gate is tagged and
pushed** — not when the arm is finished.

Stage 0's gate on its own beats what most junior candidates bring: a measured loop rate with a
saved capture, annotated step responses, four demonstrated failure tests, anti-windup and
derivative-on-measurement you can explain, host-side unit tests, and a git history showing the
tuning failures.

Hiring runs three weeks to two months. Applying at week 6 means weeks 7–10 happen *while* the
pipeline moves, and the harness is finished before most first-round interviews land.

---

## Weeks 1–6 — Stage 0

Main block is the Mimic workbook, following its own session order. Your job here is to not let it
absorb the other 2.5 hours.

| Week | Mimic sessions | Kata pool | Deck focus |
|---|---|---|---|
| 1 | S0 bench and repo, S1 motor forensics | `bitops`, `mem_primitives` | types, pointers, strings |
| 2 | S2 power, S3 encoder and interrupts | `mem_primitives`, `ring_buffer` | interrupts, memory |
| 3 | S4 open loop, S5 fixed-rate loop | `ring_buffer`, `register_map` | volatile, static, const |
| 4 | S6 units, S7 telemetry | `register_map`, `fsm` | registers, alignment |
| 5 | S8 P-only, S9 step metrics, S10 D then I | `fixed_point_pid`, `debouncer`, `rollover_timer` | protocols, timing |
| 6 | S11 safety envelope and real PWM, S12 refactor and tests | `pool_allocator`, `concurrency_sim` | sync, RTOS |

Saturday blocks: whatever the week's Mimic sessions need. **Week 4's Saturday swaps to M4.1 EMG
dataset work** — Python, no hardware, and it is your medical-device differentiator. It's already
in the calendar.

**The kata rotation deliberately avoids what Mimic is teaching that week.** In week 3 Mimic is
doing timing loops, so the kata is `register_map` — the thing CubeIDE's HAL will hide from you
later. Don't double up; use the drill to cover the gaps.

### Week 6 gate — both must be true

1. Mimic's Stage 0 exit gate, all ten criteria, tagged `v0.0-stage0-exit`.
2. From this repo: clean-first-compile rate above 55%, and 25+ logged kata reps.

If (1) slips, push everything a week. If (2) is failing, you have been letting the robot eat the
kata slot — that is the exact failure mode this plan is built to prevent.

**End of week 6: applications go out.** Six to eight test & integration roles. Resume reframed per
`reference/question-bank/README.md`.

---

## Weeks 7–9 — Test engineering and the harness

Mimic pauses. Main block moves to this repo.

### Week 7 — Test engineering from zero

| Day | Main block |
|---|---|
| Mon | pytest from scratch: discovery, assertions, exit codes. 20 tests on a pure function |
| Tue | Fixtures, scope, teardown that survives a failing test. `conftest.py` |
| Wed | `parametrize`. Then verification vs validation, and test plan structure |
| Thu | Traceability, IEC 62304 classes, one test case per requirement |
| Fri | `make prompt` ×3. Score each against the rubric |
| Weekend | Device abstraction over a fake transport. The same tests must pass on both |

### Week 8 — The harness, against your own Stage 0 board

| Day | Main block |
|---|---|
| Mon | pyserial: open, write, read with timeout, frame the responses. Talk to the board |
| Tue | Fixture that opens and closes the port and resets the device between tests |
| Wed | Flashing from the harness. Test isolation |
| Thu | Fault injection: truncated frames, bad CRC, impossible lengths. Assert recovery |
| Fri | Trace each test to a Stage 0 requirement. Requirement IDs in the test names |
| Weekend | Dockerise it. GitHub Actions with a self-hosted runner |

**This is the flagship and it must point at your Stage 0 board.** One story instead of two: you
wrote the firmware, then you built the rig that regression-tests it in CI on every commit. That is
the shape of the Kepler posting.

### Week 9 — Finish and write it up

| Day | Main block |
|---|---|
| Mon | Green CI run against real hardware. Screenshot it |
| Tue | README: what it verifies, what it cannot catch, how tests trace to requirements |
| Wed | `make prompt` ×4. Then the full protocol and hardware verbal set |
| Thu | Behavioural: six STAR stories written out, sourced from Mimic's failures |
| Fri | Project deep-dive rehearsal ×3, recorded |
| Weekend | Publish. Harness repo public. Site updated with the Stage 0 sequence |

---

## Week 10 — Interview simulation

| Day | Main block |
|---|---|
| Mon | Timed 2-hour mock take-home, AI-free: state machine, a debugging task, bit masking |
| Tue | Debrief the take-home out loud as if defending it. Record it. Watch it back |
| Wed | Full deck pass. Every card in box 4 or higher, or it goes back to daily |
| Thu | Ten-minute project presentation, timed, twice |
| Fri | Second application wave — embedded and firmware roles this time |
| Weekend | `make report`. Compare the week 1 and week 10 curves |

---

## Mid-point check — end of week 4

Answer honestly in `logs/WEEKLY_REVIEW.md`:

- Clean-first-compile rate above 40%? If not, the kata slot is being skipped or rushed.
- Is the AI-use log shrinking?
- Are you actually saying deck answers **out loud**? Silent review is a weaker, different skill.
- Is Mimic on pace to reach S8 by the end of week 5?

Adjusting here is normal. Pretending it is on track when it isn't costs you the whole ten weeks.

---

## What this plan does not buy you

- **Stages 1–5 of Mimic.** You get Stage 0 plus one Stage 4 software session. Stage 1's CAN and
  FreeRTOS work is where firmware C fluency and RTOS evidence would come from, and it lands after
  the application date. Restart it in week 11.
- **Hands-on RTOS.** `concurrency_sim` gets you answering the questions well. It does not let you
  claim RTOS experience.
- **LeetCode.** Ten problems, in C, low priority. Largely absent at your targets and the
  lowest-value hour available.
- **Firmware-role readiness.** At week 10 you are genuinely ready for **test & integration** and
  credible but junior for firmware. That is the honest position, and it matches where the faster
  door is.
