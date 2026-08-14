# embedded-training

A measured training system for embedded and test-and-integration engineering — built
from interview research, run as a daily practice, and scored against evidence rather
than against how much I feel I have learned.

Fourteen weeks. Fifteen katas in C and Python, a spoken deck, design prompts,
architecture drills, behavioural rehearsal, and one hardware-in-the-loop project.
Everything is timed and logged.

**[START_HERE.md](START_HERE.md)** explains how it fits together in five minutes.
**[DAILY.md](DAILY.md)** is the daily checklist: how to read a calendar line, and what
gets recorded at each end of a session.
**[reference/COMMANDS.md](reference/COMMANDS.md)** documents every command.
**[logs/PROGRESS.md](logs/PROGRESS.md)** is the current score.

---

## Why it is built this way

Interview research produced a list of **numbered capabilities** — concrete things you have to
be able to do, each with a stated bar for what counts as proof. They are written down in
[plan/INTERVIEW_REQUIREMENTS.md](plan/INTERVIEW_REQUIREMENTS.md), and every other file here
exists to satisfy some part of that list. `make progress` reports the current count and score;
no document restates the number, because a number in prose is a number that goes stale.

Two findings shaped the design:

- **Candidates get rejected in the live coding round on syntax execution under
  observation** — not on knowledge. One firmware engineer with ten years of shipped
  product was told he "didn't know how to code" because he had never practised
  interview-style coding. So the C work is drilled cold and timed, never reviewed.
- **Test-and-integration candidates fail the behavioural and project-walkthrough
  rounds more often than the technical one.** So concepts are rehearsed *out loud*,
  and "how would you test this" is its own repeating exercise with a fixed rubric.

Only the C and Y groups are katas. Drilling code and then failing the verbal round is the
failure mode this is built to avoid.

## Layout

```
plan/          the program: the research, the capability list, coverage, the calendar
practice/      the daily mechanics: katas, decks, design prompts, architecture, rehearsal
reference/     material to consult, not drill: question bank, commands, architecture
projects/      specs for the one-shot portfolio artifacts
tools/         the machinery behind the make targets
logs/          the record — the only place that decides whether this is working
```

| Directory | What is in it |
|---|---|
| **`plan/`** | `INTERVIEW_REQUIREMENTS.md` is the specification: the research plus every capability. `COVERAGE.md` maps each one to the mechanism that owns it. `CALENDAR.md` is all 98 days, generated. `CURRICULUM.md` is why the fourteen weeks are shaped as they are. `REPOS.md` is the disk layout. |
| **`practice/`** | `PRACTICE_SYSTEM.md` explains the seven formats and the rules for using AI. `katas/` holds eleven C modules and four Python ones. `decks/` holds the spoken deck as TSV, including the Python trap cards. `design-prompts/` holds 60 test subjects and 8 architecture prompts, each with its own fixed rubric. `rehearsal/` holds the behavioural stories. |
| **`reference/`** | `COMMANDS.md` documents every command. `ARCHITECTURE.md` covers repo internals. `question-bank/` holds 76 coding exercises, the verbal set with trap answers, and the T&I track. |
| **`projects/`** | `hil-harness/BRIEF.md` — the weeks 10–11 flagship spec. The project itself lives in its own public repo. |
| **`logs/`** | Every rep, every phase split, every story take, every AI use, and the generated progress report. |

## The kata mechanism

The unusual part, and the reason a solved kata stays practisable:

```
practice/katas/ring_buffer/
├── BRIEF.md      committed   what it is, the API, how to think about it, what to test
├── VARIANTS.md   committed   the variants the drill draws from (seven or more)
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

None of it is gated by the calendar. `make drill KATA=fsm` runs that module now, whatever the
day says; `make hunt` plants a single-token bug in one of your own older solutions and times you
finding it. `make help` lists everything and [DAILY.md](DAILY.md) explains what each line means.

| Day | Shape | Total |
|---|---|---|
| Mon, Thu, Fri | 15 C kata · **25 Python kata** · 55 main · 12 deck · 8 log | 115 min |
| Tue | 15 C kata · **15 C kata** · 65 main · 12 deck · 8 log | 115 min |
| Wed | 28 C kata · **25 Python kata** · 42 main · 12 deck · 8 log | 115 min |
| Sat | 28 kata (adaptive, either language) · 100 main · 10 rehearsal | 138 min |
| Sun | **two** 28-min katas · 20 review · 15 deck · 10 prompt · 30 rehearsal | 131 min |
| Sun, weeks 6/8/10/12 | the same, plus a 45-minute architecture drill | 176 min |

14.1 to 15.0 hours a week; weeks 1–5 are heavier — up to 16.4 — because they carry the
kata build sessions. 207 hours over the fourteen weeks.
The generated calendar prints the real figures. Every kata block is at least as long as that
kata's target time, and CI fails if that stops being true.

Saturday's rep is the only one with no assigned module — `make drill` with no arguments picks
the worst recent time, so one day a week catches whatever is being avoided. It is also the only
slack in the rotation.

## How progress is measured

`make progress` scores every capability and writes [logs/PROGRESS.md](logs/PROGRESS.md) plus a
machine-readable `logs/progress.json`. Nothing in it is a rating of how well something is
known — a capability is met when its evidence bar is met and logged. The kata and rubric bars
are measured by a clock, a compiler and a score out of 16; the deck bar is graded by you, one
card at a time, spaced out far enough that a single generous `y` cannot carry it.
[plan/COVERAGE.md](plan/COVERAGE.md) says which bars are which, and what none of them can do.

| Group | Bar |
|---|---|
| **C** — C fluency | Three consecutive clean reps at or under target, across three variants. C1 is the clean-first-compile rate itself, over 20+ reps — C modules only |
| **Y** — Python fluency | The same kata bar for Y2 and Y3. Y1 is the deck. "Clean" for a Python rep means it ran first try with no traceback, and is reported apart from C |
| **E** — concepts | 80% of its deck cards in Leitner box 4 or higher (all of them, below three cards), said aloud with the trap |
| **T** — test & integration | Deck boxes, the design-prompt rubric for T1, or artifacts in the harness repo |
| **B** — behavioural | Three takes rated strong, on three different days |
| **H** — hardware | Deck boxes, or bench evidence — reported as tracked outside this repo, which is not the same as done |

## Verification

`make test` builds under `-Werror` with AddressSanitizer and UndefinedBehaviorSanitizer
(`-fno-sanitize-recover=all`, so undefined behaviour aborts instead of printing and
exiting 0). `concurrency_sim` builds under ThreadSanitizer instead, since the two cannot
coexist.

One compiler at a time: `make test` uses gcc, and `make test CC=clang` is a manual second
opinion worth taking when something looks wrong. CI does not run `make test` at all — `src/`
is gitignored, so there is nothing to link — and it is `make check-frozen` that runs on both
compilers, because the frozen headers and suites are the artifacts that have to stay valid.

Seven checks run in CI on every push, and `make check` runs all of them locally:

| Check | Proves |
|---|---|
| `make check-frozen` | Every frozen C header and test suite still compiles, gcc and clang |
| `make check-frozen-py` | Every frozen Python suite still imports and collects, against a stand-in for the implementation it cannot have |
| `make check-log` | The practice log is well formed |
| `make check-calendar` | Schedule, derived build plan, timer blocks and retirement feasibility agree |
| `make check-coverage` | The spec and the coverage map describe exactly the same capabilities |
| `make check-decks` | Every deck tag names a real capability, and nothing scored by the deck lacks a card |
| `make check-generated` | The generated files still match their generators |

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
eight weeks — is a separate repo. This one *schedules* those hours and *tracks what they
cover* so the two do not duplicate each other, but contains none of it. The HIL
harness gets its own public repo when it is built. See
[plan/REPOS.md](plan/REPOS.md).
