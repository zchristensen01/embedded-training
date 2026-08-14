# Start here

This repo is a training system for embedded and test-and-integration engineering
interviews. It is not notes and it is not a course. It is a set of exercises with
timers attached, a spaced-repetition deck, and a log — built so that progress is
something you can measure rather than something you feel.

If you read nothing else, read this file. It takes five minutes and explains how the
whole thing fits together.

---

## The idea in one paragraph

Interview research produced a list of **numbered capabilities** — things you have to be able
to *do*, each with a stated bar for what counts as proof. Every one is assigned to a mechanism
that practises it repeatedly and records the result. Nothing is marked as learned because it
feels learned; it is marked when the log says so.

The count is not written into any document. `make progress` reports it, and CI proves the
spec and the coverage map still describe the same set.

```
plan/INTERVIEW_REQUIREMENTS.md      the capability list        THE SPECIFICATION
        │
        ├── plan/COVERAGE.md         who owns each one
        │
        ├── practice/                the mechanisms that do the work
        │     ├── katas/             C and Python, written cold every rep
        │     ├── decks/             embedded · test-integration · python
        │     ├── design-prompts/    SUBJECTS (test it) · ARCHITECTURE (design it)
        │     └── rehearsal/         the behavioural stories
        │
        ├── logs/                    what actually happened
        │     └── PROGRESS.md        the score, generated from the logs
        │
        └── research/                the interview research the spec is built on,
                                     with sources, dates and confidence ratings
```

## The seven mechanisms

Only the first is katas. That is deliberate — drilling code and then failing the
verbal round is the most common way this kind of preparation goes wrong.

| Mechanism | Covers | How it repeats | Command |
|---|---|---|---|
| **Kata** | C and Python fluency — the C and Y groups | Frozen tests, deleted `src/`, 7+ variants each | `make drill` |
| **Deck** | Concepts and verbal — the whole E group, most of T, and Y1 | Leitner boxes at 1/2/4/8/16 days, spoken aloud | `make review` |
| **Design prompt** | "How would you test X", the core T&I question | 60 rotating subjects, one fixed rubric | `make prompt` |
| **Architecture drill** | "Design this subsystem", the embedded design round | 8 rotating prompts, a different fixed rubric | `make design` |
| **Bug hunt** | Debugging code you did not write today | Your own old solution, silently mutated | `make hunt` |
| **Rehearsal** | Behavioural, 11 stories | Re-told to three strong takes on three days | `make rehearse` |
| **Project** | The HIL harness | Not repeatable — one artifact, done well | its own repo |

**Both languages, every day, from day one.** The C rep and the Python rep sit next to each
other on a weekday rather than being separated into phases. That is deliberate too: an
interview loop does not block by language, and working out *which* kind of problem you are
looking at before you solve it is part of the skill being trained.

## The kata mechanism, because it is the unusual one

Inside every kata directory:

```
practice/katas/ring_buffer/
├── BRIEF.md      committed   what it is, the API, how to think about it, what to test
├── VARIANTS.md   committed   the variants the drill draws from (seven or more)
├── NOTES.md      committed   one decision or bug per rep, appended automatically
├── include/      committed   the API contract.  FROZEN — never edited during a rep
│                          (a *_py kata has none: its contract is the BRIEF, and the
│                           frozen suite is what enforces it)
├── tests/        committed   the test suite.    FROZEN — never edited during a rep
└── src/          GITIGNORED  your implementation. DELETED at the start of every rep
```

`make drill` deletes `src/`, writes an empty stub, and starts a clock. **Every rep is
a genuine cold start, because your last solution does not exist.** The expensive,
hard-won artifacts — the contract and the test suite — are permanent. The
implementation is disposable, which is exactly backwards from normal software and
exactly right for practice.

What accumulates is the *lesson* and the *time*, not the code.

## Your first hour

```bash
date +%F > logs/.start_date     # the Monday you're starting
make dates                      # plan/CALENDAR.dated.md — 98 days with real dates
make today                      # what to do right now
```

`plan/CALENDAR.md` is committed and carries relative labels (`Day 1 · Mon`), because
your start date is yours and not the repo's. `make dates` writes the same ninety-eight
days with real dates to a gitignored file next to it — that is the one to open, or to paste
into a real calendar. `make calendar` regenerates the committed file and is only needed
after editing `tools/schedule.py`.

Then read, once, in this order — and then stop reading:

1. **`SETUP.md`** — day 0 and the kata build order.
2. **`plan/INTERVIEW_REQUIREMENTS.md`** — the research, and the capability list.
3. **`plan/COVERAGE.md`** — which mechanism owns each capability.
4. **`practice/PRACTICE_SYSTEM.md`** — how practice is made repeatable and AI-proof.
5. **`plan/CURRICULUM.md`** — fourteen weeks, hour by hour.

`plan/CALENDAR.md` then tells you what to do on each of the ninety-eight days. It is
generated, not written, so it cannot drift out of step with the rest.

## The daily loop

```
make today          what to do right now
                    read the BRIEF and the variant line — the clock is not running yet
make drill          start a rep — wipes src/, starts the clock. You are in `write`
make test           run the frozen suite — sanitizers for C, pytest for Python
                    also closes `write`, then `compile`/`run`, for you
make done           stop the clock, log the rep. Closes `debug`
make review         deck pass — ANSWER OUT LOUD
```

Three phases — `write -> compile -> debug`, and `write -> run -> debug` for a Python rep —
and you lap none of them by hand. `make test` sees both boundaries it can see and closes
them; `make done` closes the last. `make lap` is still there for a rep you drive yourself.

Most weekdays carry two reps: the assigned C kata and the assigned Python one. Both are
`make drill KATA=...`, and `make today` prints them in order.

**[`DAILY.md`](DAILY.md)** is the checklist for that loop: what a line like `make drill
KATA=bitops VARIANT=v1` actually does, what changes with the day of the week, and what you
owe the log at each end of a session. Read it before day 1.

Full list with explanations: **[`reference/COMMANDS.md`](reference/COMMANDS.md)**.

## The one rule that matters

> **AI writes infrastructure. You write everything that gets interviewed.**

AI may write Makefiles, CI config, the tooling in `tools/`, and test *runners*. It may
not write a single **test case**, any kata implementation, or any project code. "How
would you test this" is a top-three question in both tracks — outsourcing the test
suite means outsourcing the thing you are selling. Every use gets logged in
`logs/ai-use.tsv`, and the count should fall over the fourteen weeks.

That log is not just self-discipline. The research found a real company take-home that requires
candidates to submit a `PROMPTS.md` documenting the AI they used — the industry is moving to
*audit* AI use rather than ban it, and take-homes increasingly end in a live defence of the code
you submitted. Being able to say exactly what you generated and why is becoming the skill; being
unable to explain your own submission is the fastest way to fail the follow-up.

## How to tell it is working

```bash
make report      time curve, clean-compile rate, phase breakdown, coverage
make progress    every capability scored against its evidence bar
```

Four numbers matter, and all four come from the logs rather than from self-assessment:

- **Clean-first-compile rate** — the best single proxy for C syntax fluency. 40% by
  week 6, 55% by week 8, 70% by week 14. Python reps are excluded from it and reported
  separately: a Python kata has no compile step, so "clean" there is a different claim
  about a different skill, and one number covering both would measure neither.
- **`write` + `compile` as a share of total rep time** — syntax fluency in one number, and
  `write` + `run` for a Python rep. Under 40% by week 14. `make report` prints the two apart.
- **Reps per week** — consistency beats intensity. The calendar schedules thirteen a week:
  eight C and four Python across the weekdays and Sunday, plus Saturday's adaptive one. Eleven
  is the target, because one missed day is real life and two is a drift.
- **Capabilities met** — `make progress`. Should climb steadily, not in a rush at the end.
  The kata and rubric bars behind it are measured; the deck bar is graded by you, spaced out
  so a single generous `y` cannot carry a card. `plan/COVERAGE.md` says which is which.

If all four are flat and you feel like you are improving, you are not. That is what
the logs are for.
