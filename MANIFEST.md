# Manifest

Every file, what it's for, whether you edit it.

## Root

| File | What it is | Edit? |
|---|---|---|
| `README.md` | Front page: what this is, why it's built this way, the layout | No |
| `START_HERE.md` | **Read this first.** How the whole system fits together, in five minutes | No |
| `SETUP.md` | Day 0 and the staged kata build order. **Start here** | No |
| `DAILY.md` | What a calendar line means, the session checklist, and how to practise off-plan | No |
| `MANIFEST.md` | This file | No |
| `Makefile` | The command interface. Put your build rules under `test:` | **Yes** |
| `.gitignore` | Contains `practice/katas/*/src/` — the line that makes reps repeatable | Rarely |

## `plan/` — the program. Read once, then follow the calendar.

| File | What it is | Edit? |
|---|---|---|
| `INTERVIEW_REQUIREMENTS.md` | The research findings + every numbered capability. The spec | No |
| `COVERAGE.md` | Who owns each capability — Mimic vs a mechanism in here | No |
| `CALENDAR.md` | All 70 days: timers, katas, main blocks. Relative labels, committed | `make calendar` |
| `CALENDAR.dated.md` | The same 70 days with your real dates. **Gitignored** | `make dates` |
| `CURRICULUM.md` | Why the ten weeks are shaped this way, and the week 6 gate | No |
| `REPOS.md` | The three-repo layout on disk, naming, what `mimic-hil` is | No |

## `practice/` — the daily mechanics

| Path | What it is | Edit? |
|---|---|---|
| `PRACTICE_SYSTEM.md` | Seven formats, variants, constraint cards, AI rules, measurement | No |
| `katas/README.md` | The fifteen-module map and target times | No |
| `katas/<name>/BRIEF.md` | What it is, the API, how to think about it, what to test | Once, when building |
| `katas/<name>/VARIANTS.md` | The variants `make drill` draws from | Add over time |
| `katas/<name>/NOTES.md` | One decision or bug per rep | `make done` appends |
| `katas/<name>/include/*.h` | The API contract. **Frozen during a rep** | Once, when building |
| `katas/<name>/tests/*` | The suite. **Frozen during a rep. You write every case** | Once, when building |
| `katas/<name>/src/` | Your implementation. **Gitignored, deleted every rep** | Every rep |
| `decks/embedded.tsv` | `topic <TAB> question <TAB> answer <TAB> trap <TAB> caps` | `make card` |
| `decks/test-integration.tsv` | Same format, the T&I half of the deck | `make card` |
| `decks/python.tsv` | Same format, the Python fluency deck — the Y group's bar | `make card` |
| `design-prompts/SUBJECTS.md` | 40 "how would you test X" subjects + the fixed 8-category rubric | No |
| `design-prompts/ARCHITECTURE.md` | 8 "design this subsystem" prompts + a different 8-axis rubric | No |
| `rehearsal/README.md` | How takes work, what "ready" means | No |
| `rehearsal/STORIES.md` | The behavioural stories | **Yes — fill before your first take** |

**All fifteen katas ship with `BRIEF.md` and `VARIANTS.md` written.** For every one of them you
owe exactly two things: the API header and the test suite. `make newkata NAME=x` scaffolds the
directories and a test runner; the cases are yours. Which to build when is derived from the
rotation — `make check-calendar` prints it.

## `reference/` — consult, don't drill

| File | What it is |
|---|---|
| `question-bank/README.md` | Topic-to-kata map, why the six added katas exist |
| `question-bank/embedded-coding.md` | 76 coding exercises by theme and kata |
| `question-bank/embedded-concepts.md` | Verbal questions, strong answers, **and the trap answers** |
| `question-bank/test-integration.md` | The T&I track: coding, conceptual, process, behavioural |
| `COMMANDS.md` | Every command, what it does, and what it writes |
| `ARCHITECTURE.md` | Repo internals and the gitignore trick |

## `projects/` — one-shot artifacts

| File | What it is |
|---|---|
| `hil-harness/BRIEF.md` | Week 8 flagship spec: acceptance criteria for T16–T21, structure, build order |

The project itself lives in its own repo, `~/embedded/mimic-hil`. This is only the spec.

## `tools/`

| File | What it does |
|---|---|
| `drill.py` | Kata reps: select, wipe `src/`, time, phase splits, log |
| `review.py` | Leitner spaced repetition over the decks |
| `rehearse.py` | Behavioural takes: draw, time, rate, log |
| `prompt.py` | Draws a design prompt, opens a rubric-scored answer file |
| `design.py` | Draws an architecture prompt, times 45 min, opens a rubric-scored answer file |
| `report.py` | Time curve, clean-compile rate, phase breakdown, coverage |
| `progress.py` | Scores every capability, writes `logs/PROGRESS.md` and `progress.json` |
| `card.py` | Adds a deck card in ~20s. `make card`, and offered at the end of `make done` |
| `schedule.py` | Generates `plan/CALENDAR.md` (named `schedule` to avoid shadowing stdlib `calendar`) |
| `newkata.py` | Scaffolds a kata module |
| `bughunt.py` | Plants one mutation in an old solution of yours, and times you finding it |
| `today.py` | Prints today's assignment, entirely from `schedule.py` |
| `check_log.py` | Validates `logs/log.tsv` against the schema `make done` writes. CI runs it |
| `check_decks.py` | Validates every deck tag against the capability list. CI runs it |
| `check_generated.py` | Proves the generated files still match their generators. CI runs it |

## `logs/` — the record

| File | What it holds | Written by |
|---|---|---|
| `log.tsv` | Every rep: date, module, variant, minutes, clean, note | `make done` |
| `splits.tsv` | Phase breakdown: design, write, compile, debug | `make lap` + `make done` |
| `rehearsal.tsv` | Story takes: date, story, seconds, rating, note | `make rehearse` |
| `bughunt.tsv` | Bug hunts: date, module, mutation kind, minutes, found | `make hunt-done` |
| `.snapshots/` | Copies of your passing solutions, so `make hunt` has something to break. **Gitignored** | `make done` |
| `ai-use.tsv` | Every AI use: date, what for, which rule | You, by hand |
| `WEEKLY_REVIEW.md` | The Sunday honesty check template | You, Sundays |
| `design-prompts/` | Prompt answers with rubric scores | `make prompt`, then you |
| `architecture/` | Architecture drills with rubric scores | `make design`, then you |
| `PROGRESS.md` | Every capability scored against its evidence bar. **Generated** | `make progress` |
| `progress.json` | The same data, machine-readable — this is what a website reads | `make progress` |
| `.start_date` | Day 1. `date +%F > logs/.start_date` | You, once |

## Not in this repo, on purpose

| What | Where | Why |
|---|---|---|
| Mimic | `~/embedded/mimic` — its own repo | This repo schedules it and tracks what it covers; it contains none of it. Capabilities owned there are reported as *tracked outside this repo*, not as done |
| The HIL harness | `~/embedded/mimic-hil` — its own repo, week 8 | Public portfolio piece; needs its own clean front page |
| Throwaway C | `~/embedded/scratch` — not in git | So there is never a reason to commit junk to a real repo |
| Job-search material | `plan/APPLICATIONS.md`, `plan/private/` — both gitignored | This repo measures capability. It contains nothing about where to apply or what to ask for |
