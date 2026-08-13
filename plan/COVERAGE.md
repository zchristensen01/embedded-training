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

Seven mechanisms. The C and Y groups are katas; the rest are not.

The counts below are the ones `make progress` prints; if they ever disagree with the table,
`make progress` is right and this table is stale. `make check-coverage` proves every capability
in the spec has exactly one row here, and vice versa.

| Group | n | Where the evidence bar sits | The artifact |
|---|---|---|---|
| **C** — C fluency | 12 | 10 katas, 1 the log itself (C1), 1 deferred | `practice/katas/*/` — write it cold, timed, every rep |
| **Y** — Python fluency | 3 | 2 katas, 1 deck | `practice/katas/*_py/`, `practice/decks/python.tsv` |
| **E** — embedded concepts | 34 | Deck for 33; 1 the architecture drill (E30) | `practice/decks/embedded.tsv` — spoken aloud with the trap |
| **H** — hardware & debugging | 11 | 7 deck, 4 the bench (Mimic) | The bench, plus captures in Mimic's `docs/` |
| **T** — test & integration | 28 | deck, 1 design prompts, 3 katas, the HIL project, 1 deferred | `practice/decks/test-integration.tsv`, `projects/hil-harness/BRIEF.md`, `practice/design-prompts/SUBJECTS.md` |
| **B** — behavioural | 11 | Rehearsal | `practice/rehearsal/STORIES.md`, `make rehearse` |

**A capability can have several mechanisms but only one bar.** E1 is a verbal question whose bar
is "said aloud with the trap named", so its bar is the deck even though `register_map` also
drills it; the kata is reinforcement. `tools/progress.py:bar_for()` is where that precedence
lives, and it is the only place it lives. One rule matters: **a kata in this repo always outranks
work tracked elsewhere.** Anything owned by a kata here is scored here.

Every mechanism is repeatable and recorded, not just the katas:

| Mechanism | Repeat by | Recorded in | Command |
|---|---|---|---|
| Kata | Frozen tests, deleted `src/`, variants | `logs/log.tsv`, `logs/splits.tsv` | `make drill` |
| Deck | Leitner boxes, 1/2/4/8/16 days | `practice/decks/.state.json` | `make review` |
| Design prompt | 40 rotating subjects, one fixed rubric | `logs/design-prompts/` | `make prompt` |
| Architecture drill | 8 rotating prompts, a different fixed rubric | `logs/architecture/` | `make design` |
| Bug hunt | Your own old solution, mutated | `logs/bughunt.tsv` | `make hunt` |
| Rehearsal | Re-tell until three strong takes on three days | `logs/rehearsal.tsv` | `make rehearse` |
| Project | Not repeatable. One-shot | The public repo | — |

## The split, in one line

**Mimic owns depth. This repo owns speed, recall, Python fluency, and test engineering.**

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
**D** = deck card · **P** = the HIL harness project · **R** = rehearsal ·
**Design prompts** / **Architecture drill** spelled out in full where they own a bar.

**`P` here is the project, not a capability group.** Python fluency is group **Y** for exactly
this reason — a `P1` sitting in a table whose owner column already uses `P` would be ambiguous
to a reader even though the parser keeps the two namespaces apart.

### C — C language and syntax fluency

| ID | Owner | Notes |
|---|---|---|
| C1 syntax fluency | **K** | Scored on the clean-first-compile rate across every module, not on retiring one kata — it is the only capability the whole log measures at once. Mimic gives volume in **C++**, not C |
| C2 pointers | **K** `mem_primitives`, `pool_allocator`, `fsm` | Pointer arithmetic and array decay in the first, the free list threaded through free blocks in the second, function pointers in the third. All three retired, because "no reference" means all of it |
| C3 string primitives | **K** `mem_primitives` | Mimic never asks for these |
| C4 memory primitives | **K** `mem_primitives` | |
| C5 ring buffer | **K** `ring_buffer` | Mimic never forces you to write one cold. Highest-value kata you have |
| C6 bit manipulation | **K** `bitops` + M0 incidental | Mimic uses bit ops; it doesn't drill them |
| C7 endianness | **K** `bitops` | |
| C8 struct padding | **K** `register_map` | |
| C9 pool allocator | **K** `pool_allocator` | Mimic allocates nothing |
| C10 fixed point | **K** `fixed_point_pid` | **Kata retained.** Stage 0's PID uses floats; the Q-notation reps are still yours to do |
| C11 timer rollover | **K** `rollover_timer` + M0 S5 | S5's `next += period` is the same idea. Kata makes it fast |
| C12 the ten DSA problems | **Deferred** | **Not scheduled, by decision.** The research found LeetCode-style DSA largely absent outside FAANG-scale embedded teams, and this is the lowest-value hour available. Turn it on only if Google, Meta Reality Labs or Anduril is actually in play — those pipelines are shared with general software engineering and do ask. The ten problems are written up in `reference/question-bank/embedded-coding.md`. Marked deferred rather than left as an unowned kata so `make progress` reports it honestly instead of showing a capability that can never be met |

### Y — Python fluency

Mimic covers none of this — it is C++ on a robot. Nothing outside this repo produces it either,
which is why all three bars sit here.

| ID | Owner | Notes |
|---|---|---|
| Y1 python internals | **D** | The deck is the bar: these are "what does this print and why" answers, and the mechanism that proves you can produce one cold across spaced sessions is box 4. Cards live in `practice/decks/python.tsv` |
| Y2 binary telemetry | **K** `binary_frame_py` | The host side of `protocol_parser` — same framing problem seen from the test harness rather than the firmware. Do them close together on purpose |
| Y3 domain scripting | **K** `log_parser_py` | Stream-parse, reduce, exit code. The shape of every reported T&I live-coding task and of the SpaceX telemetry take-home |

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
| E13 priority inversion | **D + K** `concurrency_sim` | Build it, watch it, fix it. Nothing in Mimic does. The deck is the bar because the question is verbal; the kata is what makes the answer yours |
| E14 deadlock | **D + K** `concurrency_sim` | |
| E15 race vs data race | **D + K** | |
| E16 volatile ≠ synchronisation | **D + K** | |
| E17 scheduling | **D** + M1 S1.5 | |
| E18 protocol comparison | **D** + M0/M1 | Mimic gives you UART, I2C, SPI, CAN hands-on. Deck makes it sayable in 90 seconds |
| E19 I2C pull-ups | **D** + M0 | |
| E20 SPI modes | **D** + M0 | |
| E21 CRC | **D + K** `protocol_parser` | |
| E22 DMA | **D** | Not in Mimic Stage 0 |
| E23 state machines | **D + K** `fsm` + M0 | |
| E24 debouncing | **D + K** `debouncer` + M0 | **Kata retained.** Cheap reps, and it's asked |
| E25 watchdog | **D** + M1 | |
| E26 linker script and map file | **D** + M1 | Stage 1's CubeIDE project has a real linker script. Until then it's the deck |
| E27 firmware update and rollback | **D** | Not in Mimic at all. Asked wherever a device ships to a customer |
| E28 low-power modes | **D** | Not in Mimic — the arm is mains-powered and never sleeps |
| E29 super-loop vs RTOS | **D** + M1 S1.5 | S1.5's two tasks and a queue is the worked example of the cost side. The card is the answer |
| E30 architect a subsystem | **Architecture drill** (`make design`) | The one capability with a mechanism built for it alone. A dedicated round at Google and Meta Reality Labs that nothing else here produces — katas start from a written contract, design prompts ask how you would *test* a thing, and neither asks you to invent the thing |
| E31 bootloader and update path | **D** | E27 covers field update conceptually; this is the mechanism and the verification design |
| E32 functional safety | **D** | **Deliberately deck-only.** The second research pass found DO-178C in 0 of 32 test-role postings and argued for down-weighting it. Kept because automotive and aerospace loops do ask, scoped to one card because the evidence does not support more |
| E33 embedded cybersecurity | **D** | Now a legal requirement for connected medical devices (§524B), not a nice-to-have |
| E34 hard-fault debugging | **D** | The bar is the card. Recovering a faulting PC on real hardware belongs to Mimic's bench time, and is reinforcement rather than the bar |

### H — Hardware and debugging

| ID | Owner | Notes |
|---|---|---|
| H1 methodical comms debugging | **D** + M0/M1 | Verbal scenario, so the deck is the bar. Mimic's "what will go wrong" sections are the material |
| H2 scope vs analyzer | **D + M0 S3** | S3 is your first capture |
| H3 reading captures | **M0** | The exit gate requires a saved capture. Portfolio evidence |
| H4 schematic reading | **M0 S2** | The power topology drawing |
| H5 datasheet under pressure | **M0/M1** | "Look it up yourself" sessions are exactly this |
| H6 Ohm's law, power | **D + M0 S1, S2** | Asked verbally as a two-line calculation, so the deck is the bar. The torque and supply math is where you do it for real |
| H7 Nyquist | **D** | Not in Stage 0 |
| H8 pull-ups / floating | **D + M0** | |
| H9 JTAG/SWD, debuggers | **D + M1 S1.1** | The breakpoint that is the actual point |
| H10 bench competence | **M0** | Multimeter, soldering, analyzer — all in Stage 0 |
| H11 DMA cache coherency | **D** | The stock debugging scenario. Mimic's M4 has no data cache, so the bug is not reachable there — this one is the deck's alone |

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
| T19 CI on hardware | **P** | A green run against real hardware, captured |
| T20 Bash | **P** | |
| T21 test-to-requirement tracing | **P** | |
| T22 host-side testing of firmware C | **D** + M0 S12 | The deck is the bar. S12's host-side Unity tests on the PID and encoder table are the worked example, and the harness's fake transport is the same idea one layer up |
| T23 static analysis and MISRA | **D** | `make analyze` puts `gcc -fanalyzer` in front of you daily, which is the habit. The card is the answer |
| T24 instrument control | **P** | The bar is an instrument driver class in the harness repo. `cli_tool_py` and the deck cards on SCPI synchronisation are reinforcement — you cannot prove this one without a scope on the bench |
| T25 measurement quality | **D** | **Scoped to the card deliberately.** Calibration and uncertainty get asked; running a Gauge R&R study is metrology coursework and does not belong in ten weeks of interview prep |
| T26 regulated CSV | **P** | The highest-value T addition for a Canada-based candidate: Medtronic and Abbott name IQ/OQ/PQ, GAMP 5 and 21 CFR Part 11 in 5 of 32 postings. The bar is **P** rather than the deck because the stated evidence is a drafted OQ protocol — an artifact, not an answer. Qualifying your own harness is the exercise. The deck card on the same topic is reinforcement |
| T27 read a C# harness | **Deferred** | **Not scheduled, by decision.** C# appears in 6 of 32 postings but only on the manufacturing-test side. The second research pass says explicitly it is "only worth doing if Intuitive or Medtronic manufacturing is live". Turning it on means reading fluency, not authoring — deferred rather than dropped so `make progress` reports it honestly |
| T28 reduce and conclude | **P** | What sits behind B4. A test result nobody turned into a conclusion is not a test result. The harness produces the captures |
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
| B11 defend an architecture | **R**, sourced from **`make design`** | Rehearsal owns the bar, because what is being graded is whether you hold a position under pressure. The material comes from the architecture drill — take the design you just defended on paper and defend it again out loud |

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

It is available now rather than a year out, and it doubles as T&I practice, because a classifier
with no evaluation methodology is not a result — the evaluation is the artifact, not the model.

Slot it into weekend blocks from around Week 4. It is the only part of Mimic beyond Stage 0 worth
touching inside these ten weeks.
