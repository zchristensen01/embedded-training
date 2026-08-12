# Coverage

Who is responsible for each capability in `plan/INTERVIEW_REQUIREMENTS.md`.

**Mimic lives in its own repo and is not part of this one.** This document exists so you know
what Mimic already covers and therefore what this repo must not duplicate. Nothing here changes
how you build Mimic.

Two systems are running at once and they do different jobs:

- **Mimic** builds a real robot. It produces **understanding and artifacts**. Slow, deep, one-shot.
- **This repo** builds interview performance. It produces **speed, recall, and evidence**.
  Fast, repeated, measured.

Neither substitutes for the other. The most common way to waste the next ten weeks is to assume
that because Mimic taught you something, you can perform it cold in fifteen minutes with someone
watching. You can't. That's a separate skill and it only comes from reps.

---

## Where every capability actually lives

78 capabilities, five mechanisms. Only the C group is katas.

| Group | n | Where it lives | The artifact |
|---|---|---|---|
| **C** — C fluency | 12 | Katas | `practice/katas/*/` — write it cold, timed, every rep |
| **E** — embedded concepts | 25 | Deck, ~8 also a kata | `practice/decks/embedded.tsv` — spoken aloud with the trap |
| **H** — hardware & debugging | 10 | Mimic Stage 0 mostly, 5 deck | The bench, plus captures in Mimic's `docs/` |
| **T** — test & integration | 21 | 3 katas, 12 deck, 6 the HIL project | `practice/decks/test-integration.tsv`, `projects/hil-harness/BRIEF.md`, `practice/design-prompts/SUBJECTS.md` |
| **B** — behavioural | 10 | Rehearsal | `practice/rehearsal/STORIES.md`, `make rehearse` |

Every mechanism is repeatable and recorded, not just the katas:

| Mechanism | Repeat by | Recorded in | Command |
|---|---|---|---|
| Kata | Frozen tests, deleted `src/`, variants | `logs/log.tsv`, `logs/splits.tsv` | `make drill` |
| Deck | Leitner boxes, 1/2/4/8/16 days | `practice/decks/.state.json` | `make review` |
| Design prompt | 40 rotating subjects, one fixed rubric | `logs/design-prompts/` | `make prompt` |
| Rehearsal | Re-tell until three strong takes on three days | `logs/rehearsal.tsv` | `make rehearse` |
| Project | Not repeatable. One-shot | The public repo | — |

## The split, in one line

**Mimic owns depth. This repo owns speed, recall, and test engineering.**

---

## What Mimic Stage 0 covers, and what it therefore replaces

Stage 0 is the target. Six weeks. It replaces four standalone projects from the original plan,
which are now **deleted, not deferred**:

| Deleted project | Replaced by | Why the replacement is better |
|---|---|---|
| Bare-metal GPIO + timer/PWM | S11 Part B — getting off `analogWrite()` | Real PWM on a real motor with a safety envelope around it |
| Interrupt-driven UART driver | S3 encoder interrupts + S7 telemetry with a bandwidth budget | You derive the serial budget rather than guessing a baud rate |
| Multi-sensor I2C/SPI drivers | Stages 0–1, Stage 4 IMUs | Deferred, but real when it lands |
| Cooperative scheduler / RTOS | S1.5 FreeRTOS two tasks and a queue | Includes the demonstration that justifies using an RTOS at all |
| Protocol emulator / fault injector | S1.6–S1.9 CAN, protocol design, filters, silent-host timeout | Two physical nodes and a protocol you designed on paper |

**Still yours to build:** the HIL harness. Nothing in Mimic covers it, and it is the wedge.

---

## Capability ownership table

Legend: **M0** = Mimic Stage 0 · **M1+** = Mimic Stage 1 or later · **K** = kata in this repo ·
**D** = deck card · **P** = the HIL harness project · **R** = rehearsal

### C — C language and syntax fluency

| ID | Owner | Notes |
|---|---|---|
| C1 syntax fluency | **K** | Mimic gives volume in **C++**, not C. The daily kata is the only thing producing C fluency |
| C2 pointers | **K** | |
| C3 string primitives | **K** `mem_primitives` | Mimic never asks for these |
| C4 memory primitives | **K** `mem_primitives` | |
| C5 ring buffer | **K** `ring_buffer` | Mimic never forces you to write one cold. Highest-value kata you have |
| C6 bit manipulation | **K** `bitops` + M0 incidental | Mimic uses bit ops; it doesn't drill them |
| C7 endianness | **K** `bitops` | |
| C8 struct padding | **K** `register_map` | |
| C9 pool allocator | **K** `pool_allocator` | Mimic allocates nothing |
| C10 fixed point | **K** `fixed_point_pid` | **Kata retained.** Stage 0's PID uses floats; the Q-notation reps are still yours to do |
| C11 timer rollover | **K** `rollover_timer` + M0 S5 | S5's `next += period` is the same idea. Kata makes it fast |
| C12 the ten DSA problems | **Deferred** | **Not scheduled, by decision.** The research found LeetCode-style DSA largely absent outside FAANG-scale embedded teams, and this is the lowest-value hour available. The ten problems are written up in `reference/question-bank/embedded-coding.md` if a specific employer makes them relevant. Marked deferred rather than left as an unowned kata so `make progress` reports it honestly instead of showing a capability that can never be met |

### E — Embedded concepts

| ID | Owner | Notes |
|---|---|---|
| E1 volatile | **D + K** `register_map` | **Mimic actively hides this.** CubeIDE's HAL generates register access for you |
| E2 static | **D + K** `register_map` | |
| E3 const/volatile combinations | **D + K** `register_map` | The canonical MMIO declaration — write it until automatic |
| E4 const in flash | **D** | |
| E5 stack vs heap | **D + K** `pool_allocator` | |
| E6 stack sizing | **D** + M1 S1.5 | Stage 1 does real stack sizing and it bites there |
| E7 before main() | **D** + M1 | Stage 1's CubeIDE startup files are the real thing |
| E8 padding/alignment | **D + K** | |
| E9 ISR rules | **D** + **M0 S3** | S3 is a real encoder ISR. Strong evidence once done |
| E10 ISR data sharing | **D** + M0 S3 | |
| E11 interrupt latency | **D** | |
| E12 mutex vs semaphore | **D + K** `concurrency_sim` | **Mimic does not cover this.** S1.5 gives tasks and a queue, not ownership semantics |
| E13 priority inversion | **K** `concurrency_sim` | Build it, watch it, fix it. Nothing in Mimic does |
| E14 deadlock | **K** `concurrency_sim` | |
| E15 race vs data race | **D + K** | |
| E16 volatile ≠ synchronisation | **D + K** | |
| E17 scheduling | **D** + M1 S1.5 | |
| E18 protocol comparison | **D** + M0/M1 | Mimic gives you UART, I2C, SPI, CAN hands-on. Deck makes it sayable in 90 seconds |
| E19 I2C pull-ups | **D** + M0 | |
| E20 SPI modes | **D** + M0 | |
| E21 CRC | **D + K** `protocol_parser` | |
| E22 DMA | **D** | Not in Mimic Stage 0 |
| E23 state machines | **K** `fsm` + M0 | |
| E24 debouncing | **K** `debouncer` + M0 | **Kata retained.** Cheap reps, and it's asked |
| E25 watchdog | **D** + M1 | |

### H — Hardware and debugging

| ID | Owner | Notes |
|---|---|---|
| H1 methodical comms debugging | **M0/M1** | Mimic's "what will go wrong" sections are this, repeatedly |
| H2 scope vs analyzer | **D + M0 S3** | S3 is your first capture |
| H3 reading captures | **M0** | The exit gate requires a saved capture. Portfolio evidence |
| H4 schematic reading | **M0 S2** | The power topology drawing |
| H5 datasheet under pressure | **M0/M1** | "Look it up yourself" sessions are exactly this |
| H6 Ohm's law, power | **M0 S1, S2** | The torque and supply math |
| H7 Nyquist | **D** | Not in Stage 0 |
| H8 pull-ups / floating | **D + M0** | |
| H9 JTAG/SWD, debuggers | **D + M1 S1.1** | The breakpoint that is the actual point |
| H10 bench competence | **M0** | Multimeter, soldering, analyzer — all in Stage 0 |

**Mimic is the clear winner on H.** Almost the entire hardware column is Stage 0's job. This is
where the robot earns its place in the plan.

### T — Test and integration

| ID | Owner | Notes |
|---|---|---|
| T1 "how would you test X" | **Design prompts** (`make prompt`) | Not in Mimic at all |
| T2 verification vs validation | **D** | |
| T3 traceability | **D + P** | |
| T4 IEC 62304 | **D** | Mimic's own traceability marks this *not covered* |
| T5 test lifecycle | **D** | |
| T6 change impact analysis | **D** | |
| T7 test types | **D** | |
| T8 defect reports | **D** | |
| T9 field debugging | **D** | |
| T10 fixture/harness/HIL | **D + P** | |
| T11 flakiness | **D + P** | |
| T12 when not to automate | **D** | |
| T13 pytest basics | **K** `test_harness_py` | |
| T14 fixtures | **K** `test_harness_py` | |
| T15 parametrize | **K** `test_harness_py` | |
| T16 device abstraction | **P** | |
| T17 real serial | **P** | |
| T18 fault injection | **P** | |
| T19 CI on hardware | **P** | The screenshot that goes in outreach |
| T20 Bash | **P** | |
| T21 test-to-requirement tracing | **P** | |
| — | **M0 S12** partial credit | About an hour of host-side Unity tests on the PID and encoder table. Genuinely good, and more than most embedded portfolios have. Not remotely the whole column |

**This repo owns almost all of T.** T&I is your faster job door, and Mimic covers roughly 5% of
it. This is the single most important reason not to let the robot absorb all your hours.

### B — Behavioural and narrative

| ID | Owner | Notes |
|---|---|---|
| B1 why hardware | **R** | Mimic *is* the answer. You still have to rehearse saying it |
| B2 why this domain | **R** | |
| B3 project walkthrough | **R**, sourced from **M0** | Stage 0's exit gate is the material |
| B4 how I tested it | **R**, sourced from **M0 S12 + P** | |
| B5–B9 STAR stories | **R**, sourced from **M0** | Mimic's failures are your stories. Log them as they happen |
| B10 10-minute presentation | **R** | Stage 0 exit artifacts make the deck |

---

## Stage 0's exit gate, translated into interview language

Stage 0's gate is already written in test-engineering terms. You just have to say it that way.

| Workbook language | What an interviewer hears | Serves |
|---|---|---|
| "Prove your loop rate, measured not intended" | Verification against a requirement with objective evidence | T2, B4 |
| Four demonstrated failure tests: soft limits, velocity limiting, command timeout, stall latch | Negative and boundary testing | T1, B4 |
| Step-response metrics: rise, overshoot, settling, steady-state error | Quantified acceptance criteria | T1, B3 |
| `docs/decisions/` | Design rationale and traceability | T3, B3 |
| S12's derivative-on-measurement unit test | "A bug my tests caught" — in 50 µs on a laptop instead of on a bench with a motor slamming | B8 |
| Git history showing tuning failures | Defect tracking and evidence of process | B5, B9 |

That last row is worth rehearsing standalone. Most candidates hide their failures; a history that
contains them deliberately reads as maturity.

---

## The one thing to pull forward

Mimic Stage 4 says it itself: *start with the software, months early.* **M4.1 is EMG feature
extraction on public datasets — Python, no hardware, no dependency on Stages 1 through 3.**

Given the kinesiology background, an EMG classifier with a real evaluation writeup is the most
differentiating artifact you could put in front of a medical-device employer, and it's available
now rather than a year out. It also doubles as T&I practice, because a classifier with no
evaluation methodology is not a result.

Slot it into weekend blocks from around Week 4. It is the only part of Mimic beyond Stage 0 worth
touching before you apply.
