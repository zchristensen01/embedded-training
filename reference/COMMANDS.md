# Commands

Every command, what it does, and what it writes. `make help` prints a short version.

Nothing here needs arguments to be useful — every command has a sensible default.

---

## The daily loop

### `make today`
Prints the current day's assignment: the week, the phase, the Mimic sessions or main
block, and every timer block with its duration. Reads `logs/.start_date` to work out
which day it is, and takes the day's shape from `tools/schedule.py` so it can never
disagree with the calendar.

Needs `logs/.start_date`. Create it once: `date +%F > logs/.start_date`.

### `make drill`
Starts a kata rep. **Deletes `practice/katas/<kata>/src/`**, writes an empty stub
containing only the `#include`, and starts a clock. About a third of the time it also
draws a constraint card ("no dynamic allocation", "single return per function", "write
it on paper first").

```bash
make drill                              # adaptive pick — see below
make drill KATA=ring_buffer             # a specific kata, random variant
make drill KATA=ring_buffer VARIANT=v3  # exactly this
```

With no arguments it picks by **worst recent time first, then longest since last rep,
then never attempted**, and will not repeat a kata within three days if alternatives
exist. That is deliberate: left to choose, you would avoid `pool_allocator`. The
calendar names a specific kata on every day except Saturday, which is left adaptive on
purpose so one day a week catches whatever you have been avoiding.

### `make lap`
Records a phase split. Call it at each transition:

| Phase | From | To |
|---|---|---|
| `design` | `make drill` | the first line of code you type |
| `write` | first line | your first compile attempt |
| `compile` | first compile | it compiles clean |
| `debug` | clean compile | tests pass |

```bash
make lap            # auto-advances to the next phase in sequence
make lap P=debug    # name it explicitly
```

A total time tells you whether you are getting faster. The split tells you *what is
slow*, which is the part you can act on. Missing a lap call is fine — `make done`
attributes the remainder to the next phase.

### `make test`
Builds and runs the frozen test suites under sanitizers: `-std=c11 -Wall -Wextra
-Werror -fsanitize=address,undefined -fno-sanitize-recover=all`.

```bash
make test                      # every kata that has an implementation
make test MODULE=ring_buffer   # just one
make test CC=clang             # second compiler; the two disagree usefully
```

Two katas are special and handled automatically: `concurrency_sim` builds under
ThreadSanitizer instead of AddressSanitizer (the two cannot coexist in one binary),
and `test_harness_py` runs under pytest instead of being compiled.

### `make done`
Stops the clock, prints where the time went, and asks two questions: whether it was
clean on first compile, and one line about a decision or a bug. Writes
`logs/log.tsv`, `logs/splits.tsv`, and appends the note to the kata's `NOTES.md`.

Then offers to add a deck card — see `make card`.

### `make review`
A spaced-repetition pass over `practice/decks/*.tsv`. Five Leitner boxes; box N comes
back after 2^(N-1) days: 1, 2, 4, 8, 16. Right answer moves up a box, wrong drops to
box 1.

```bash
make review        # whatever is due, 20 cards
make review N=30   # more
make stats         # box distribution, and how many cards are unseen
```

**Two rules that make this work.** Answer *out loud, in full sentences*, before
revealing — the failure mode is knowing an answer and not being able to structure it
aloud. And a card only counts as correct if you also said the **trap**, the wrong
answer an interviewer expects to hear. "A mutex has ownership, a semaphore is
signalling" is a pass; adding "and the classic wrong answer is that they are the same
but semaphores count higher" is what sounds like expertise.

---

## Weekly and occasional

### `make card`
Adds a deck card in about twenty seconds. This is how the deck grows into something
that fits you rather than staying at the 56 it ships with.

```bash
make card                                   # interactive
make card ARGS="--topics"                   # topics already in use
make card ARGS="--last 3"                   # the most recent cards in each deck
make card ARGS='-t interrupts -q "..." -a "..." -x "..." -c E9'
```

It shows the topics already in use so they stay consistent, warns if a similar
question already exists, and **refuses a card with no trap**. It also asks which
capability ID the card proves, which is what lets `make progress` count it.

Add one every time a rep or a Mimic session surprises you — something you half-knew,
or got wrong out loud. Same day, while it still stings. `make done` offers the prompt
automatically at the end of every rep, which is the moment it is most likely to apply.

### `make prompt`
Draws one of 40 "how would you test X" subjects and opens a pre-scored answer file in
`logs/design-prompts/`. Ten minutes, written, then said aloud.

This is the highest-frequency test-and-integration question and one of the four
listed reasons candidates get rejected. Two things fail you automatically regardless
of the rest: **proposing solutions before asking for requirements**, and **stopping
before you are told to stop**. The subject rotates; the eight-category rubric does
not, so your score across many subjects measures one real skill.

### `make rehearse`
Draws a behavioural story from `practice/rehearsal/STORIES.md`, times the take, and
asks you to rate it. Writes `logs/rehearsal.tsv`.

```bash
make rehearse        # a story that needs work
make rehearse S=B3   # a specific one
```

A story is ready at **three strong takes on three different days**. The research is
blunt that test-and-integration candidates fail the behavioural round more often than
the technical one, so this is not the optional part. Fill in `STORIES.md` before your
first take — the file ships as a skeleton, and the stories have to be yours.

### `make report`
Four measurements, all from the logs:

1. **Time curve per kata.** Should fall, then flatten.
2. **Phase breakdown.** `write` + `compile` as a share of total — syntax fluency in
   one number.
3. **Clean-first-compile rate.** 40% by week 4, 55% by week 6, 70% by week 10.
4. **Coverage.** Which katas you are avoiding; flags anything untouched for 14 days.

### `make progress`
Scores all 78 capabilities against the evidence bars in
`plan/INTERVIEW_REQUIREMENTS.md` and writes two files:

- **`logs/PROGRESS.md`** — human-readable, and the file to link from a website.
- **`logs/progress.json`** — the same data, machine-shaped, for anything that wants
  to render it.

Nothing in it is self-assessed. A capability is met when its bar is met and logged:
three clean kata reps at target across three variants, every tagged deck card in
Leitner box 4 or higher, or three rated takes of a story. Capabilities proved outside
this repo — bench work in Mimic, artifacts in the harness — are reported as such
rather than counted or hidden.

### `make calendar`
Regenerates `plan/CALENDAR.md` — all seventy days, with real dates if
`logs/.start_date` exists. Also regenerates the **Build plan**, which is derived from
the kata rotation rather than written by hand.

Run this after changing anything in `tools/schedule.py`.

### `make newkata NAME=x`
Scaffolds a kata module: `BRIEF.md`, `VARIANTS.md`, `NOTES.md`, `include/x.h`,
`tests/test_x.c`, and an empty gitignored `src/`. Never overwrites an existing file.

You then owe the header and the tests, in that order, and the AI rule applies hardest
here.

---

## Checks

These three run in CI on every push. Run them locally any time.

### `make check-frozen`
Every frozen header parses standalone and every frozen test suite compiles against it,
on both gcc and clang.

This is what CI can actually prove. `src/` is gitignored, so a fresh clone has no
implementations and no kata can be linked — but the artifacts that *are* permanent,
the contracts and the suites, must never stop being valid C.

### `make check-log`
Validates `logs/log.tsv`: header, field count, date order, known modules, variants
that exist in that kata's `VARIANTS.md`, and `y`/`n` for the clean column. It takes
its module and variant lists from the filesystem, so adding a kata needs no change.

Mostly this catches rows you added by hand — Mimic sessions and project hours.

### `make check-calendar`
Proves the schedule and the build plan agree: nothing scheduled that is never built,
nothing built that is never scheduled, no variant named that does not exist, no kata
on disk that is unscheduled, no stale exemption, and no build session so long it will
not realistically happen. Also prints the whole derived plan.

### `make check-coverage`
Every one of the 78 capabilities has a mechanism that practises it. Fails if any
capability is orphaned — scheduled nowhere, owned by nothing.

---

## Build extras

| Command | What it does |
|---|---|
| `make debug MODULE=x` | `-g -O0` build for gdb, sanitizers still on. Does not run it |
| `make analyze` | `gcc -fanalyzer` — finds bugs without running. Advisory, not gating |
| `make valgrind MODULE=x` | Second opinion on memory, sanitizers off (they conflict) |
| `make list` | Which katas have an implementation, which are scaffolded |
| `make clean` | Removes `build/` |

---

## What writes what

| File | Written by | Committed |
|---|---|---|
| `logs/log.tsv` | `make done` | yes |
| `logs/splits.tsv` | `make lap` + `make done` | yes |
| `logs/rehearsal.tsv` | `make rehearse` | yes |
| `logs/ai-use.tsv` | you, by hand | yes |
| `logs/design-prompts/*.md` | `make prompt`, then you | yes |
| `logs/PROGRESS.md`, `logs/progress.json` | `make progress` | yes |
| `logs/WEEKLY_REVIEW.md` | you, Sundays | yes |
| `plan/CALENDAR.md` | `make calendar` | yes |
| `practice/katas/*/NOTES.md` | `make done` | yes |
| `practice/decks/*.tsv` | `make card` | yes |
| `practice/decks/.state.json` | `make review` | no — local scheduling state |
| `logs/.drill_state.json` | `make drill` | no — one rep in flight |
| `logs/.start_date` | you, once | no — yours, not the repo's |
| `practice/katas/*/src/` | you, every rep | **no — deleted every rep, on purpose** |
