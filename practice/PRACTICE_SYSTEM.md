# The practice system

How this repo makes practice repeatable, forced, and recorded. Mimic is not discussed here — see
`plan/COVERAGE.md` for the split.

---

## Seven formats, because "practice" is not one thing

| Format | Repeatable? | Mechanism | Recorded in |
|---|---|---|---|
| **A. Katas** | Infinitely | Frozen tests + gitignored `src/` + variants | `logs/log.tsv` |
| **B. Concepts** | On a schedule | Leitner spaced repetition, spoken aloud | `practice/decks/.state.json` |
| **C. Design prompts** | With fresh subjects | Rotating subject list, fixed rubric | `logs/design-prompts/` |
| **D. Architecture drills** | With fresh prompts | Rotating prompt list, a *different* fixed rubric | `logs/architecture/` |
| **E. Bug hunts** | After any rep you keep | Your own old solution, silently mutated | `logs/bughunt.tsv` |
| **F. Rehearsal** | Until it's tight | Re-tell one story to three strong takes | `logs/rehearsal.tsv` |
| **G. Projects** | **No. One-shot.** | Artifact + README + rehearsed story | The repo itself |

A through F repeat. G does not, and trying to drill it wastes time — its value is the artifact
and the story.

---

## Format A — Katas

### The mechanism that makes a solved kata practisable again

```
katas/ring_buffer/
├── BRIEF.md      committed   what it is, the API, how to think about it, what to test
├── VARIANTS.md   committed   the variants the drill tool draws from
├── NOTES.md      committed   one design decision + one bug, appended every rep
├── include/      committed   the API contract. FROZEN. Not edited during a rep
├── tests/        committed   the test suite. FROZEN. Not edited during a rep
└── src/          GITIGNORED  your implementation. DELETED before every rep
```

`.gitignore` holds `practice/katas/*/src/`.

`make drill` deletes `src/`, writes an empty stub containing only the include line, and starts a
timer. **Every rep is a genuine cold start, because your previous solution does not exist.** The
expensive artifacts — the contract and the tests — are permanent. Your implementation is
disposable.

What accumulates across reps is the *lesson* and the *time*, not the code. That's correct.

### Where the variability comes from

Three sources that multiply:

**1. Variants.** Same kata, different constraint. Every module has at least seven, written up in its
`VARIANTS.md` — `ring_buffer`'s run from count-based full/empty through lock-free
single-producer/single-consumer, power-of-two masking, overwrite-oldest, generic element size,
bulk transfer, and peek. You cannot muscle-memory seven.

**2. Constraint cards.** Drawn automatically about a third of the time, applied on top of any
variant:

```
no dynamic allocation
single return per function, no goto
2 KB RAM budget, stated in a header comment
add peek() without breaking the frozen tests
must be safe against a single-producer ISR
zero branches in the hot path
no standard library at all
write it on paper first, then type it in
name every variable in full words
write the test you'd add before the implementation
```

The paper one matters more than it looks. Whiteboard rounds still exist and paper removes
autocomplete entirely.

A Python rep draws from a different deck, because half of that list is unobeyable in Python —
there is no `goto` to forbid and no allocation to avoid. Its cards are stdlib-only, O(1)
memory, no bare `except`, type-annotate everything, and *say the byte order out loud before
you type the format string*.

**3. Falling time targets.** A kata that's comfortable at 40 minutes is a different exercise at 12.

### Phase splits — the diagnosis

A total time tells you whether you're getting faster. It doesn't tell you *what* is slow. Three
phases do:

| Phase | From | To | Closed by |
|---|---|---|---|
| `write` | `make drill` | your first `make test` | `make test` |
| `compile` | first `make test` | it compiles clean | `make test` |
| `debug` | clean compile | tests pass | `make done` |

A Python kata has no compile step, so its second phase is **`run`** — from your first
execution attempt to the point where it runs without a syntax or import error. Same position
in the sequence, same meaning: the gap between having typed something and the machine
accepting it. Everything picks the right set from the module name.

**You don't lap any of this by hand.** Both boundaries `make test` can observe, it closes:
`write` when you invoke it, and `compile`/`run` when the build or the import succeeds. That
second one fires on *acceptance*, not on passing — a failing assertion means your code ran,
so you're debugging; a compile error or an `ImportError` means it didn't, and you stay put
until the next `make test` gets further. `make lap` remains for a rep you drive by hand and
always overrides.

**There is no `design` phase, deliberately.** It measured reading the BRIEF — real work
exactly once per module, and a glance at one signature thereafter. Across the reps that make
up the bulk of the plan it was a near-zero column that still had to be lapped, and a missed
lap doesn't lose a little precision, it moves minutes into `write`. Read the BRIEF and the
variant line first; the clock starts at the keyboard.

`make done` prints the breakdown and writes it to `logs/splits.tsv`. `make report` aggregates it
and, once you have enough reps, compares your first reps against your recent ones.

**How to read it:**

- **`write` dominates** — this is the syntax-fluency gap, the one you set out to fix. It should
  shrink faster than any other phase.
- **`compile` dominates** — syntax errors, not logic. Type 20% slower on the first pass; it
  usually beats three compile cycles.
- **`run` dominates** (Python) — imports, indentation, typos. The same claim as `compile`.
- **`debug` dominates** — logic and edge cases. Write the test you'd add *before* the
  implementation on the next rep. If the failure is silent — a wrong answer with no sanitizer
  report — stop re-reading your own code and open the debugger: `make debug MODULE=x`, then
  `gdb build/x-debug`. See [`../reference/GDB.md`](../reference/GDB.md).

**`write` + `compile` combined is your syntax fluency in one number** (`write` + `run` for a
Python rep). Watch it fall. Under 40% by week 14 is the target.

### Selection — the default chooses, you can always override

`make drill` with no arguments picks by: worst recent time first, then longest since last rep,
and a module one good rep from its bar gets a nudge up that order. A module you have never
attempted comes last, because the rotation already schedules its first rep. It won't repeat a
module within three days if alternatives exist. That default is deliberate — left to choose every day, you'd avoid
`pool_allocator` for fourteen weeks.

**But nothing stops you choosing.** `make drill KATA=fsm` runs `fsm` right now, whatever the
calendar says, and picks the variant you've done least recently. `make drill KATA=fsm VARIANT=v4`
pins both. Swapping the assigned module for one you know you're worse at is not cheating the
system, it is using it — the score comes from `logs/log.tsv`, which records what you *did*, not
what the calendar asked for. The calendar is a default, not a gate.

The one thing that does refuse you is a module with no frozen header and test suite. A rep
against an empty suite isn't a rep, so `make drill` will tell you what you owe it instead.

Two things to watch if you free-play a lot:

- **`make report` flags what you're avoiding** — anything untouched for 14 days, and anything
  never attempted. That is the honest counterweight to choosing your own reps.
- **Spread the variants.** Doing `v1` six times is one exercise done six times. Leaving `VARIANT=`
  off handles this for you: it picks the one you've gone longest without.

### When a module has met its bar

A module has met its bar after **three consecutive clean reps at target time, across three
different variants.** Not before.

**"Met" does not mean "stop".** Nothing locks, nothing is removed from the rotation, and the
calendar keeps scheduling it. All it means is that the capability resting on that module is now
proved by the log rather than by how you feel about it — `make progress` flips it to **met** and
`make log` prints *bar met* beside the module. Keep drilling it if you want to; a module you can
do cold in eight minutes is a nice way to start a session.

`tools/progress.py:kata_retired()` is that rule in code. Two consequences worth knowing:
consecutive means one bad rep resets the count, and every module that owns a capability's bar is
scheduled with at least three slots ending in three different variants — `make check-calendar`
fails if that stops being true. Saturday's adaptive rep is the slack that lets you recover from
a bad one.

---

## Format B — Concepts

`make review` runs a five-box Leitner schedule over `practice/decks/*.tsv`. Box N returns after 2^(N-1)
days: 1, 2, 4, 8, 16. Right answer moves up a box; wrong drops to box 1.

**Two non-negotiable rules:**

1. **Answer out loud, in full sentences, before revealing.** Not in your head. The interview
   failure mode is knowing the answer and not being able to structure it aloud. If you can't
   speak, skip the session rather than doing it silently.
2. **A card is correct only if you also said the trap.** Every card carries a `trap` field.
   "A mutex has ownership, a semaphore is signalling" is a pass. Adding "and the classic wrong
   answer is that they're the same but semaphores count higher" is what an interviewer hears as
   expertise.

**Add a card whenever a kata rep or a Mimic session surprises you.** `make card` does it
in about twenty seconds: it shows the topics already in use so they stay consistent, warns
if a similar question already exists, and refuses a card with no trap — a card without the
wrong answer on it is worth much less than one with it. `make done` offers the same prompt
at the end of every rep, which is the moment you are most likely to have been caught out.

The cards that ship here do not cover every capability and are not meant to: C is katas, B is
rehearsal, and part of H is bench work. The deck is the evidence bar for the whole E group,
most of T, and Y1 — `make decks` prints which capabilities it carries and which are resting on a single
card. Some cards are tagged with a capability scored some other way; those are reinforcement,
they are labelled as such, and `make check-decks` will fail on a tag that names no capability
at all. S3's encoder interrupts and S10's anti-windup will each produce two or three cards of
their own — write them the same day, while you still remember which part actually caught you.

---

## Format C — Design prompts

"How would you test this" is the highest-frequency test & integration question and the one
candidates most often fail. It repeats because the **subject rotates** and the **rubric is fixed**.

`make prompt` draws one of 60 subjects and starts a 10-minute clock. Write into
`logs/design-prompts/`, then score against the eight-category rubric already in the generated file.

Your score across 60 different subjects is a real measurement of one skill. Two automatic
failures regardless of score: proposing solutions before asking for requirements, and stopping
before you're told to stop.

---

## Format D — Architecture drills

`make design` draws one of 8 prompts and starts a 45-minute clock. You produce a labelled
block diagram with numbers on it, then argue against your own design and answer yourself.

**This is not Format C with different words.** A design prompt hands you a finished object and
asks how you would test it. An architecture drill asks you to invent the object. Candidate
reports put it as a dedicated round at Google and Meta Reality Labs, and as a design item
inside Tesla's and Medtronic's take-homes — and nothing else here produces it, because katas
start from a written contract and design prompts start from a thing that already exists.

Both rubrics are out of 16 so one parser reads either. They are different rubrics. The
architecture one scores six axes the interviewer is actually grading — ISR/main partitioning,
memory budget, comms topology, power states, failure handling, testability — plus two gates:
asking for constraints before drawing, and holding your position under one round of pushback.

The subject rotates and the rubric does not, which is what makes it repeatable. E30 is met at
three scored 12+/16. The out-loud defence logs separately as a B11 rehearsal take.

---

## Format E — Bug hunts

`make hunt` takes a solution *you* wrote on an earlier rep, silently mutates one line, and
starts a clock. You find it.

Every other format here starts from an empty file. Real take-homes do not: Tesla's is reported
to hand you a broken C module and ask you to find the errors, and Intel runs a dedicated
debug round. This is the closest thing here to that, and it uses your own old code because a
corpus of broken C written by an AI would be an AI-written exercise — which the rules below
forbid for good reason.

**Be clear about what it is not.** The code is yours, so you are diffing against your own
memory rather than reading a stranger's intent out of their assertions — a related skill and
the easier one. `plan/INTERVIEW_REQUIREMENTS.md` lists "making a suite of red tests green" as
still open for exactly this reason, and the weeks 13–14 mock take-homes are the only exposure.
`make hunt` is also not on the calendar on purpose: it needs a snapshot of a rep you have
already done, so it belongs to free practice. Run it when `make snapshots` shows something a
few weeks old — that is when it stops being code you remember.

Mutations are chosen to be *silent*: a `<` becomes `<=`, a `volatile` disappears, a struct
format's endianness prefix flips. None of them raise. `make hunts` shows which kinds keep
catching you, and that list is a reading list.

**This is the debugger exercise, and the only one.** Because nothing raises, there is no
sanitizer report naming a file and a line — which is exactly the condition gdb is for and
exactly what a normal kata rep never produces. `make hunt` builds the `-g -O0` binary for
you and prints the invocation; `make hunt-done` then asks whether you found it by stepping
or by reading, and `make hunts` reports the split. Both routes are legitimate, but only one
of them transfers to a codebase you did not write, which is the point of the exercise.
[`../reference/GDB.md`](../reference/GDB.md) is the twelve commands worth knowing.

---

## Format F — Rehearsal

The B group: eleven narrative capabilities, in `practice/rehearsal/STORIES.md`. The research is
blunt that test-and-integration candidates fail the behavioural round *more often* than the
technical one, which makes this the least optional part of the plan and the easiest to skip.

`make rehearse` draws the story with the fewest strong takes, times it, and asks for a rating.
A story is **ready at three takes rated strong, on three different days** — three takes in one
afternoon is one rehearsal, not three, and the point is that the story survives a gap.
`tools/rehearse.py:ready()` is the single definition of that; `make progress` imports it rather
than keeping a second opinion.

Eleven stories at three takes each is thirty-three takes **rated strong**. The calendar
schedules three on Sunday and one on Saturday from week 3 on, rising to two on Saturday from
week 11, plus the takes inside the weeks 12, 13 and 14 main blocks.

**Do not take that number on trust.** It stopped closing once, silently, when B11 was added to
a schedule sized for ten stories and nothing recounted. `make check-calendar` now proves it:
check #9 reads the story list out of `STORIES.md`, multiplies by three, and fails the build if
the calendar schedules fewer takes than that. Add a story and the check tells you to add slots.

Two things that check cannot do for you. It counts takes *scheduled*, not takes rated strong,
so the total only closes the bar if roughly three in four land — `make check-calendar` prints
the implied rate as a note whenever the margin gets thin, and the shortfall, if there is one,
comes out of free practice. And it once under-counted in the other direction: the late-week
takes were written as prose rather than `xN`, so three takes read as one and the calendar
looked thinner than it was. Both halves of that are why the totals are derived and printed
rather than typed into this paragraph.

Fill in `STORIES.md` before the first take; an unwritten story wanders.

Record every third take and watch it back. You cannot hear your own filler.

## Format G — Projects

Not repeatable. Do it once, properly, and extract three things: a public repo with a README that
states design decisions, three to five rehearsed answers to "walk me through a project," and a
written account of **how you tested it** — that last one is what converts a build into a test &
integration interview answer.

Log project hours with `module=project`. Don't expect a time curve.

---

## Rules for using AI

> **AI writes infrastructure. You write everything that gets interviewed.**

### AI may write

Makefiles, CI YAML, shell scripts, the tooling in `tools/`, assert macros and test *runners* (the
plumbing that reports pass/fail), explanations of a concept, reviews of code you already got
passing, and explanations of an error you've already stared at for five minutes.

### AI must not write

- **Any test case.** Not one. "How would you test this" is a top-three question in both tracks. If
  AI writes your tests, you have no answer to it.
- Any kata implementation, at any point, including "just show me the pattern once."
- Any project firmware or harness code you'll put on your resume.
- Anything during a take-home unless explicitly permitted. Assume you'll defend it live — Tesla,
  SpaceX, and Kraken all follow up on their assessments.

### The close-the-tab rule

After any AI explanation: close it, wait five minutes, reimplement from scratch with no reference.
Can't? You didn't learn it. The feeling of understanding while reading is not recall, and that
gap is the whole reason this repo exists.

### The log

`logs/ai-use.tsv` — one line per use: date, what for, which rule. Reviewed weekly. If lines are
appearing under "explanations" three times a day in week 8, you've drifted. The count should fall.

---

## Measurement — real progress vs the feeling of it

`make report` gives four numbers:

1. **Time curve per kata.** Should fall, then flatten. Flat from the start means the kata is too
   easy. Never falling means you're reading an old solution somehow.
1b. **Phase breakdown.** `write` + `compile` as a share of total. This is the number that most
   directly measures the gap you're fixing.
2. **Clean-first-compile rate.** The best single proxy for syntax fluency. Above 40% by week 4,
   above 55% by week 8, above 70% by week 14.
3. **Reps per week.** Consistency beats intensity. The calendar schedules thirteen — eight C
   and four Python on the weekdays and Sunday, plus Saturday's adaptive one. Eleven is the
   target, because one missed day a week is real life and two is a drift.
4. **Coverage.** Which katas you're avoiding. The report flags anything untouched for 14 days.

`make stats` gives a fifth: deck box distribution. If most cards are stuck in boxes 1–2 by week 5,
you're reviewing silently or skipping the trap. Fix the method, not the schedule.

**If all five are flat and you feel like you're improving, you're not.** That is what the logs are
for.

---

## What gets recorded, and where

| Thing | File | Written by |
|---|---|---|
| Every kata rep: date, module, variant, minutes, clean, note | `logs/log.tsv` | `make done` |
| Phase splits: write, compile/run, debug | `logs/splits.tsv` | `make test` + `make done` |
| One design decision or bug per rep | `practice/katas/*/NOTES.md` | `make done` |
| Every AI use | `logs/ai-use.tsv` | you, by hand |
| Deck scheduling and box state | `practice/decks/.state.json` | `make review` |
| Design prompt answers and rubric scores | `logs/design-prompts/` | `make prompt`, then you |
| Architecture drills and rubric scores | `logs/architecture/` | `make design`, then you |
| Behavioural takes: date, story, seconds, rating | `logs/rehearsal.tsv` | `make rehearse` |
| Bug hunts: module, mutation kind, minutes, found | `logs/bughunt.tsv` | `make hunt-done` |
| Weekly honesty check | `logs/WEEKLY_REVIEW.md` | you, Sundays |
| Mimic sessions | `logs/log.tsv` with `module=mimic`, variant = session ID | you, by hand |

Commit all of it. The commit history is the second record, and it's the one a hiring manager can
see.
