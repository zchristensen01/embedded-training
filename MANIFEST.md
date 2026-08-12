# Manifest

Every file, what it's for, whether you edit it.

## Root

| File | What it is | Edit? |
|---|---|---|
| `README.md` | Front page: what this is, why it's built this way, the layout | No |
| `START_HERE.md` | **Read this first.** How the whole system fits together, in five minutes | No |
| `SETUP.md` | Day 0 and the staged kata build order. **Start here** | No |
| `MANIFEST.md` | This file | No |
| `Makefile` | The command interface. Put your build rules under `test:` | **Yes** |
| `.gitignore` | Contains `practice/katas/*/src/` — the line that makes reps repeatable | Rarely |

## `plan/` — the program. Read once, then follow the calendar.

| File | What it is | Edit? |
|---|---|---|
| `INTERVIEW_REQUIREMENTS.md` | The research findings + all 78 numbered capabilities. The spec | No |
| `COVERAGE.md` | Who owns each capability — Mimic vs a mechanism in here | No |
| `CALENDAR.md` | All 70 days: timers, katas, main blocks | `make calendar` |
| `CURRICULUM.md` | Ten weeks, hour allocation, the week 6 gate | No |
| `REPOS.md` | The three-repo layout on disk, naming, what `mimic-hil` is | No |

## `practice/` — the daily mechanics

| Path | What it is | Edit? |
|---|---|---|
| `PRACTICE_SYSTEM.md` | Four formats, variants, constraint cards, AI rules, measurement | No |
| `katas/README.md` | The eleven-module map and target times | No |
| `katas/<name>/BRIEF.md` | What it is, the API, how to think about it, what to test | Once, when building |
| `katas/<name>/VARIANTS.md` | The variants `make drill` draws from | Add over time |
| `katas/<name>/NOTES.md` | One decision or bug per rep | `make done` appends |
| `katas/<name>/include/*.h` | The API contract. **Frozen during a rep** | Once, when building |
| `katas/<name>/tests/*` | The suite. **Frozen during a rep. You write every case** | Once, when building |
| `katas/<name>/src/` | Your implementation. **Gitignored, deleted every rep** | Every rep |
| `decks/embedded.tsv` | 41 cards: `topic <TAB> question <TAB> answer <TAB> trap <TAB> caps` | `make card` |
| `decks/test-integration.tsv` | 15 cards, same format | `make card` |
| `design-prompts/SUBJECTS.md` | 40 subjects + the fixed 8-category rubric | No |
| `rehearsal/README.md` | How takes work, what "ready" means | No |
| `rehearsal/STORIES.md` | The ten behavioural stories | **Yes — fill before your first take** |

**Katas shipping with BRIEF + VARIANTS written:** `register_map`, `mem_primitives`,
`pool_allocator`, `concurrency_sim`, `test_harness_py`. You owe the header and tests.
**Katas with BRIEF + VARIANTS carried over from the old repo:** `bitops`, `ring_buffer`, `fsm`,
`debouncer`, `protocol_parser`, `fixed_point_pid`. `rollover_timer` ships written too. For all
seven you owe the header and the tests, same as the five above — use `make newkata NAME=x` to
scaffold the directories it needs.

## `reference/` — consult, don't drill

| File | What it is |
|---|---|
| `question-bank/README.md` | Topic-to-kata map, why the five new katas exist |
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
| `report.py` | Time curve, clean-compile rate, phase breakdown, coverage |
| `progress.py` | Scores the 78 capabilities, writes `logs/PROGRESS.md` and `progress.json` |
| `card.py` | Adds a deck card in ~20s. `make card`, and offered at the end of `make done` |
| `schedule.py` | Generates `plan/CALENDAR.md` (named `schedule` to avoid shadowing stdlib `calendar`) |
| `newkata.py` | Scaffolds a kata module |
| `check_log.py` | Validates `logs/log.tsv` against the schema `make done` writes. CI runs it |

## `logs/` — the record

| File | What it holds | Written by |
|---|---|---|
| `log.tsv` | Every rep: date, module, variant, minutes, clean, note | `make done` |
| `splits.tsv` | Phase breakdown: design, write, compile, debug | `make lap` + `make done` |
| `rehearsal.tsv` | Story takes: date, story, seconds, rating, note | `make rehearse` |
| `ai-use.tsv` | Every AI use: date, what for, which rule | You, by hand |
| `WEEKLY_REVIEW.md` | The Sunday honesty check template | You, Sundays |
| `design-prompts/` | Prompt answers with rubric scores | `make prompt`, then you |
| `PROGRESS.md` | The 78 capabilities scored against their evidence bars. **Generated** | `make progress` |
| `progress.json` | The same data, machine-readable — this is what a website reads | `make progress` |
| `.start_date` | Day 1. `date +%F > logs/.start_date` | You, once |

## Not in this repo, on purpose

| What | Where | Why |
|---|---|---|
| Mimic | `~/embedded/mimic` — its own repo | Already built and set up. This repo schedules it, doesn't contain it |
| The HIL harness | `~/embedded/mimic-hil` — its own repo, week 8 | Public portfolio piece; needs its own clean front page |
| Throwaway C | `~/embedded/scratch` — not in git | So you never commit junk to a real repo |
