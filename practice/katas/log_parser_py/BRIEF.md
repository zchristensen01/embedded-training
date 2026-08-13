# Kata 14 — log_parser_py

> **Before your first rep you owe this module its test suite** in `tests/`, in pytest,
> written by you. `make drill` refuses a module whose tests do not exist. Frozen once
> written: you do not edit it during a rep, only your `src/`, which is deleted each time.
> See [DAILY.md](../../../DAILY.md#build-sessions).

## What it is
Read a telemetry log that does not fit in memory. Answer a question about it. Exit with the
right code. That is the entire shape of the reported T&I live-coding task, and of the SpaceX
telemetry take-home.

## Why firmware test needs it
This is the one that gets asked live, under observation, with someone watching you type — and
it is the format your own diagnosis says is your weak point. Tesla's reported live task was
strings parsing on Coderpad; the SpaceX take-home is telemetry processing. A published company
take-home (Aquatic's) **fails candidates outright for calling `readlines()`**, which tells you
the memory constraint is graded, not decorative.

**Evidence bar for Y3** — three consecutive clean reps at 20 minutes, across three variants.

## The API you implement
```python
def scan(lines: Iterable[str]) -> Report:
    """One pass. O(1) memory. Never materialise the input."""

def main(argv: list[str]) -> int:
    """0 = all readings in range, 1 = a violation, 2 = bad input."""
```

## How to think about it
- **Iterate the file object.** `for line in f` streams; `f.readlines()` and `list(f)` do not.
  If the file is 2 GB, the difference is the whole exercise.
- **One pass, carrying state.** "Left the range for more than 100 ms" needs the timestamp the
  excursion started, not a list of every excursion. Decide what you must remember and keep
  only that.
- **Get the edges right.** Which comparison opens a violation and which closes it, and whether
  the boundary value itself is in or out. Write that down before you type.
- **Exit codes are part of the answer.** CI reads them. A script that prints "FAIL" and exits
  0 has reported a pass.
- **Malformed lines are normal.** A log from real hardware has a truncated final line.

## What to test
- A value that touches the boundary exactly, from both directions.
- An excursion shorter than the window, and one exactly at it.
- An excursion still open when the file ends.
- A truncated final line, a blank line, a line with the wrong field count.
- An empty file, and a file with only a header.
- Memory: feed a generator of a million lines and assert it completes — a `readlines()`
  implementation will not.

## Interview questions this lets you answer from experience
How would you find X in a file bigger than RAM · what does your script exit with and why ·
how do you handle a malformed record · walk me through parsing this telemetry · how would you
test a parser.
