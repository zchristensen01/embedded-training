# Commands

Every command, what it does, and what it writes. `make help` prints a short version.

Nothing here needs arguments to be useful — every command has a sensible default.

---

## The daily loop

### `make today`
Prints the current day's assignment: the week, the phase, the Mimic sessions or main
block, the deck focus, and every timer block with its duration. Reads `logs/.start_date`
to work out which day it is.

**Everything else comes from `tools/schedule.py`** — the same generator that writes
`plan/CALENDAR.md`, so the two cannot disagree. This file used to read the main-block
text out of the curriculum instead, and they drifted.

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
exist. That is deliberate: left to choose, you would avoid `pool_allocator`. The calendar
names a specific kata on every day except Saturday, which is left adaptive on purpose so
one day a week catches whatever you have been avoiding — and Saturday is the only slack
in the rotation: fourteen unassigned reps over the plan, spent wherever you are weakest.

Only katas that actually have a frozen header and test suite are eligible. It will not
hand you a module you have not built yet, and neither will `KATA=` — a rep against an
empty suite is not a rep.

### `make lap`
Records a phase split by hand. **You normally never call this** — `make test` and `make done`
close all three boundaries for you. It exists for a rep you drive outside the Makefile, and a
manual call always overrides the automatic one.

| Phase | From | To | Closed by |
|---|---|---|---|
| `write` | `make drill` | your first `make test` | `make test` |
| `compile` | first `make test` | it compiles clean | `make test` |
| `debug` | clean compile | tests pass | `make done` |

A Python kata (`*_py`) has no compile step, so its second phase is **`run`** — first execution
attempt until it runs without a syntax or import error. Everything picks the right set from
the module name.

```bash
make lap            # auto-advances to the next phase in sequence
make lap P=debug    # name it explicitly
```

**There is no `design` phase.** Read the BRIEF and the variant line before `make drill`; the
clock starts at the keyboard. It was dropped because it measured reading — genuine work once
per module, a glance thereafter — while still needing a lap call whose omission moved minutes
into `write`, the number the whole fluency claim rests on. `logs/splits.tsv` still accepts a
`design` row so rows written before the change stay valid.

A total time tells you whether you are getting faster. The split tells you *what is
slow*, which is the part you can act on.

### `make test`
Builds and runs the frozen test suites under sanitizers: `-std=c11 -Wall -Wextra
-Werror -fsanitize=address,undefined -fno-sanitize-recover=all`.

```bash
make test                      # every kata that has an implementation
make test MODULE=ring_buffer   # just one
make test CC=clang             # second compiler; the two disagree usefully
```

Some katas are handled automatically: `concurrency_sim` builds under ThreadSanitizer instead
of AddressSanitizer (the two cannot coexist in one binary), and the four `*_py` modules
(`binary_frame_py`, `log_parser_py`, `cli_tool_py`, `test_harness_py`) run under pytest
instead of being compiled. The `_py` suffix is the switch, in the Makefile and in every tool.

**It also laps the rep.** If a drill is in flight for the module being tested, this closes
`write` when you invoke it and `compile`/`run` once the build or the import succeeds. That
second one fires on **acceptance, not on passing**: a failing assertion means the machine ran
your code, so the phase is over and you are debugging; a compile error or an `ImportError`
means it never got that far, and you stay in `compile`/`run` until a later `make test` gets
through. For C the distinction is the compiler's exit status; for pytest it is exit 0 or 1
against 2, 3, 4 or 5. Both calls are silent no-ops when no rep is in flight, so running
`make test` during unrelated work never writes a split row.

**When a C suite fails**, it prints the debugger line — `make debug MODULE=x`, then
`gdb build/x-debug`. Worth taking whenever the failure is silent: sanitizers name the file
and line for a memory bug, but a wrong answer with no report is what a debugger is for.
[`GDB.md`](GDB.md) has the commands.

### What the build actually runs

Worth reading once. `make test` does this per C module:

```bash
gcc -std=c11 -Wall -Wextra -Werror -O1 \
    -fsanitize=address,undefined -fno-sanitize-recover=all \
    -Ipractice/katas/<m>/include \
    practice/katas/<m>/src/*.c practice/katas/<m>/tests/*.c -o build/<m>
./build/<m>
```

and this per Python module:

```bash
PYTHONPATH=practice/katas/<m>/src \
  python3 -B -m pytest -q -p no:cacheprovider practice/katas/<m>/tests
```

| Flag | Why |
|---|---|
| `-std=c11` | One language version, so a GNU extension that happens to work here is still a portability bug |
| `-Wall -Wextra` | The warnings that catch real bugs, not just style |
| `-Werror` | A warning **stops the build**. Otherwise warnings accumulate and stop being read |
| `-O1` | Some warnings only appear once the optimiser runs the dataflow analysis. `-O0` hides them |
| `-fsanitize=address` | Instruments every memory access: overflow, use-after-free, leaks |
| `-fsanitize=undefined` | Signed overflow, bad shifts, misaligned access, null deref |
| `-fno-sanitize-recover=all` | **Undefined behaviour aborts** rather than printing and exiting 0. Without it a sanitizer finding can pass CI |
| `-I<m>/include` | The frozen header. `src/` is compiled *against* it and never edits it |
| `-B` (Python) | Don't write `__pycache__` into `src/`, which `make drill` then has to delete |
| `-p no:cacheprovider` | Don't write `.pytest_cache` either |
| `PYTHONPATH=<m>/src` | How the frozen suite finds your implementation. It is the Python equivalent of `-I` |

`concurrency_sim` swaps `-fsanitize=address,undefined` for `-fsanitize=thread -pthread` —
ThreadSanitizer and AddressSanitizer cannot coexist in one binary, and a concurrency kata
needs the one that finds data races.

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
that fits you rather than staying at what it ships with.

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
Draws one of the 60 "how would you test X" subjects and opens a pre-scored answer file in
`logs/design-prompts/`. Ten minutes, written, then said aloud. **Fill in the rubric total**
when you score it — T1 is met on the score, not on the number of files, and an unscored
answer counts for nothing.

This is the highest-frequency test-and-integration question and one of the four
listed reasons candidates get rejected. Two things fail you automatically regardless
of the rest: **proposing solutions before asking for requirements**, and **stopping
before you are told to stop**. The subject rotates; the eight-category rubric does
not, so your score across many subjects measures one real skill.

### `make design`
Draws one of the 8 architecture prompts from `practice/design-prompts/ARCHITECTURE.md`,
starts a 45-minute clock, and opens a pre-scored answer file in `logs/architecture/`.
**Fill in the rubric total** — E30 is met on three scored 12+/16, not on the number of files.

```bash
make design            # the prompt you have written least recently
make design N=3        # that one
make designs           # what you have written and what it scored
```

**Not the same exercise as `make prompt`, and the difference is the point.** A design prompt
hands you a finished object and asks how you would test it. This asks you to invent the
object: partition ISR from main, budget RAM and flash *in numbers*, choose a comms topology,
plan power states, say what fails and what the safe state is, and say where you would cut it
to test it. Then argue against yourself and answer.

Candidate reports put it as a dedicated round at Google and Meta Reality Labs and as a design
item inside Tesla's and Medtronic's take-homes. Two automatic failures: **drawing before
asking what the constraints are**, and **a block diagram with no numbers on it**. Axis 8 —
holding the position under pushback — is the behavioural half, and logs separately as a B11
rehearsal take.

### `make rehearse`
Draws a behavioural story from `practice/rehearsal/STORIES.md`, times the take, and
asks you to rate it. Writes `logs/rehearsal.tsv`.

```bash
make rehearse        # a story that needs work
make rehearse S=B3   # a specific one
```

A story is ready at **three takes rated strong, on three different days** — three takes
in one afternoon is one rehearsal, not three. `tools/rehearse.py:ready()` is the single
definition of that, and `make progress` imports it rather than keeping a second opinion.

The research is blunt that test-and-integration candidates fail the behavioural round
more often than the technical one, so this is not the optional part. Fill in
`STORIES.md` before your first take — the file ships as a skeleton, the stories have to
be yours, and the calendar's rehearsal slots start in week 3. Story targets come from
`STORIES.md` too, so adding a story needs no code change.

### `make hunt`
Debugging practice, in code you did not write — using your own code.

```bash
make hunt              # picks an old snapshot you have not hunted recently
make hunt KATA=fsm     # that module
make hunt-done         # stop the clock, reveal the mutation, log it
make hunts             # your history: which bug kinds catch you out
make snapshots         # what is available to hunt in
```

`make done` quietly keeps a copy of each passing implementation in `logs/.snapshots/`
(gitignored, like `src/`). `make hunt` takes one from an earlier week, changes exactly one
token — a flipped comparison, an off-by-one, a dropped `volatile` — checks the result
still compiles but now **fails the suite**, and drops it into `src/` with a clock running.
You run `make test`, read the failure, and find the line.

This exists because the research says take-homes hand you a codebase, while every other
mechanism here starts from an empty editor. It could not be closed by writing a corpus of
broken C — an AI-written bug is an AI-written exercise — so the bug is generated
mechanically from your own work instead. A rep from three weeks ago is genuinely code you
did not write today.

**Do not diff against the snapshot.** That is the answer, and it is the one thing that
makes the exercise worthless.

**This is the debugger exercise.** The mutations are chosen to be silent, so nothing raises
and no sanitizer names a line for you — which is the condition gdb exists for and one a
normal kata rep never produces. `make hunt` builds the `-g -O0` binary and prints the
invocation; `make hunt-done` asks whether you found it by stepping or by reading, and
`make hunts` reports the split alongside your found rate. Reading works fine on code you
wrote; it is the habit that breaks on a take-home. [`GDB.md`](GDB.md) is the short version
of the tool.

### `make report`
Four measurements, all from the logs:

1. **Time curve per kata.** Should fall, then flatten.
2. **Phase breakdown.** `write` + `compile` as a share of total — syntax fluency in
   one number.
3. **Clean-first-compile rate.** 40% by week 6, 55% by week 8, 70% by week 14.
4. **Coverage.** Which katas you are avoiding; flags anything untouched for 14 days.

### `make progress`
Scores every capability against the evidence bars in
`plan/INTERVIEW_REQUIREMENTS.md` and writes two files:

- **`logs/PROGRESS.md`** — human-readable, and the file to link from a website.
- **`logs/progress.json`** — the same data, machine-shaped, for anything that wants
  to render it.

Nothing in it is a rating of how well something is known — a capability is met when its bar is
met and logged. The kata and rubric bars are measured; the deck bar is graded by you, spaced
out. `plan/COVERAGE.md` says which is which. A capability is met when:
three consecutive clean kata reps at target across three variants, 80% of a capability's
deck cards in Leitner box 4 or higher, three strong takes of a story on three different days,
or — for T1 — enough scored design prompts with the recent ones clearing 12/16.

Capabilities whose mechanism lives elsewhere — bench work in Mimic, artifacts in the
harness repo — are reported as **tracked outside this repo** and left out of the score.
That is not a claim the work is done; it is a statement that this repo cannot see it.

### `make log`
The per-module time curve, straight out of `logs/log.tsv`, plus which modules have met their
bar and how many reps each has had. Clean rates are reported **per language** — a C rep's
"clean" means it compiled first try under `-Werror` with the sanitizers silent, a Python rep's
means it ran first try with no traceback, and averaging the two measures neither.

Faster than `make report` and useful mid-week. `make report` is the Sunday version.

### `make status`
What rep is in flight right now: module, variant, elapsed minutes, the laps recorded so far,
which phase you are in, and the constraint card if you drew one. Prints "Nothing in progress"
if the clock is not running.

Use it when you have lost track of whether you called `make drill`, or which lap comes next.

### `make snapshots`
Which modules have a solution old enough to hunt in, and when each was written. `make hunt`
picks from this list. Empty until you have finished a few reps — snapshots are taken by
`make done`.

### `make calendar`
Regenerates `plan/CALENDAR.md` — all ninety-eight days, always with **relative** day labels
(`Day 1 · Mon`). Also regenerates the **Build plan**, which is derived from the kata
rotation rather than written by hand.

Run this after changing anything in `tools/schedule.py`. You do not need it otherwise.

### `make dates`
Writes the same ninety-eight days to `plan/CALENDAR.dated.md` with **real dates**, read from
`logs/.start_date`. Gitignored — this is the one to open daily, or to paste into a real
calendar.

The split is not fussiness. The shape of the ninety-eight days is a repo fact, identical for
anyone who clones this. The Monday you started is not: `logs/.start_date` is gitignored
on purpose. Stamping your dates into the committed file made `make check-generated` fail
on every machine with a different start date — CI included, since it has none.

### `make newkata NAME=x`
Scaffolds a kata module: `BRIEF.md`, `VARIANTS.md`, `NOTES.md`, `include/x.h`,
`tests/test_x.c`, and an empty gitignored `src/`. Never overwrites an existing file.

You then owe the header and the tests, in that order, and the AI rule applies hardest
here.

---

## Checks

All six run in CI on every push. `make check` runs the set locally.

### `make check-frozen`
Every frozen header parses standalone and every frozen test suite compiles against it,
on both gcc and clang.

This is what CI can actually prove. `src/` is gitignored, so a fresh clone has no
implementations and no kata can be linked — but the artifacts that *are* permanent,
the contracts and the suites, must never stop being valid C.

### `make check-frozen-py`
Imports every frozen `*_py` suite and enumerates its tests under pytest, without running
them. `src/` is gitignored, so — exactly as for C — the most that can be proved about a
frozen Python suite is that it is valid and collectable.

This exists because it did not, and a suite with a syntax error passed every other check and
shipped green. You would have found it mid-rep, with the clock running.

**How it imports a suite whose subject does not exist.** The C check compiles a test file
against the *header*; only linking needs an implementation. Python has no such split —
collection imports the test module, which imports the implementation — so this check
generates a stand-in for the kata's own module and collects against that. The stand-in is
what stands where a C header stands. Nothing here reads `src/`, so the check gives the same
answer on a clean tree, in CI, and in the middle of a rep.

Only the kata's own module is stood in for. `import pytset` is a typo, not a missing
implementation, and it fails here rather than mid-rep. If your suite legitimately needs a
third-party package, it belongs in `SETUP.md`.

### `make check-log`
Validates `logs/log.tsv`: header, field count, date order, known modules, variants
that exist in that kata's `VARIANTS.md`, and `y`/`n` for the clean column. It takes
its module and variant lists from the filesystem, so adding a kata needs no change.

Mostly this catches rows you added by hand — Mimic sessions and project hours.

### `make check-calendar`
Proves the schedule holds together: nothing scheduled that is never built, nothing built
that is never scheduled, no variant named that does not exist, no kata on disk that is
unscheduled, no stale exemption, no Sunday so long it will not realistically happen, no
kata whose target time is longer than the block it is scheduled into, and no kata that
owns a capability's evidence bar without enough slots to reach it. Also prints the whole
derived build plan.

### `make check-coverage`
Proves `plan/INTERVIEW_REQUIREMENTS.md` and `plan/COVERAGE.md` describe exactly the same
set of capabilities — every one in the spec has a row in the map and vice versa, each
group numbered from 1 with no gaps — and that none is orphaned. The count is not
hardcoded anywhere, which is the point: a row deleted from either file is a CI failure
rather than a quietly smaller total.

### `make check-decks`
Every capability tag on a deck card names a real capability, no card is missing its trap,
no field contains a stray tab, and nothing whose evidence bar is the deck is left without
a card. `make decks` shows what each card is doing and which capabilities are thin.

### `make check-generated`
`plan/CALENDAR.md`, `logs/PROGRESS.md` and `logs/progress.json` are output, not source.
This regenerates each and compares, so a hand-edit fails CI instead of surviving until
the next `make calendar` silently reverts it.

---

## Build extras

| Command | What it does |
|---|---|
| `make debug MODULE=x` | `-g -O0` build for gdb, sanitizers still on. Does not run it |
| `make analyze` | `gcc -fanalyzer` — finds bugs without running. Advisory, not gating |
| `make valgrind MODULE=x` | Second opinion on memory, sanitizers off (they conflict) |
| `make list` | Which katas have an implementation, which are scaffolded |
| `make check` | Every check CI runs, in one command |
| `make decks` | What each deck card is doing, and which capabilities are thin |
| `make clean` | Removes `build/` |

---

## What writes what

| File | Written by | Committed |
|---|---|---|
| `logs/log.tsv` | `make done` | yes |
| `logs/splits.tsv` | `make test` + `make done` | yes |
| `logs/rehearsal.tsv` | `make rehearse` | yes |
| `logs/ai-use.tsv` | you, by hand | yes |
| `logs/design-prompts/*.md` | `make prompt`, then you | yes |
| `logs/architecture/*.md` | `make design`, then you | yes |
| `logs/bughunt.tsv` | `make hunt-done` | yes |
| `logs/PROGRESS.md`, `logs/progress.json` | `make progress` | yes |
| `logs/WEEKLY_REVIEW.md` | you, Sundays | yes |
| `plan/CALENDAR.md` | `make calendar` | yes |
| `practice/katas/*/NOTES.md` | `make done` | yes |
| `practice/decks/*.tsv` | `make card` | yes |
| `practice/decks/.state.json` | `make review` | **yes — a card's box is the evidence bar for the E group and Y1, so it is proof, not preference** |
| `logs/.drill_state.json` | `make drill` | no — one rep in flight |
| `logs/.start_date` | you, once | no — yours, not the repo's |
| `practice/katas/*/src/` | you, every rep | **no — deleted every rep, on purpose** |
| `logs/.snapshots/` | `make done` | no — fuel for `make hunt` |
