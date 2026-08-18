# Kata 14 — log_parser_py

**In one sentence.** Read a telemetry log that does not fit in memory, answer one question
about it, and exit with the right code.

---

> **Before your first rep you owe this module its test suite** in `tests/`, in pytest,
> written by you. `make drill` refuses a module whose tests do not exist. Frozen once
> written: you do not edit it during a rep, only your `src/`, which is deleted each time.
> See [DAILY.md](../../../DAILY.md#build-sessions).

## The problem, in plain language

A device logged for eight hours at 100 Hz. The file is 2 GB. The question is *"did any
reading leave its valid range for more than 100 ms?"*

The obvious solution is to read the file, then look through it. That fails, and it fails in
a way that gets you rejected rather than debugged.

```python
   data = f.readlines()        # loads all 2 GB into RAM. Machine swaps, or dies.
   rows = [parse(l) for l in f]  # same thing wearing a different hat

   for line in f:              # reads ONE line at a time. Constant memory.
       ...                     # 2 GB or 2 TB, it does not care.
```

A published company take-home **fails candidates outright for calling `readlines()`**, which
tells you the memory constraint is graded rather than decorative.

### The one genuinely interesting question

**What do you actually have to remember?**

The question is "did a reading stay out of range for more than 100 ms". The naive approach
collects every out-of-range reading into a list and measures the list afterwards — which is
back to holding the file in memory, just filtered.

You don't need the excursions. You need *one timestamp*: when the current excursion started.

```
   value
     │
 max ├────────────────────────────────────────────────
     │        ╭────────╮              ╭──────────────╮
     │   ╭────╯        ╰────╮    ╭────╯              ╰───
     │───╯                  ╰────╯
 min ├────────────────────────────────────────────────
     │
     └──────────────────────────────────────────────────▶ time
              ▲        ▲              ▲              ▲
              │        │              │              │
         start=t1   in range      start=t2       in range
         (remember  → is t−t1 >   (remember      → is t−t2 >
          t1)         100ms?)      t2)            100ms?)

   state carried between lines:  ONE optional timestamp.
   memory used:                  the same for a 10-line file and a 10-billion-line file.
```

That is the shape of every streaming problem: **decide what state the answer needs, carry
only that, throw the line away.** Being able to say "I only need the start of the current
excursion, so it's O(1) memory" out loud is the answer to the follow-up question, and the
follow-up question is always asked.

### The second thing that gets marked: exit codes

This runs in CI. CI does not read your lovely output; it reads one integer.

```
   exit 0  →  all readings in range        CI goes green
   exit 1  →  a violation was found        CI goes red, correctly
   exit 2  →  bad input, could not tell    CI goes red, differently
```

**A script that prints "FAIL" and exits 0 has reported a pass.** Distinguishing 1 from 2
matters too: "the device misbehaved" and "you gave me a corrupt file" need different humans
to look at them, and conflating them is how a broken test rig quietly reports green for a
week.

---

## Why firmware test needs this

This is the one that gets asked **live, under observation, with someone watching you type**.
Tesla's reported live task was string parsing on Coderpad; the SpaceX take-home is telemetry
processing. It is the single most common shape of the T&I live-coding round.

It is also the format the research says is the weak point for someone coming from web work —
not because the logic is hard, but because doing it cold, in twenty minutes, while narrating,
is a different skill from doing it well over an afternoon.

**Evidence bar for Y3** — three consecutive clean reps at 20 minutes, across three variants.

---

## What you need from Python

**A file object is already an iterator over lines.** This is the whole trick:

```python
   with open(path) as f:
       for line in f:          # streams, one line at a time
           ...
```

`f.readlines()`, `list(f)` and `f.read().split('\n')` all materialise the file. Learn to see
those three as the same mistake.

**Generators are how you build a pipeline without materialising it.** A function with
`yield` in it returns a lazy sequence — nothing is computed until something asks for the next
item:

```python
   rows = (parse(l) for l in lines)      # generator expression, () not []
   rows = [parse(l) for l in lines]      # list comprehension — builds the whole list
```

One character of difference, unbounded difference in memory. This is a favourite interview
question precisely because the code looks nearly identical.

**Take `Iterable[str]`, not a filename.** `scan` accepting *lines* rather than a path is what
makes it testable: your tests pass a list, or a generator of a million fabricated lines, with
no file on disk. That decision — the seam between "get the data" and "process the data" — is
a design point worth being able to defend.

**A generator is consumed once.** Iterate it twice and the second pass sees nothing. If your
tests are mysteriously empty on the second assertion, this is why.

---

## The API you are writing

```python
def scan(lines: Iterable[str]) -> Report:
    """One pass. O(1) memory. Never materialise the input."""

def main(argv: list[str]) -> int:
    """0 = all readings in range, 1 = a violation, 2 = bad input."""
```

- **`scan` does the work and returns a summary**, not a print. Keeping it pure means the
  tests assert on a value rather than capture stdout, and stdout capture in tests is a smell.
- **`main` takes `argv` as a parameter** rather than reading `sys.argv`. Same reason: your
  tests call `main(['--max', '50', 'file.log'])` directly, with no subprocess. This is a small
  decision that makes the whole thing testable, and an interviewer will notice it.
- **`Report`** is yours to define — a dataclass or a NamedTuple. Whatever answers the
  question plus enough context to explain it: how many lines were read, how many were
  malformed, the worst excursion.

**Malformed lines are normal, not exceptional.** A log from real hardware has a truncated
final line, because the power was cut mid-write. It has blank lines. It may have a line with
the wrong field count where two writers interleaved. Decide — and write in `NOTES.md` —
whether a bad line is skipped-and-counted or fatal. Both are defensible; silently ignoring
them is not, because "we processed 4 million lines" with no mention that 40,000 were garbage
is a false report.

---

## The contract I decided

> Transcribed from `tests/test_log_parser_py.py`, which is the only thing that enforces it —
> there is no header for a Python kata. Read this section at the start of a rep.

### Types

```python
Report   # dataclass or NamedTuple
  .violated: bool   # did any excursion reach the window?
  .worst_ms: int    # longest excursion seen, in ms. 0 if none
```

### Functions

```python
def scan(lines: Iterable[str], max_ok: int, window_ms: int) -> Report
def main(argv: list[str]) -> int
```

`scan` takes **lines, not a path** — that is what lets the suite feed it a generator of a
million fabricated lines with no file on disk. `main` is the only thing that opens a file.

Line format is `timestamp_ms,value`. Two fields, no header row.

### What no signature can say

| Question | My answer |
|---|---|
| What does failure look like? | `main` returns an exit code: `0` all readings in range, `1` a violation was found, `2` bad input. `scan` does not fail — malformed input is `main`'s problem. |
| What is left untouched when it fails? | N/A — nothing is mutated in place. `scan` is pure. |
| Preconditions, and what happens if they don't hold | A reading is **out of range when `value >= max_ok`** (so `50` violates `max_ok=50`). A violation is **`duration >= window_ms`** — an excursion exactly at the window counts. |
| Ownership and lifetime | `lines` is consumed once. It may be a generator, and `scan` must never materialise it — one pass, O(1) memory, no `readlines()`. |
| Safe to call concurrently? | Single-threaded. Not a consideration for this kata. |
| The invariant that holds after every call | `scan` reads each line exactly once and holds only the start timestamp of the current excursion, so memory is constant in the size of the input. |

**Decisions the tests pin down, spelled out:**

- An excursion still **open when the input ends counts**, measured from its start to the last timestamp seen.
- Duration is `closing timestamp - opening timestamp`.
- A **malformed line is fatal**, not skipped-and-counted: truncated (`"30,"`), blank, or wrong field count (`"10,53,100"`) all make `main` return `2`.
- An **empty file returns `2`**, and so does a file containing only a header row — the format has no header, so `timestamp,value` is just an unparseable line.
- `argv` is **positional and excludes the program name**: `[max_ok, window_ms, path]`, all strings — e.g. `main(["50", "20", "/tmp/telemetry.log"])`.

## How to think about it

Don't write code yet. Answer these on paper:

1. Write down the exact state your loop carries between lines. If it is more than two or
   three small values, you are collecting rather than streaming.
2. Which comparison *opens* a violation and which *closes* it? Is the boundary value itself
   in range or out? Write it down — this is where the off-by-one lives.
3. The file ends while an excursion is still open. Does that count? (Decide, then test it
   either way.)
4. What is `main`'s exit code when the file has 1000 good lines and 1 unparseable one? Justify
   it.
5. State the invariant: *`scan` reads each line exactly once and never holds more than a
   fixed number of them.* Your million-line test is that invariant.

Then write it. It is about 40 lines.

---

## Tests it must pass

| Test | What it's protecting against |
|---|---|
| A value that touches the boundary exactly, from both directions | The `<` vs `<=` decision you wrote down in step 2 |
| An excursion shorter than the window, and one **exactly** at it | The other off-by-one |
| An excursion still open when the file ends | The case everyone forgets, because the loop is where the logic lives |
| A truncated final line, a blank line, a line with the wrong field count | Real logs. All three occur |
| An empty file, and a file with only a header | The degenerate cases |
| **Memory: feed a generator of a million lines and assert it completes** | This is the test that fails a `readlines()` implementation, and it is the point of the kata |

That last one is the most valuable test here. Write it as a generator expression that
fabricates lines on the fly — no file, no memory — and a streaming implementation finishes in
a second while a materialising one grinds. **Write that test first**, before the
implementation, and it will keep you honest under time pressure.

---

## Once it's boring

*Boring* means: blank file to working, tests green first run, in under twenty minutes, never
unsure what to type next. Then add a constraint.

**Second pass — multiple channels.** The log interleaves readings from eight sensors, each
with its own valid range, and the question becomes "which channels violated, and for how
long". Your O(1) state becomes O(channels) — which is still constant in the file size, and
saying *that* precisely is the skill.

**Third pass — a streaming pipeline.** Restructure into composed generators: `lines →
parsed → filtered → violations`, each a small generator function. It reads beautifully and
stays O(1). Then work out what you gave up (you can no longer look backwards) and when you
would not do it.

---

> **Variants:** seven, `v1` through `v7`, written up in [VARIANTS.md](VARIANTS.md).
> `make drill` picks one and `make done` logs the rep to
> [logs/log.tsv](../../../logs/log.tsv). Time is only comparable within a variant.

## Interview questions this lets you answer from experience

How would you find X in a file bigger than RAM · what does your script exit with and why ·
how do you handle a malformed record · walk me through parsing this telemetry · how would you
test a parser · generator vs list comprehension and when it matters.
