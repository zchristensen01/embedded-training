# Coverage

Who is responsible for each capability in `plan/INTERVIEW_REQUIREMENTS.md`.

**Mimic lives in its own repo and is not part of this one.** This document exists so you know
what Mimic already covers and therefore what this repo must not duplicate. Nothing here changes
how you build Mimic.

Two systems are running at once and they do different jobs:

- **Mimic** builds a real robot. It produces **understanding and artifacts**. Slow, deep, one-shot.
- **This repo** builds interview performance. It produces **speed, recall, and evidence**.
  Fast, repeated, measured.

Neither substitutes for the other. The most common way to waste the next fourteen weeks is to assume
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
| Design prompt | 60 rotating subjects, one fixed rubric | `logs/design-prompts/` | `make prompt` |
| Architecture drill | 8 rotating prompts, a different fixed rubric | `logs/architecture/` | `make design` |
| Bug hunt | Your own old solution, mutated | `logs/bughunt.tsv` | `make hunt` |
| Rehearsal | Re-tell until three strong takes on three days | `logs/rehearsal.tsv` | `make rehearse` |
| Project | Not repeatable. One-shot | The public repo | — |

## The split, in one line

**Mimic owns depth. This repo owns speed, recall, Python fluency, and test engineering.**

---

## What Mimic Stage 0 covers, and what it therefore replaces

Stage 0 is the target. Eight weeks. It replaces four standalone projects from the original plan,
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
| Y1 python internals | **D** | The deck is the bar, and it carries both halves of the research's stated bar. The prose cards are "explain the mechanism"; the **snippet cards** are "here are five lines, what does it print and why" — the half that actually tests live syntax under observation, which is the whole reason this group exists. Box 4 on a snippet card means you predicted it right across spaced sessions with no interpreter. Cards live in `practice/decks/python.tsv`; `tools/review.py:render()` is what lets a one-line TSV field carry a multi-line snippet |
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
| T25 measurement quality | **D** | **Scoped to the card deliberately.** Calibration and uncertainty get asked; running a Gauge R&R study is metrology coursework and does not belong in fourteen weeks of interview prep |
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

## What the research asked for and this repo did not do

Every row here is a deliberate decision, not an oversight. It exists because the alternative —
quietly implementing the cheap half of a two-part evidence bar and letting `make progress` report
it as met — is exactly the self-deception this whole system is built to prevent. If you disagree
with a call, change it; but change it here first.

### Evidence bars scoped down

| Bar | The research asked for | What is implemented | Why |
|---|---|---|---|
| **Y2, Y3** | the decoder written against an **unseen** packet spec / **unseen** parse prompts | three clean reps across three known variants | "Unseen" is not available in a solo repo: you write the frozen suite yourself, so you have seen every spec here. The variants are the nearest honest substitute. The genuinely unseen version is a take-home, and that is what the weeks 13 and 14 mocks are for |
| **Y3** | three prompts back to back in **45 minutes total** | three separate reps at 20 minutes each | Back-to-back-under-one-clock is a different exercise — endurance rather than fluency. Worth adding once the individual reps are at target; not worth blocking the capability on |
| **E29** | deck card **and** a written super-loop-vs-RTOS comparison for a real system | deck card | The written comparison belongs to Mimic, which is where you actually make that decision. Recorded here so nobody thinks the deck card alone was the whole ask |
| **E31, E33** | deck card **and** a diagram drawn from memory (bootloader handoff / signed-boot chain) | deck card | A flashcard cannot verify a drawing. Drawing these is genuinely worth doing — do it in a `make design` session, where the rubric already scores a labelled diagram |
| **E34** | a fault handler **written cold**, plus recovering a faulting PC on real hardware | deck card, with the hardware half handed to Mimic | Writing a hard-fault handler cold needs a target to fault. There is no Cortex-M kata here and adding one for a single LOW-confidence capability is not proportionate |
| **T26, T28** | 5 of 5 / 10 of 10 logged samples | one artifact each, in the harness repo | These are artifacts, not reps. The tenth OQ protocol teaches nothing the first did not; volume was the research's proxy for "you actually did it", and the artifact is better evidence than the count |
| **B11** | takes **recorded** and logged alongside the E30 rubric score | three strong takes on three days | `make rehearse` already tells you to record every third take. The E30 linkage is in the workflow — `make design` ends by telling you to run `make rehearse S=B11` — rather than enforced in the tooling |

Three more were scoped down and are recorded in their own rows above: **E32** (deck only — 0 of 32
postings named DO-178C), **T25** (deck only — a Gauge R&R study is metrology coursework), and
**T27** (deferred — the research gates it on Intuitive or Medtronic manufacturing being live).

### Exercises not landed

| Exercise | Source | Decision |
|---|---|---|
| CAN log filter and 12-bit signal decode | report 2 §3, **LOW** confidence, sourced to a single Tesla posting | **Dropped.** Motorola-vs-Intel bit ordering on a sub-byte signal is real and worth knowing, but it is one posting and the nearest capability is already covered by `log_parser_py` and `binary_frame_py`. Recorded here so the drop is a decision rather than an omission |

### The deck bar is a proportion, not all of them

**Decision, taken deliberately.** A capability whose bar is the deck is met when **80% of its
cards are in box 4 or higher, with a floor of three**. `tools/progress.py:cards_needed()` is
that rule, and `make decks` prints the number beside every capability.

**In practice that is still every card for most of them, and it is worth knowing which.** The
proportion only relaxes anything at five cards or more, because 80% of four rounds up to four.
Of the 55 deck-barred capabilities, 50 have four cards or fewer and therefore need all of them;
only 5 get any slack. So the rule below fixed the incomparability at the top of the range —
Y1's twenty cards now need sixteen rather than twenty — and left the bottom of the range where
it was. Adding a card to a one-, two- or three-card capability still raises its own bar by one
and un-meets it until the new card reaches box 4. Write the card anyway; the score catching up
a fortnight later is the correct behaviour, not a reason to skip it.

It used to be *every* card, which was wrong in two ways that pulled against each other. It
made the bars incomparable: H7 has one card and needed one, T11 has nine and needed nine, Y1
has twenty and needed twenty, so "met" meant something different in each case while the report
listed them in the same column. And it pointed the incentive backwards — **adding a good card
to a capability made that capability harder to meet**, in a system whose whole design is to
prompt you for a card the moment something surprises you. `make done` offers the prompt at the
end of every rep. It should not be a tax.

The floor of three is what stops the proportion becoming a loophole: 80% of two cards is two,
but a capability resting on one or two cards should not be provable on a single lucky answer,
and where the cards do not exist yet the honest answer is that the capability needs more of
them. Nineteen capabilities currently rest on a single card — `make decks` lists them, and
that list is the best guide to where the next `make card` should go.

### What the measurement cannot do

Not decisions about the research — decisions about how much the score is worth. Written down
because "nothing here is self-assessed" is the claim this repo makes loudest, and it is true
of some bars and not others. Knowing which is which is the difference between a score you can
show someone and a score you are telling yourself.

| Limit | What it means |
|---|---|
| **The deck bar is self-graded.** `make review` reveals the answer and asks "Did you say all of it? [y/N]". Nothing verifies you said it, or that you said the trap | This is the bar for the whole **E** group, most of **H** and **T**, and **Y1** — 34 of the 84 scorable capabilities. The spacing is real evidence: you cannot fake having answered a card correctly across five sessions a fortnight apart, because a wrong answer sends it to box 1 and the interval resets. What is not evidence is any single `y`. Treat a box-4 card as "I have said this correctly on four separate days", which is what it is, and not as "an examiner passed me" |
| **Append-only is not enforced.** Editing a row in `logs/log.tsv` passes every check | The logs measure consistency rigorously and capability by proxy. `make check-log` validates shape — dates in order, known modules, real variants — not history. A solo practice log cannot do better, and pretending otherwise would be the exact self-deception the rest of this document exists to prevent |
| **A met kata capability can become unmet.** `kata_retired()` looks at the *last three* reps, and the calendar keeps scheduling a module after it has retired | Retire `ring_buffer` on rep 8, have a bad rep 9, and C5 flips back to "in progress" — correctly by the letter of the bar, surprisingly by the spirit of it, since `make progress` had already said you could do it. The rehearsal bar does not behave this way: `ready()` counts strong takes ever, so B-group capabilities only ever move forwards |
| **The deck bar needs about 90% accuracy, and no amount of calendar fixes that.** A card reaches box 4 on three correct answers with 1-, 2- and 4-day gaps, and a wrong answer sends it back to box 1 | Simulated against the real 162 cards and the real day shape: at 100% you finish all of them, at 90% about 154, at 80% about 139, at 70% about 100. **Stretching the plan from 70 days to 98 moved that by one card.** It is not a race you can win with more time — boxes 4 and 5 come back every 8 and 16 days, so a wrong answer costs a card a week whenever it happens, and the fraction sitting at box 4+ settles at an equilibrium set by your accuracy rather than climbing toward the deadline. Nothing checks it, because the number that decides it is the one no tool can know in advance. `make stats` is the in-flight signal: cards stuck in boxes 1–2 by week 5 means the method, not the schedule |
| **`make hunt` is not "code you did not write".** It mutates your own earlier solution | You are diffing against memory rather than reading a stranger's intent. See the Known gaps section of `plan/INTERVIEW_REQUIREMENTS.md`, which lists the real version — making a suite of red tests green — as still open |

### Recommendations declined

| Recommendation | Decision | Why |
|---|---|---|
| Merge **E3 + E4** ("your most over-drilled cluster relative to how often it decides an outcome") | **Declined** | `make check-coverage` requires each group numbered `1..n` with no gaps, so merging E3 and E4 renumbers E5–E34. That invalidates every deck card tag, every coverage row and every research reference to an E number. The cost is a repo-wide renumber; the benefit is two fewer cards in one cluster |
| Merge **T7 into T5** ("vocabulary rather than judgement; never appears standalone") | **Declined** | Same renumbering cost, smaller benefit |
| **Practise every kata twice — once with AI, then once cold, and only count the cold rep** | **Declined** | It contradicts the one rule this repo has. The rule is not "cold reps are what count", it is "AI does not write the things you get interviewed on" — and a first pass with AI means the design decisions were not yours to make cold the second time. Doing the rep twice yourself is strictly better and is what Saturday's adaptive slot is for |
| Re-scope **C12** as a target-gated LeetCode track rather than deferring it globally | **Accepted** — see the C12 row above | |

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
touching inside these fourteen weeks.
