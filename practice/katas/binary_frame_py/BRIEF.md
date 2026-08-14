# Kata 13 — binary_frame_py

**In one sentence.** The host side of a wire protocol: given bytes off a serial port,
produce structured values — and refuse, loudly, anything malformed.

---

> **Before your first rep you owe this module its test suite** in `tests/`, in pytest,
> written by you. `make drill` refuses a module whose tests do not exist. Frozen once
> written: you do not edit it during a rep, only your `src/`, which is deleted each time.
> See [DAILY.md](../../../DAILY.md#build-sessions).

## The problem, in plain language

A device sends you bytes. Not text — raw binary, laid out exactly as the firmware author
decided. Your job is to turn that back into numbers.

A typical frame:

```
   ┌──────┬──────┬────────┬──────────────────────┬──────────┐
   │ SYNC │ TYPE │ LENGTH │        PAYLOAD       │   CRC    │
   │ 0xAA │  1B  │   1B   │      LENGTH bytes    │   2B     │
   └──────┴──────┴────────┴──────────────────────┴──────────┘

   bytes on the wire:
   AA 03 04 E8 03 F6 FF 1C 2D
   ▲  ▲  ▲  └────┬────┘ └──┬─┘
   │  │  │       │         └─ CRC over everything before it
   │  │  │       └─────────── 4 bytes of payload: two 16-bit values
   │  │  └─────────────────── length = 4
   │  └────────────────────── type = 3 (a sensor reading, say)
   └───────────────────────── sync byte, marks a possible frame start
```

Those four payload bytes `E8 03 F6 FF` are two 16-bit integers. What they *mean* depends
entirely on two decisions the firmware made and did not tell you: which end the bytes go in,
and whether the values are signed.

### The one genuinely interesting question

**Why does the same buffer decode to different numbers on different machines?**

Because `struct.unpack` has to be told the byte order, and if you don't tell it, it uses
whatever your own CPU happens to prefer.

```python
   struct.unpack('<H', b'\xE8\x03')   #  1000   little-endian: last byte is most significant
   struct.unpack('>H', b'\xE8\x03')   # 59395   big-endian:    first byte is most significant
```

Same two bytes. Two completely plausible numbers. Neither raises an exception. **This is the
defining property of the whole kata: every bug in it is silent.**

Three format-character decisions, and each has a trap:

| Prefix | Byte order | Sizes and padding |
|---|---|---|
| *(none)* or `@` | native | native — **and it inserts padding** |
| `<` | little-endian | fixed, no padding |
| `>` or `!` | big-endian | fixed, no padding. `!` means "network order", same thing |

The trap is the first row. No prefix means native order *and* native alignment, so Python
inserts padding bytes to match how a C compiler would lay out a struct:

```python
   struct.calcsize('@BI')   # 8  — a byte, three padding bytes, then the 4-byte int
   struct.calcsize('<BI')   # 5  — a byte then the int, packed tight
```

Matching a wire format with `@` is the classic bug: the first field decodes correctly and
everything after it is misaligned, so it looks *nearly* right. **Say the byte order out
loud, every time.**

And signedness is a separate decision from byte order:

```python
   struct.unpack('<H', b'\xF6\xFF')   # 65526    H = unsigned 16-bit
   struct.unpack('<h', b'\xF6\xFF')   #    -10   h = signed 16-bit
```

`h` and `H` read the *same bits*. A temperature of −10 °C read as unsigned becomes 65526,
which looks like data, passes every range check you forgot to write, and gets logged.

Worth memorising, because it is muscle memory in an interview:

| Code | Size | Meaning | | Code | Size | Meaning |
|---|---|---|---|---|---|---|
| `b` / `B` | 1 | signed / unsigned char | | `i` / `I` | 4 | signed / unsigned int |
| `h` / `H` | 2 | signed / unsigned short | | `q` / `Q` | 8 | signed / unsigned long long |
| `f` | 4 | float | | `d` | 8 | double |
| `s` | n | `4s` = 4 raw bytes | | `x` | 1 | one pad byte, skipped |

### The second interesting question: a read is not a message

`ser.read(n)` returns **up to** n bytes — whatever has arrived. On a loaded bus you get half
a frame, or two and a bit:

```
   what the device sent:   [frame A][frame B][frame C]

   what read() gives you:  [frame A ][fr      ← chunk 1
                           ame B][frame ]     ← chunk 2
                           [C]                ← chunk 3
```

So `frames()` cannot assume a chunk is a frame. It accumulates into a buffer, pops every
*complete* frame it can find, and keeps the remainder for next time. Getting this right is
what separates code that works at your desk from code that works on a busy bus.

---

## Why firmware test needs this

Binary telemetry handling is the daily work of a test engineer at a space or aerospace firm,
and it is exactly where generic Python interview prep is useless — nobody's LeetCode practice
covers `struct`. Job postings name it constantly, and SpaceX's reported take-home includes
parsing a custom binary protocol.

`protocol_parser` is this same problem seen from the *firmware* side, in C. Doing the two
close together is deliberate: the wire format is the contract between them, and being able to
say "I wrote both ends" is a strong answer.

**Evidence bar for Y2** — three consecutive clean reps at 20 minutes, across three variants.

---

## What you need from Python

```python
import struct
```

**`bytes` vs `str` — they are not interchangeable and mixing them is the most common
beginner error in this domain.** `bytes` is raw binary (`b'\xAA\x03'`); `str` is text.
Indexing a `bytes` gives you an `int`, not a one-byte `bytes`, which surprises everyone once:

```python
   buf = b'\xAA\x03'
   buf[0]     # 170   ← an int
   buf[0:1]   # b'\xaa'  ← a bytes of length 1
```

**`struct.unpack` returns a tuple, always** — even for one value. `struct.unpack('<H', b)[0]`
is the idiom, and forgetting the `[0]` is a five-second bug you should stop making.
`struct.unpack_from(fmt, buf, offset)` reads at an offset without slicing, which is what you
want inside a loop.

**`memoryview`** lets you slice a buffer without copying it. Not needed for correctness; it
is the answer to "how would you make this faster for a million packets."

---

## The API you are writing

```python
def decode(buf: bytes) -> dict:
    """One frame -> its fields. Raise FrameError on anything malformed."""

def frames(chunks: Iterable[bytes]) -> Iterator[dict]:
    """A stream of arbitrary read() chunks -> complete frames only."""

class FrameError(Exception):
    ...
```

- **`decode` takes exactly one frame** and either returns its fields or raises. It never
  returns a partial result and never returns `None` for "bad" — a caller who forgets to check
  a return value gets an exception; a caller who forgets to check `None` gets a crash three
  functions later.
- **`frames` is a generator.** It takes an iterable of chunks — which in a test is a list of
  `bytes`, and in production is `iter(lambda: ser.read(64), b'')` — and yields complete
  frames as they become available. Incomplete tail data stays in the buffer.
- **`FrameError` is your own exception type**, so a caller can distinguish "the wire is
  corrupt" from "your code has a bug."

**Validate the declared length before you slice.** A length field is attacker-controlled in
the general case and garbage-controlled in the real one. `buf[3:3+length]` on a short buffer
does not raise in Python — slicing silently returns whatever is there — so a truncated frame
becomes a short payload and a wrong answer rather than an error. Check first.

---

## How to think about it

Don't write code yet. Answer these on paper:

1. Write out the byte layout of your frame, with an offset for each field, like the diagram
   above. Write the `struct` format string for the header. Say the prefix out loud.
2. What is the *minimum* number of bytes before `decode` can even know the frame's total
   length? (Header only. That is the first check.)
3. In `frames`, you have 5 bytes buffered and the header says the frame is 12 long. What do
   you do? What if the first byte isn't the sync byte at all?
4. A sync byte appears *inside* a payload — which it will, sooner or later. Why does that not
   break you, and what would it break if you were splitting on the sync byte instead of using
   the length? (This is the test that proves you are length-driven.)
5. What is the invariant for `frames`? Something like: *every complete frame in the
   concatenated input is yielded exactly once, in order, regardless of where the chunk
   boundaries fall.*

Then write it. It is about 50 lines.

---

## Tests it must pass

| Test | What it's protecting against |
|---|---|
| Round-trip: `decode(encode(x)) == x` for every field at its limits | The baseline. Build a tiny encoder in the test to generate frames |
| A frame one byte short, and one byte long | Both sides of the length check |
| A declared length that overruns the buffer | The silent slice. Must raise, not truncate |
| A negative value in a signed field, and the same bits read unsigned | The `h`/`H` trap, asserted rather than assumed |
| A sync byte appearing inside a payload | Proves you are length-driven, not delimiter-driven |
| Chunk boundaries falling in **every** position within a frame | The reassembly. Loop the split point across the whole frame — this is one `for` loop and it is the best test in the suite |
| Bad CRC, if your variant has one | That you check it at all |
| A chunk of `b''`, and a chunk containing two complete frames | The degenerate and the greedy case |

---

## Once it's boring

*Boring* means: blank file to working, tests green first run, in under twenty minutes, never
unsure what to type next. Then add a constraint.

**Second pass — resynchronisation.** Corrupt a byte mid-stream so the sync byte is lost.
Your parser should discard bytes until it finds a plausible frame start rather than giving
up or looping forever. Real links do this, and "what happens after a corrupt byte" is a good
interview question.

**Third pass — make it fast.** Unpack a million frames and time it. Then replace repeated
`struct.unpack` calls with a precompiled `struct.Struct` object, and slicing with
`memoryview`. Measure both. Being able to say "compiling the format string once cut it by
about a third" is worth more than knowing the trick.

---

> **Variants:** seven, `v1` through `v7`, written up in [VARIANTS.md](VARIANTS.md).
> `make drill` picks one and `make done` logs the rep to
> [logs/log.tsv](../../../logs/log.tsv). Time is only comparable within a variant.

## Interview questions this lets you answer from experience

Why did `struct.unpack` give different numbers on two machines · what do you check before
unpacking a frame off a port · how do you reassemble frames across read boundaries · how
would you fault-inject this · what happens when the length field lies.
