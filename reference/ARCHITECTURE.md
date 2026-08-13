# Architecture

How this repo is put together internally, and the one trick the whole thing rests on.

For the three-repo layout and why the boundaries sit where they do, see
[`plan/REPOS.md`](../plan/REPOS.md). This file is about the inside of this repo.

---

## The gitignore trick that makes katas repeatable

This is the important bit, and it is the thing a normal practice repo is missing.

Inside each kata module:

```
practice/katas/ring_buffer/
├── BRIEF.md          committed   what it is, the API, how to think about it, what to test
├── VARIANTS.md       committed   the seven variants of this kata
├── NOTES.md          committed   design decisions and bugs, one line per rep
├── include/
│   └── ring_buffer.h committed   the API contract. Frozen. Not edited during a rep.
├── tests/
│   └── test_*.c      committed   the test suite. Frozen. Not edited during a rep.
└── src/
    └── ring_buffer.c GITIGNORED  the implementation. Deleted before every rep.
```

`.gitignore` contains `practice/katas/*/src/`.

**Why this works:** the expensive, correct, hard-won artifacts — the API contract and the
tests — are permanent and version-controlled. The implementation, the thing you are trying to
get fast at producing, is disposable. `make drill` deletes `src/`, writes an empty stub, and
starts a timer. Every rep is a genuine cold start because the last solution is not sitting
there to read.

You get the repeatability of a kata without the "I already solved this" problem, and the git
history stays clean because it only ever contains the parts that should be stable.

The only things that accumulate across reps are `NOTES.md` and `logs/log.tsv`. That is exactly
right: what you keep is the *lesson* and the *time*, not the code.

---

## What is generated and what is source

Three files are output. Every document says so, and `make check-generated` proves it on every
push — a hand-edit to any of them fails CI rather than surviving until the next regeneration
silently reverts it.

| Generated | Generator | Regenerate with |
|---|---|---|
| `plan/CALENDAR.md` | `tools/schedule.py` | `make calendar` |
| `logs/PROGRESS.md` | `tools/progress.py` | `make progress` |
| `logs/progress.json` | `tools/progress.py` | `make progress` |

The rule behind that: **one source of truth per fact, and the tools read it rather than
restating it.**

| Fact | Lives in | Read by |
|---|---|---|
| The kata rotation and every day shape | `tools/schedule.py` | `make calendar`, `make today` |
| The kata build order | derived from the rotation | `make check-calendar`, printed into the calendar |
| Per-kata target times | `tools/drill.py:TARGETS` | `report.py`, `check_log.py`, `progress.py`, `schedule.py` |
| The capability list | `plan/INTERVIEW_REQUIREMENTS.md` | `progress.py`, `check_decks.py` |
| Who owns each capability | `plan/COVERAGE.md` | `progress.py`, `schedule.py` |
| Which mechanism is a capability's *bar* | `tools/progress.py:bar_for()` | `progress.py`, `check_decks.py`, `schedule.py` |
| When a story counts as ready | `tools/rehearse.py:ready()` | `rehearse.py`, `progress.py` |
| The behavioural stories and their targets | `practice/rehearsal/STORIES.md` | `rehearse.py` |

Every one of those used to have, or nearly had, a second copy. Two of them drifted before
anyone noticed: `report.py` kept its own target-time dict and fell a kata behind, and
`today.py` parsed the curriculum for main-block text while the calendar rendered it from the
scheduler, so the two disagreed about week 9. Both are now single-sourced, which is why the
table above exists — it is the list to check before adding a constant anywhere.

---

## The checks, and what each one can actually prove

Six, all run by CI on every push and all runnable together with `make check`.

| Check | Proves |
|---|---|
| `check-frozen` | Every frozen header parses standalone and every frozen suite compiles against it, gcc and clang |
| `check-log` | `logs/log.tsv` is well formed: header, fields, date order, known modules, real variants |
| `check-calendar` | Schedule, derived build plan, timer blocks, variants and retirement feasibility all agree |
| `check-coverage` | The spec and the coverage map describe exactly the same set of capabilities, each group numbered from 1 with no gaps |
| `check-decks` | Every card tag names a real capability, and every deck-scored capability has a card |
| `check-generated` | The three generated files match their generators |

**CI deliberately does not run the katas.** `src/` is gitignored and deleted every rep, so
there is nothing to link — the only thing that could be tested is an implementation that is
not supposed to exist. What CI protects is the artifacts that are meant to be permanent.

Two things worth knowing about the limits:

- `check-coverage` cannot tell whether an ownership assignment is *correct*, only that one
  exists and parses. `plan/COVERAGE.md` owner cells are prose matched by regex, which is the
  brittlest thing in the repo. What keeps it honest is the bijection check: a reworded cell
  that stops parsing becomes a CI failure rather than a silent zero.
- `check-decks` cannot tell whether a card's answer is *right*. It checks that the tag names a
  real capability and that nothing scored by the deck is left without a card.

---

## Toolchain

C11, `-Wall -Wextra -Werror`, AddressSanitizer and UndefinedBehaviorSanitizer with
`-fno-sanitize-recover=all`, on both gcc and clang. `concurrency_sim` builds under
ThreadSanitizer instead, because TSan and ASan cannot coexist in one binary; `make test`
selects per module.

`-fno-sanitize-recover=all` is not optional. By default UBSan prints a diagnostic and lets the
program carry on, so a run containing real undefined behaviour still exits 0 and CI goes green.
This makes it abort the way ASan does.

`make analyze` runs `gcc -fanalyzer` and is advisory rather than gating — it produces false
positives often enough that `-Werror` would be wrong. Read the path it prints rather than
obeying it. `make valgrind` drops the sanitizers, because Valgrind and ASan conflict.
