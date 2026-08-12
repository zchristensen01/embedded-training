# embedded-training

A measured training system for embedded and test-and-integration engineering — built
from interview research, run as a daily practice, and scored against evidence rather
than against how much I feel I have learned.

Ten weeks. Twelve C katas, a 56-card spoken deck, design prompts, behavioural
rehearsal, and one hardware-in-the-loop project. Everything is timed and logged.

**[START_HERE.md](START_HERE.md)** explains how it fits together in five minutes.
**[reference/COMMANDS.md](reference/COMMANDS.md)** documents every command.
**[logs/PROGRESS.md](logs/PROGRESS.md)** is the current score.

---

## Why it is built this way

Interview research produced **78 numbered capabilities** — concrete things you have to
be able to do, each with a stated bar for what counts as proof. They are written down
in [plan/INTERVIEW_REQUIREMENTS.md](plan/INTERVIEW_REQUIREMENTS.md), and every other
file here exists to satisfy some part of that list.

Two findings shaped the design:

- **Candidates get rejected in the live coding round on syntax execution under
  observation** — not on knowledge. One firmware engineer with ten years of shipped
  product was told he "didn't know how to code" because he had never practised
  interview-style coding. So the C work is drilled cold and timed, never reviewed.
- **Test-and-integration candidates fail the behavioural and project-walkthrough
  rounds more often than the technical one.** So concepts are rehearsed *out loud*,
  and "how would you test this" is its own repeating exercise with a fixed rubric.

Only 12 of the 78 capabilities are katas. Drilling code and then failing the verbal
round is the failure mode this is built to avoid.

## Layout

```
plan/          the program: the research, the capability list, coverage, the calendar
practice/      the daily mechanics: katas, decks, design prompts, rehearsal
reference/     material to consult, not drill: question bank, commands, architecture
projects/      specs for the one-shot portfolio artifacts
tools/         the machinery behind the make targets
logs/          the record — the only place that decides whether this is working
```

| Directory | What is in it |
|---|---|
| **`plan/`** | `INTERVIEW_REQUIREMENTS.md` is the specification: the research plus all 78 capabilities. `COVERAGE.md` maps each one to the mechanism that owns it. `CALENDAR.md` is all 70 days, generated. `CURRICULUM.md` is the week-by-week shape. `REPOS.md` is the disk layout. |
| **`practice/`** | `PRACTICE_SYSTEM.md` explains the four repeatable formats and the rules for using AI. `katas/` holds twelve C modules. `decks/` holds 56 cards as TSV. `design-prompts/` holds 40 subjects and the fixed rubric. `rehearsal/` holds the ten behavioural stories. |
| **`reference/`** | `COMMANDS.md` documents every command. `ARCHITECTURE.md` covers repo internals. `question-bank/` holds 76 coding exercises, the verbal set with trap answers, and the T&I track. |
| **`projects/`** | `hil-harness/BRIEF.md` — the week 8 flagship spec. The project itself lives in its own public repo. |
| **`logs/`** | Every rep, every phase split, every story take, every AI use, and the generated progress report. |

## The kata mechanism

The unusual part, and the reason a solved kata stays practisable:

```
practice/katas/ring_buffer/
├── BRIEF.md      committed   what it is, the API, how to think about it, what to test
├── VARIANTS.md   committed   seven variants the drill draws from
├── NOTES.md      committed   one decision or bug per rep
├── include/      committed   the API contract.  FROZEN during a rep
├── tests/        committed   the test suite.    FROZEN during a rep
└── src/          GITIGNORED  the implementation. DELETED at the start of every rep
```

`make drill` deletes `src/`, writes an empty stub, and starts a clock. Every rep is a
genuine cold start because the previous solution does not exist. The expensive
artifacts — the contract and the tests — are permanent and version-controlled. The
implementation is disposable.

What accumulates across reps is the lesson and the time, not the code.

## The daily loop

```bash
make today            # what to do right now
make drill            # start a rep — wipes src/, starts the clock
    make lap          # at each transition: design -> write -> compile -> debug
make test             # build + run the frozen suite under sanitizers
make done             # stop the clock, log the rep
make review           # deck pass, ANSWER OUT LOUD
```

| Day | Shape | Total |
|---|---|---|
| Mon, Tue, Thu, Fri | 10 kata (short) · 60 main · 12 deck · 8 log | 90 min |
| Wed | 25 kata (long) · 45 main · 12 deck · 8 log | 90 min |
| Sat | 10 kata (adaptive) · 120 main | 130 min |
| Sun | 25 kata · 20 review · 15 deck · 10 prompt · 10 rehearsal | 80 min |

About 11 hours a week. Saturday's rep is the only one with no assigned module —
`make drill` with no arguments picks the worst recent time, so one day a week catches
whatever is being avoided.

## How progress is measured

`make progress` scores all 78 capabilities and writes
[logs/PROGRESS.md](logs/PROGRESS.md) plus a machine-readable `logs/progress.json`.
Nothing in it is self-assessed. A capability is met when its evidence bar is met and
logged:

| Group | Bar |
|---|---|
| **C** — C fluency | Three clean reps at or under target time, across three different variants |
| **E** — concepts | Every tagged deck card in Leitner box 4 or higher, said aloud with the trap |
| **T** — test & integration | Deck boxes, or artifacts in the harness repo |
| **B** — behavioural | Three rated takes of that story |
| **H** — hardware | Bench evidence, reported as proved outside this repo |

## Verification

`make test` builds under `-Werror` with AddressSanitizer and UndefinedBehaviorSanitizer
(`-fno-sanitize-recover=all`, so undefined behaviour aborts instead of printing and
exiting 0), on both gcc and clang. `concurrency_sim` builds under ThreadSanitizer
instead, since the two cannot coexist.

Four checks run in CI on every push:

| Check | Proves |
|---|---|
| `make check-frozen` | Every frozen header and test suite still compiles, gcc and clang |
| `make check-log` | The practice log is well formed |
| `make check-calendar` | The schedule and the derived build plan agree |
| `make check-coverage` | Every one of the 78 capabilities has a mechanism |

CI deliberately does not run the katas. `src/` is gitignored and deleted every rep, so
there is nothing to link — what CI protects is the artifacts that are meant to be
permanent.

## The rule about AI

> AI writes infrastructure. I write everything that gets interviewed.

AI may write Makefiles, CI config, the tooling in `tools/`, and test runners. It may
not write a single test case, any kata implementation, or any project code. "How would
you test this" is a top-three interview question in both tracks; outsourcing the test
suite would mean outsourcing the thing being practised. Every use is logged in
`logs/ai-use.tsv`.

## What is not in here

Mimic — a robot arm project that runs alongside this as the main block for the first
six weeks — is a separate repo. This one *schedules* those hours and *tracks what they
cover* so the two do not duplicate each other, but contains none of it. The HIL
harness gets its own public repo when it is built. See
[plan/REPOS.md](plan/REPOS.md).
