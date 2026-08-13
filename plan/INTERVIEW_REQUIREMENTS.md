# Interview requirements

Everything the research found, plus the complete list of what you have to be able to do before
sitting an embedded or test-and-integration interview. **This file is the specification.** Every
other file in this repo exists to satisfy some part of it.

Capabilities are numbered so `plan/COVERAGE.md` can point at them, `tools/progress.py` can score
them, and you can tick them off. Six groups:

- **C**n — C language and syntax fluency
- **Y**n — Python fluency
- **E**n — Embedded concepts
- **H**n — Hardware, signals, and debugging
- **T**n — Test and integration
- **B**n — Behavioural and narrative

The count is not written down here on purpose — `make progress` reports it, and
`make check-coverage` proves this file and `plan/COVERAGE.md` describe exactly the same set,
each group numbered from 1 with no gaps. A number in prose is a number that goes stale.

**On the research below.** It was gathered from public candidate reports — Glassdoor, Blind,
engineering blogs — in **August 2026**. Read every company-specific claim as "candidates have
reported", not as policy. Interview processes change without announcement, and §6 says more about
how much to trust each part.

The first pass carried no citations. **Two later passes do**, and they are committed in
[`research/`](../research/) — each with a source table giving URL, source type, date, companies
covered, and a per-source reliability grade, plus an explicit "what I couldn't find" section. Where
this document and a report disagree, the report is newer and says so in its own §1. Anything in
Part I marked as confirmed, corrected or downgraded below traces to one of those files.

---

# PART I — WHAT THE RESEARCH FOUND

## 1. The two interview shapes

### Embedded / firmware engineer

Four stages is typical at hardware companies:

1. **Recruiter screen**, ~30 min. Motivation, resume, logistics. Low technical bar.
2. **Technical screen or take-home.** This is where firmware diverges from web. Tesla's is a
   ~2-hour take-home covering state machines, SPI/UART, bit masking, and debugging existing code
   — explicitly described by candidates as "not LeetCode." SpaceX runs a 4-hour programming test
   with automated tests attached; candidates report finishing in about two.
3. **Hiring manager call**, ~45 min. Concepts, plus a deep dive on one project you took to
   completion.
4. **Onsite loop.** SpaceX's includes a candidate-given presentation, a factory tour, and around
   four technical interviews. A reported Google embedded loop was: two general programming, one
   embedded programming, one embedded system design, one behavioural.

**Where candidates get rejected:** the live coding round, on syntax execution under observation.
One firmware engineer with ten years of shipped product was rejected and told he "didn't know
how to code" because he had never practised interview-style coding. That is the exact failure
mode this repo exists to prevent.

### Test & integration engineer

Three to five rounds, three weeks to two months end to end.

- **Intuitive Surgical:** recruiter → hiring manager project walkthrough → senior engineer
  walkthrough → analysis challenge → panel. Coding in C# and Python.
- **Medtronic:** around two rounds, mostly behavioural and resume-driven, ~3 weeks. Sometimes a
  four-person panel.
- **Stryker:** around six rounds over ~2 months, including a Gallup strengths interview that acts
  as a filter separate from technical merit.
- **Rocket Lab:** 45-minute virtual panel plus a 10-minute project presentation. Candidates report
  the focus was on understanding their technical contributions rather than algorithm questions.
- **Kraken Robotics:** HR pre-screen → behavioural with hiring manager and team → **6-hour
  take-home** with a technical writing portion and a programming/design portion → follow-up
  interview on the assessment.

**Where candidates get rejected:**

1. The behavioural round, more than the technical one — repeatedly at Medtronic and Stryker.
2. The project deep-dive. **The resume walkthrough is the technical screen.** Candidates who
   can't explain how they tested their own past work fail here.
3. Open-ended "how would you test this" questions — by proposing solutions before asking for
   requirements, or by stopping after the happy path.
4. Process attrition. Two-month pipelines cause drop-off.

## 2. The coding format question, settled

**Does LeetCode-style DSA appear?**

- **At FAANG-scale embedded teams: partially.** The hiring pipeline is shared with general
  software engineering, so whether you get algorithm questions depends on whether your
  interviewer is from the embedded team. Even there the subset is arrays, strings, linked lists,
  stacks and queues, and bit manipulation — not trees, graphs, or dynamic programming.
- **At small and mid-size hardware companies: mostly no.** Rocket Lab candidates report
  interviewers focused on technical contribution and thought process rather than algorithmic
  coding.

**What replaces it:** embedded-domain coding. Ring buffer, state machine, `memcpy`, endianness
swap, debouncer, a driver function. Plus C-language trap questions and project deep-dives.

**Formats:** live coding is common in embedded and lighter in T&I. Take-homes are common and
frequently decisive. Whiteboard and on-paper still appear for C traps and "draw the state
machine."

**Languages:** C dominates embedded. Python dominates test and integration. C++ shows up in
robotics, automotive and anywhere with a real application layer on top of the firmware; Rust is
still rare in job requirements and mostly appears as a nice-to-have. Neither is in scope here.

**AI in take-homes:** take-homes increasingly ship with automated test suites (SpaceX) and a
follow-up interview where you defend the solution live (Kraken, Tesla). Assume you will have to
reproduce and extend it under observation. Submitting work you can't explain is the fastest way
to fail the follow-up.

## 3. Non-code questions

Confirmed present, especially at hardware companies and for test roles:

- **Scope and logic analyzer interpretation.** "Intermittent RS-485 dropouts — find it."
- **Schematic reading.** Components, symbols, Ohm's law, pull-ups, common logic voltages.
- **Datasheet comprehension.** Some firmware test job descriptions require it explicitly.
- **Physics and math.** Nyquist and aliasing, fixed-point arithmetic; link budgets at RF firms.
- **Bench and practical.** Qualcomm hardware test runs six rounds asking what to test, how, and
  what an unexpected result means. Medtronic showed candidates the production floor. A full
  soldering practical during the interview is less commonly reported but possible.

## 4. How a web-to-embedded background gets read

Three objections recur, and each has a concrete answer:

| Objection | What overcomes it |
|---|---|
| "Web grad, never touched hardware, will be scared of a scope" | Bare-metal work, a logic-analyzer capture in the portfolio, register-level code |
| "Lives in frameworks, can't write tight C or reason about memory" | Register-level C on GitHub, a from-scratch ring buffer, fluent live answers on volatile and pointers |
| "Will get bored and leave for web" | A credible, specific reason for working on hardware |

**What helps, and the part of this that was wrong.** Docker, CI/CD and framework design map
directly onto firmware test automation and HIL infrastructure, and they transfer cleanly. The
original version of this section said the same of Python. **A second research pass found that
half wrong, and it is the half that matters:** Tesla schedules a standalone 90-minute Python
assessment for QA and test roles, Qualcomm runs a live round on decorators, lambda and
map/filter/reduce, and a candidate reported being cut in round two on a written Python exam.
Framework thinking transfers. Live syntax under observation does not. That finding is why the
**Y** group exists and why Python is drilled from week 1 rather than week 7.

**What hurts:** a resume reading as pure web/SaaS with no low-level signal, and leading with
"LLM integration," which reads as prompt engineering unless it sits under systems depth.

**Domain background** outside software is worth naming where it is relevant — for medical
devices, human-factors and usability testing is a regulated activity under IEC 62366, and being
able to reason about the system a device attaches to or measures is a real differentiator.

## 5. Timeline

**Realistic:** 6–12 months of consistent work to be genuinely competitive for junior roles, with
test & integration the faster door.

The second research pass corrected *why* it is the faster door, and the correction matters: not
because Python transfers — it half does, see §4 — but because **the live-Python bar is lower in
regulated medical and the process vocabulary is learnable in weeks rather than months.** That
splits the target list in two, and the two halves reward different preparation:

- **Camp A — software-heavy hardware firms** (Tesla, SpaceX, Qualcomm, Rocket Lab). These test
  raw Python live and hard. Y1 and Y3 are the gate; a 90-minute assessment decides it.
- **Camp B — regulated medical** (Medtronic, Intuitive, Abbott, Stryker). Weight shifts to
  process, traceability and framework vocabulary: IEC 62304, ISO 13485, IQ/OQ/PQ, GAMP 5. T26 is
  the gate, and the behavioural round rejects more people than the technical one.

## 5b. A gate that has nothing to do with how well you interview

**Several companies named throughout this document cannot hire you regardless of the outcome of
any interview.** ITAR and EAR restrict a large share of US defence, space and aerospace work to
"U.S. Persons" — citizens and lawful permanent residents. Both research passes found this
independently:

- **Rocket Lab's own posting states US citizenship is required.**
- The same gate covers **Anduril**, and large parts of **SpaceX**, **Blue Origin** and
  **Northrop Grumman**.

This document names SpaceX repeatedly as a target, and B10's "tested by" column says "Rocket Lab,
SpaceX", because the first research pass gathered evidence without regard to eligibility. **Read
every company name here as an example of a format, not as a shortlist.** The formats are real and
the questions are real; whether you can take the job is a separate question, and this repo does
not answer it.

Where that leaves the practice is nowhere, deliberately — nothing below changes. A ring buffer is
a ring buffer. Where it does land is the applications file, which `.gitignore` reserves at
`plan/APPLICATIONS.md`, and which is the right place for eligibility, sequencing and the go/no-go
threshold the research proposed: **if after 20 logged reps you are below 15/20 on Y3, do not yet
apply to the Camp A live-Python roles — prioritise Camp B instead.** That threshold is checkable
against `make report`, which is why it is worth writing down somewhere you will see it.

## 6. Evidence quality

- Embedded interview reporting is abundant and consistent. T&I reporting is thinner, and many
  "top 30 test engineer questions" pages are AI-generated SEO filler — used here for themes only,
  with Glassdoor and Blind prioritised for anything specific.
- Company specifics can be stale or role-mismatched. Several MDA reports describe web/frontend
  roles rather than firmware.
- The DSA-at-FAANG question is genuinely contested. The variance is real and interviewer-dependent.

---

# PART II — THE MASTER CHECKLIST

What you must be able to do. Each item states the capability, how it gets tested, and the
evidence bar that counts as proof. `plan/COVERAGE.md` says who owns each one.

## C — C language and syntax fluency

| ID | I can... | Tested by | Evidence bar |
|---|---|---|---|
| C1 | Write C from a blank editor without stalling on syntax | Live coding | 70%+ clean-first-compile rate over 20 logged reps |
| C2 | Declare and reason about pointers, pointer-to-pointer, arrays decaying, function pointers | Live coding, whiteboard | Written cold, no reference |
| C3 | Write `strlen`, `strcpy`, `strncpy`, `strcmp` correctly at every boundary | Whiteboard | Passing frozen tests, ASan clean |
| C4 | Write `memset`, `memcpy`, `memmove`, and say why `memmove` exists | Whiteboard | Both overlap directions correct |
| C5 | Write a ring buffer, any variant, in under 15 minutes | Live coding | Logged time under target, three consecutive clean reps |
| C6 | Do bit manipulation cold: set/clear/toggle/test, count bits, extract fields, build masks | Whiteboard | No signed-shift bugs, `1u` every time |
| C7 | Byte-swap and read big-endian values out of a buffer portably | Whiteboard | No pointer-cast aliasing violations |
| C8 | Predict `sizeof` for a struct and reorder members to shrink it | Verbal + code | Verified with `offsetof` and `_Static_assert` |
| C9 | Write a fixed-block pool allocator with the free list threaded through free blocks | Live coding | Alignment correct, exhaustion handled, double-free detected |
| C10 | Do fixed-point arithmetic: Q notation, multiply, divide, rounding, overflow | Code | Q16.16 operations correct |
| C11 | Handle unsigned timer rollover correctly | Code | Correct across the wrap, not `if (now > next)` |
| C12 | Write the ten linked-list and array problems that recur in embedded screens | Live coding | In C, not Python |

## Y — Python fluency

The T&I track's live-coding group, and the one this repo was originally wrong about. The earlier
research assumed Python transferred wholesale from web work and scheduled it from week 7. It
half-transfers: framework design, Docker and CI carry over cleanly, and raw syntax under
observation does not. Tesla schedules a standalone 90-minute Python assessment for QA and test
roles; Qualcomm runs a live round on decorators, lambda and map/filter/reduce. This group is to
Python what C1–C12 are to C, and it is drilled from week 1 for the same reason.

| ID | I can... | Tested by | Evidence bar |
|---|---|---|---|
| Y1 | Explain Python's trap-level internals — mutable default arguments, `is` vs `==` and the small-int cache, generators vs lists, closure late binding, the GIL for CPU- vs I/O-bound work, `functools.wraps`, context managers, shallow vs deep copy — **and predict the output of an unseen snippet cold** | Live rapid-fire "what does this print and why" | Every tagged card in box 4+, including the snippet cards, said aloud with the trap named — no interpreter, no reference |
| Y2 | Parse and build binary telemetry on the host: correct `struct` format and endianness, length validated before unpacking, signed vs unsigned, frames reassembled across read boundaries | Take-home, live decode-this-packet | Three consecutive clean reps at target, three variants |
| Y3 | Write domain scripting under time pressure: stream-parse a file larger than RAM, reduce it, and exit with the right code — without loading it all | Live coding, take-home | Three consecutive clean reps at target, three variants |

## E — Embedded concepts (verbal)

| ID | I can explain... | Tested by | Evidence bar |
|---|---|---|---|
| E1 | `volatile`: what it does and that it is **not** atomicity | Verbal, always asked | Said aloud with the trap named |
| E2 | `static`: lifetime vs linkage, and that static locals are in `.data`/`.bss` not the stack | Verbal | Trap named |
| E3 | `const`, `const volatile`, and all four const/volatile pointer combinations | Verbal + write it | Canonical MMIO declaration from memory |
| E4 | Where a `const` table lives on an MCU and why that matters | Verbal | — |
| E5 | Stack vs heap in constrained memory, and why `malloc` is avoided | Verbal | Names fragmentation and non-determinism |
| E6 | Stack direction, stack sizing, and high-water-mark measurement | Verbal | — |
| E7 | What runs before `main()` | Verbal | Names `.data` copy and `.bss` zeroing |
| E8 | Struct padding and alignment, and `#pragma pack` trade-offs | Verbal | — |
| E9 | What you must never do in an ISR, **and why** | Verbal, always asked | Reasons given, not just the list |
| E10 | ISR-to-main data sharing, and where `volatile` alone is insufficient | Verbal | — |
| E11 | Interrupt latency, what worsens it, and nested interrupts | Verbal | — |
| E12 | Mutex vs semaphore — ownership, priority inheritance, ISR usage | Verbal, high-frequency filter | **Must name the classic wrong answer** |
| E13 | Priority inversion with a concrete three-task example, and both fixes | Verbal | Medium-priority task included or it's wrong |
| E14 | The four deadlock conditions and how to break one | Verbal | — |
| E15 | Race condition vs data race | Verbal | — |
| E16 | Why `volatile` doesn't fix a shared counter | Verbal | — |
| E17 | Preemptive vs cooperative scheduling, tasks, ticks | Verbal | — |
| E18 | UART vs SPI vs I2C vs CAN — wires, duplex, addressing, topology, speed | Verbal, 90 seconds | SPI has no addressing; I2C needs pull-ups |
| E19 | I2C pull-ups, open-drain, clock stretching | Verbal | — |
| E20 | SPI modes, CPOL and CPHA | Verbal | — |
| E21 | CRC: what it catches, what it isn't | Verbal | Not a hash, not correction |
| E22 | DMA and its failure modes | Verbal | Cache coherency, buffer ownership |
| E23 | State machine patterns: switch, table-driven, function-pointer, and when each | Verbal + code | — |
| E24 | Debouncing approaches and non-blocking timing | Verbal + code | — |
| E25 | Watchdog design done correctly | Verbal | Not kicked from a timer ISR |
| E26 | What a linker script does, and read a `.map` file to see where code and data landed | Verbal | Names which sections live in flash and which in RAM |
| E27 | Field firmware update: A/B partitions, integrity check, rollback | Verbal | Handles power loss mid-update |
| E28 | MCU low-power modes, wake sources, and how you'd measure real current draw | Verbal | Says what stops running in each mode |
| E29 | Choose bare-metal super-loop vs RTOS, and name the concrete costs an RTOS adds | Verbal, asked directly | Three specific costs, with a worked example each way |
| E30 | **Architect an embedded subsystem out loud in 45 minutes**: ISR vs main, RAM/flash budget, comms topology, power states, failure handling, testability | The dedicated design round (Google, Meta RL), and design items inside Tesla and Medtronic take-homes | Three prompts, each scored against the fixed rubric, each surviving one round of pushback |
| E31 | Design a firmware update and bootloader path: A/B partitions, signed image, anti-rollback, power-loss safety | Standalone design prompt | Drawn from memory, with the power-loss failure point named at each step |
| E32 | Explain functional safety — ISO 26262 ASIL, DO-178C DAL, IEC 61508 — and how an integrity level drives coverage up to MC/DC | Automotive and aerospace loops | Said aloud with the trap named |
| E33 | Explain embedded cybersecurity: secure boot vs encryption, root of trust, signed updates, and the §524B premarket requirement | Folded into the update-design question for connected medical | Authenticity vs confidentiality stated cold |
| E34 | Debug a hard fault: fault status registers, the stacked frame, the faulting PC, stack overflow vs wild pointer | Debugging scenario | Said aloud with the trap named |

## H — Hardware, signals, and debugging

| ID | I can... | Tested by | Evidence bar |
|---|---|---|---|
| H1 | Debug intermittent comms methodically, starting with power and clocks | Verbal scenario | Doesn't start with the code |
| H2 | Choose scope vs logic analyzer and say why | Verbal | — |
| H3 | Read and interpret a captured waveform against datasheet timing | Shown a capture | Own captures in the portfolio |
| H4 | Read a schematic: components, symbols, pull-ups, logic levels | Shown a schematic | — |
| H5 | Find an answer in a datasheet under time pressure | "Here's a datasheet" | — |
| H6 | Apply Ohm's law and basic power/current reasoning | Verbal | — |
| H7 | Explain Nyquist, aliasing, and anti-alias filtering | Verbal | Aliasing is irreversible |
| H8 | Explain what a pull-up resistor does and what floating causes | Verbal | — |
| H9 | Explain JTAG vs SWD and what a debugger actually does | Verbal | — |
| H10 | Use a multimeter and a logic analyzer competently at a bench | Practical, possible | — |
| H11 | Reason about cache coherency and memory barriers with DMA: why the CPU reads stale data and what fixes it | The stock "DMA completed but data is stale" scenario | Invalidate-before-read and clean-before-DMA stated cold |

## T — Test and integration

| ID | I can... | Tested by | Evidence bar |
|---|---|---|---|
| T1 | Generate 25+ test cases across 8 categories for an unfamiliar object in 10 minutes | The core T&I question | Rubric score 12+/16, requirements asked first |
| T2 | Distinguish verification from validation without blurring them | Verbal | Trap named |
| T3 | Explain requirements traceability and why auditors want it | Verbal | Links tests to requirements and to risk |
| T4 | State IEC 62304 classes A/B/C and the default | Verbal | Knows the default is C |
| T5 | Walk the test lifecycle from requirements to coverage report | Verbal | — |
| T6 | Do impact analysis on a mid-project change request | Verbal | — |
| T7 | Distinguish smoke, sanity, regression, acceptance | Verbal | — |
| T8 | Write a defect report with severity separate from priority | Written | — |
| T9 | Debug a "some sites fail, others don't" problem by isolating differences | Verbal scenario | One variable at a time |
| T10 | Distinguish fixture, harness, and HIL rig | Verbal | — |
| T11 | Explain test flakiness causes and fixes | Verbal | Not "add retries" |
| T12 | Say when **not** to automate | Verbal | — |
| T13 | Write pytest: discovery, assertions, exit codes | Take-home, live | 20 tests on a pure function |
| T14 | Use fixtures with correct scope and teardown that survives failure | Take-home | — |
| T15 | Use `parametrize` and explain why it beats copies | Take-home | — |
| T16 | Build a device abstraction testable against both a fake and real hardware | Portfolio | Same tests, both transports |
| T17 | Drive real hardware over serial: pyserial, timeouts, framing, port discovery | Portfolio | Discovery by USB serial number |
| T18 | Inject faults: truncated frames, bad CRC, impossible lengths, and assert recovery | Portfolio | — |
| T19 | Run tests against real hardware in CI | Portfolio | Green CI run, screenshot |
| T20 | Write Bash for test scripting and device wrangling | Take-home | — |
| T21 | Trace each test to a requirement | Portfolio | Requirement IDs in test names or markers |
| T22 | Test firmware C on the host: build the logic without hardware and fake what it talks to | Take-home, portfolio | Names the seam the fake goes at |
| T23 | Explain static analysis and coding standards (MISRA-C): what they catch and what they don't | Verbal | Not "it finds the bugs for you" |
| T24 | Drive lab instruments from Python over SCPI and PyVISA — scopes, supplies, SMUs — with error-queue checking and results logged against firmware version | Hardware and HIL test rounds | An instrument driver in the harness repo with timeout and error handling |
| T25 | Explain measurement quality: calibration intervals and traceability, measurement uncertainty, out-of-tolerance handling, Gauge R&R | Probed in hardware-test rounds and by auditor-adjacent questions | Said aloud: why an uncalibrated rig invalidates recorded results |
| T26 | Execute and document regulated computerised-system validation: IQ, OQ and PQ protocols, GAMP 5 risk-based validation, 21 CFR Part 11 | Scenario questions at Medtronic, Abbott, Intuitive | One drafted OQ protocol with pass/fail criteria traced to a named requirement |
| T27 | Read and modify a C#/.NET test harness well enough to be productive on manufacturing-test code | Skills screen and code reading at Intuitive and Medtronic manufacturing | Deferred — see `plan/COVERAGE.md` |
| T28 | Reduce and visualise test data — rolling statistics, pass/fail bands, a plot — and turn a raw capture into a written engineering conclusion | Project deep-dives at Rocket Lab and Blue Origin | A raw capture turned into a summary, one plot and a written verdict |

## B — Behavioural and narrative

| ID | I can... | Tested by | Evidence bar |
|---|---|---|---|
| B1 | Answer "why hardware, coming from web?" convincingly | Every interview | Rehearsed, specific, not generic |
| B2 | Answer "why this domain — space/subsea/medical?" | Every interview | — |
| B3 | Walk a project end to end: what, why that design, what you gave up | The technical screen in T&I | Structured as constraint → options → choice → trade-off |
| B4 | Explain **how I tested** each project | The T&I differentiator | Concrete, with artifacts |
| B5 | Tell a struggle-and-recovery story | Behavioural | STAR form |
| B6 | Tell a conflict-with-a-coworker story | Behavioural | — |
| B7 | Tell a pushed-back-on-skipping-a-test story | Behavioural, T&I favourite | — |
| B8 | Tell a "my tests caught a bug I'd have missed" story | Behavioural | Specific bug, specific test |
| B9 | Tell a "I was wrong about a root cause" story | Behavioural | — |
| B10 | Present a project in 10 minutes to a panel | Rocket Lab, SpaceX | Rehearsed, timed |
| B11 | Defend a from-scratch architecture decision under live pushback — hold a position, take a correction, revise in real time | The design round grades this behaviourally as much as technically | Three takes rated strong on three different days |

---

## Known gaps in this list

One thing the research says matters which nothing here measures, and two that are now covered.
Written down rather than added as capabilities, because a numbered capability with no mechanism
behind it is worse than an admitted hole:

- **Whiteboard and paper.** *Still open.* Reported for C traps and "draw the state machine". The
  only mechanism is one constraint card, drawn on roughly one rep in ten of the third that draw
  a card at all.
- **Debugging code you did not write.** *Now covered, by `make hunt`.* Tesla's take-home is
  reported to include "debugging existing code", and Intel runs a dedicated debug round. The
  problem was that a corpus of broken C would have to be written by a human under the AI rule —
  an AI-written bug is an AI-written exercise. `make hunt` sidesteps it: a machine mutates *your
  own* solution from an earlier rep, mechanically, and you find the change. Works in both
  languages, and the Python mutation set is chosen for the bugs that never raise — a flipped
  struct endianness prefix, `H` read as `h`.
- **Making a suite of red tests green.** *Still open.* `make hunt` finds one planted token in
  code you wrote. Take-homes increasingly ship with a full failing suite you have to satisfy —
  SpaceX's is described that way — which is a different exercise: you read someone else's
  intent out of their assertions rather than diffing against your own memory. Week 10's mock
  take-home is the only exposure and it is one day.
- **C++.** Scoped out at §2 and worth naming here rather than leaving in an aside: the research
  says Anduril prefers it, and Mimic gives volume in C++ rather than C. Out of scope is a
  decision, not an oversight, but it is a real edge of what these ten weeks buy.
- **Designing something from scratch.** *Now covered, by `make design`.* This was not on the
  original list at all and turned out to be a dedicated interview round. See E30.

## Scoring yourself

A capability is **done** when the evidence bar is met and logged — not when you feel you know it.

- **C items:** logged in `logs/log.tsv` via `make done`. Three consecutive clean reps at or under
  target across three different variants retires the kata. C1 is the exception: it is the
  clean-first-compile rate itself, across every **C** module, over at least twenty reps.
  Python reps are excluded from it — see the Y bullet.
- **Y items:** the same kata bar for Y2 and Y3, against `binary_frame_py` and `log_parser_py`.
  Y1 is the deck. "Clean" for a Python rep means it ran first try with no traceback — a
  different claim from clean-first-compile, which is why `make report` prints the two rates
  separately and neither is averaged into the other.
- **E items:** in box 4 or 5 of the deck via `make review`, meaning you've said it correctly
  across several spaced sessions including the trap. E30 is the exception: its bar is three
  scored architecture drills via `make design`.
- **H items:** a mix — some are deck cards, some need a real capture or bench session.
- **T items:** deck cards, the design-prompt rubric for T1, or artifacts in the harness repo.
  T27 is deferred by decision — see `plan/COVERAGE.md`.
- **B items:** written in STAR form, then three takes rated strong on three different days.
  B11 is a drill rather than a story: run it straight after `make design`, on the design you
  just wrote.

`plan/COVERAGE.md` says which system is responsible for getting you there, and `make progress`
scores it. A capability whose mechanism lives outside this repo is reported as *tracked
elsewhere* — which is not the same as done, and the report does not pretend otherwise.
