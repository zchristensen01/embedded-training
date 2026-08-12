# The practice system

How this repo makes practice repeatable, forced, and recorded. Mimic is not discussed here — see
`plan/COVERAGE.md` for the split.

---

## Four formats, because "practice" is not one thing

| Format | Repeatable? | Mechanism | Recorded in |
|---|---|---|---|
| **A. Katas** | Infinitely | Frozen tests + gitignored `src/` + variants | `logs/log.tsv` |
| **B. Concepts** | On a schedule | Leitner spaced repetition, spoken aloud | `practice/decks/.state.json` |
| **C. Design prompts** | With fresh subjects | Rotating subject list, fixed rubric | `logs/design-prompts/` |
| **D. Projects** | **No. One-shot.** | Artifact + README + rehearsed story | The repo itself |

Only A, B, and C repeat. D does not, and trying to drill it wastes time — its value is the
artifact and the story.

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

**1. Variants.** Same kata, different constraint, own test file. `ring_buffer` has six: count-based
full/empty, sacrificial slot, power-of-two masking, overwrite-oldest, ISR-safe single-producer
single-consumer, and generic element size via `void*`. You cannot muscle-memory six.

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

**3. Falling time targets.** A kata that's comfortable at 40 minutes is a different exercise at 12.

### Phase splits — the diagnosis

A total time tells you whether you're getting faster. It doesn't tell you *what* is slow. Call
`make lap` at each transition during a rep and you get that:

| Phase | From | To |
|---|---|---|
| `design` | `make drill` | the first line of code you type |
| `write` | first line | your first compile attempt |
| `compile` | first compile attempt | it compiles clean |
| `debug` | clean compile | tests pass |

`make done` prints the breakdown and writes it to `logs/splits.tsv`. `make report` aggregates it
and, once you have enough reps, compares your first reps against your recent ones.

**How to read it:**

- **`design` dominates** — you don't know the pattern. Reread the BRIEF and draw the invariant on
  paper before starting the clock next time.
- **`write` dominates** — this is the syntax-fluency gap, the one you set out to fix. It should
  shrink faster than any other phase.
- **`compile` dominates** — syntax errors, not logic. Type 20% slower on the first pass; it
  usually beats three compile cycles.
- **`debug` dominates** — logic and edge cases. Write the test you'd add *before* the
  implementation on the next rep.

**`write` + `compile` combined is your syntax fluency in one number.** Watch it fall. Under 40%
by week 10 is the target.

Missing a lap call isn't a problem — `make done` attributes whatever is left to the next phase in
sequence. Skipping laps entirely just means you get totals without the diagnosis.

### Selection — you don't get to choose

`make drill` picks by: worst recent time first, then longest since last rep, then never attempted.
It won't repeat a kata within three days if alternatives exist. This is deliberate — left to
choose, you'd avoid `pool_allocator`.

### Retirement

A kata drops to maintenance rotation (once a fortnight) after **three consecutive clean reps at
target time, across three different variants.** Not before.

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

The 56 cards that ship here do not cover all 78 capabilities and are not meant to: C is
katas, B is rehearsal, and most of H is Mimic's bench work. The deck covers roughly the E
group plus most of T. S3's encoder interrupts and S10's anti-windup will each produce two
or three cards of their own — write them the same day, while you still remember which part
actually caught you.

---

## Format C — Design prompts

"How would you test this" is the highest-frequency test & integration question and the one
candidates most often fail. It repeats because the **subject rotates** and the **rubric is fixed**.

`make prompt` draws one of 40 subjects and starts a 10-minute clock. Write into
`logs/design-prompts/`, then score against the eight-category rubric already in the generated file.

Your score across 40 different subjects is a real measurement of one skill. Two automatic
failures regardless of score: proposing solutions before asking for requirements, and stopping
before you're told to stop.

---

## Format D — Projects

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
appearing under "explanations" three times a day in week 6, you've drifted. The count should fall.

---

## Measurement — real progress vs the feeling of it

`make report` gives four numbers:

1. **Time curve per kata.** Should fall, then flatten. Flat from the start means the kata is too
   easy. Never falling means you're reading an old solution somehow.
1b. **Phase breakdown.** `write` + `compile` as a share of total. This is the number that most
   directly measures the gap you're fixing.
2. **Clean-first-compile rate.** The best single proxy for syntax fluency. Above 40% by week 4,
   above 55% by week 6, above 70% by week 10.
3. **Reps per week.** Consistency beats intensity. Five is the target.
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
| Phase splits: design, write, compile, debug | `logs/splits.tsv` | `make lap` + `make done` |
| One design decision or bug per rep | `practice/katas/*/NOTES.md` | `make done` |
| Every AI use | `logs/ai-use.tsv` | you, by hand |
| Deck scheduling and box state | `practice/decks/.state.json` | `make review` |
| Design prompt answers and rubric scores | `logs/design-prompts/` | `make prompt`, then you |
| Weekly honesty check | `logs/WEEKLY_REVIEW.md` | you, Sundays |
| Mimic sessions | `logs/log.tsv` with `module=mimic`, variant = session ID | you, by hand |

Commit all of it. The commit history is the second record, and it's the one a hiring manager can
see.
