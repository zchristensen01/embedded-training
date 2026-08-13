# Kata 13 — binary_frame_py

> **Before your first rep you owe this module its test suite** in `tests/`, in pytest,
> written by you. `make drill` refuses a module whose tests do not exist. Frozen once
> written: you do not edit it during a rep, only your `src/`, which is deleted each time.
> See [DAILY.md](../../../DAILY.md#build-sessions).

## What it is
The host side of a wire protocol. Given bytes off a serial port, produce structured values —
and refuse, loudly, anything malformed. The firmware half of this problem is
`protocol_parser`; this is the same problem seen from the test harness.

## Why firmware test needs it
Binary telemetry handling is the daily work of a test engineer at a space or aerospace firm,
and it is where the generic Python prep material is useless. Job postings name it constantly;
SpaceX's reported take-home includes parsing a custom binary protocol.

It is also where Python's quiet failures live. Every bug in this kata is silent: a byte-order
mismatch does not raise, it returns plausible numbers. A missing length check does not raise
until the buffer is short. Wrong signedness turns −10 into 65526, which looks like data. You
will not be saved by an exception, so you have to write the check.

**Evidence bar for Y2** — three consecutive clean reps at 20 minutes, across three variants.

## The API you implement
```python
def decode(buf: bytes) -> dict:
    """One frame -> its fields. Raise FrameError on anything malformed."""

def frames(chunks: Iterable[bytes]) -> Iterator[dict]:
    """A stream of arbitrary read() chunks -> complete frames only."""

class FrameError(Exception):
    ...
```

## How to think about it
- **Say the byte order out loud, every time.** No prefix means native order *and* native
  alignment. `<` and `>` mean fixed sizes and no padding. Matching a wire format with `@` is
  the classic bug: the first field decodes correctly and everything after it misaligns, so it
  looks nearly right.
- **A read is a stream chunk, not a message.** `ser.read(n)` returns *up to* n bytes. On a
  loaded bus you get half a frame, or two. Accumulate into a buffer, pop complete frames,
  keep the remainder.
- **Validate the declared length against what remains before you slice.** A length field is
  attacker-controlled in the general case and garbage-controlled in the real one.
- **Signed vs unsigned is a decision, not a default.** `h` and `H` read the same bits.

## What to test
- Round-trip: `decode(encode(x)) == x` for every field at its limits.
- A frame one byte short, and one byte long.
- A declared length that overruns the buffer.
- A negative value in a signed field, and the same bits read unsigned.
- A sync byte appearing inside a payload — proves you are length-driven, not delimiter-driven.
- Chunk boundaries falling in every position within a frame.
- Bad CRC, if your variant has one.

## Interview questions this lets you answer from experience
Why did `struct.unpack` give different numbers on two machines · what do you check before
unpacking a frame off a port · how do you reassemble frames across read boundaries · how would
you fault-inject this · what happens when the length field lies.
