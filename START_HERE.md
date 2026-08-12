# Start here

This repo is a training system for embedded and test-and-integration engineering
interviews. It is not notes and it is not a course. It is a set of exercises with
timers attached, a spaced-repetition deck, and a log — built so that progress is
something you can measure rather than something you feel.

If you read nothing else, read this file. It takes five minutes and explains how the
whole thing fits together.

---

## The idea in one paragraph

Interview research produced a list of **78 numbered capabilities** — things you have
to be able to *do*, each with a stated bar for what counts as proof. Every one is
assigned to a mechanism that practises it repeatedly and records the result. Nothing
is marked as learned because it feels learned; it is marked when the log says so.

```
plan/INTERVIEW_REQUIREMENTS.md      the 78 capabilities        THE SPECIFICATION
        │
        ├── plan/COVERAGE.md         who owns each one
        │
        ├── practice/                the mechanisms that do the work
        │
        └── logs/                    what actually happened
                └── PROGRESS.md      the score, generated from the logs
```

## The five mechanisms

Only the first is katas. That is deliberate — drilling code and then failing the
verbal round is the most common way this kind of preparation goes wrong.

| Mechanism | Covers | How it repeats | Command |
|---|---|---|---|
| **Kata** | C fluency, 12 items | Frozen tests, deleted `src/`, 7 variants each | `make drill` |
| **Deck** | Concepts and verbal, ~37 items | Leitner boxes at 1/2/4/8/16 days, spoken aloud | `make review` |
| **Design prompt** | "How would you test X", the core T&I question | 40 rotating subjects, one fixed rubric | `make prompt` |
| **Rehearsal** | Behavioural, 10 stories | Re-told to three strong takes | `make rehearse` |
| **Project** | The HIL harness, 6 items | Not repeatable — one artifact, done well | its own repo |

## The kata mechanism, because it is the unusual one

Inside every kata directory:

```
practice/katas/ring_buffer/
├── BRIEF.md      committed   what it is, the API, how to think about it, what to test
├── VARIANTS.md   committed   seven variants the drill draws from
├── NOTES.md      committed   one decision or bug per rep, appended automatically
├── include/      committed   the API contract.  FROZEN — never edited during a rep
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
make calendar                   # stamps plan/CALENDAR.md with real dates
make today                      # what to do right now
```

Then read, once, in this order — and then stop reading:

1. **`SETUP.md`** — day 0 and the kata build order.
2. **`plan/INTERVIEW_REQUIREMENTS.md`** — the research, and the 78 capabilities.
3. **`plan/COVERAGE.md`** — which mechanism owns each capability.
4. **`practice/PRACTICE_SYSTEM.md`** — how practice is made repeatable and AI-proof.
5. **`plan/CURRICULUM.md`** — ten weeks, hour by hour.

`plan/CALENDAR.md` then tells you what to do on each of the seventy days. It is
generated, not written, so it cannot drift out of step with the rest.

## The daily loop

```
make today          what to do right now
make drill          start a rep — wipes src/, starts the clock
    make lap        at each transition: design -> write -> compile -> debug
make test           build and run the frozen suite under sanitizers
make done           stop the clock, log the rep
make review         deck pass — ANSWER OUT LOUD
```

Full list with explanations: **[`reference/COMMANDS.md`](reference/COMMANDS.md)**.

## The one rule that matters

> **AI writes infrastructure. You write everything that gets interviewed.**

AI may write Makefiles, CI config, the tooling in `tools/`, and test *runners*. It may
not write a single **test case**, any kata implementation, or any project code. "How
would you test this" is a top-three question in both tracks — outsourcing the test
suite means outsourcing the thing you are selling. Every use gets logged in
`logs/ai-use.tsv`, and the count should fall over the ten weeks.

## How to tell it is working

```bash
make report      time curve, clean-compile rate, phase breakdown, coverage
make progress    the 78 capabilities scored against their evidence bars
```

Four numbers matter, and all four come from the logs rather than from self-assessment:

- **Clean-first-compile rate** — the best single proxy for syntax fluency. 40% by
  week 4, 55% by week 6, 70% by week 10.
- **`write` + `compile` as a share of total rep time** — syntax fluency in one number.
  Under 40% by week 10.
- **Reps per week** — consistency beats intensity. Six is the target.
- **Capabilities met** — `make progress`. Should climb steadily, not in a rush at the end.

If all four are flat and you feel like you are improving, you are not. That is what
the logs are for.
