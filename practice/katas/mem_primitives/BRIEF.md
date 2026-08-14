# Kata 8 — mem_primitives

**In one sentence.** The standard library's memory and string functions, written from
scratch, correct at every boundary.

---

> **Before your first rep you owe this module two files:** `include/mem_primitives.h` — the API
> contract — and the suite in `tests/`. Write the header first, then list the cases under
> **Tests it must pass** below in your own words, then write every one of them yourself. AI writes
> neither. `make drill` refuses a module whose header and tests do not exist, because a rep
> against an empty suite is not a rep. Both are frozen once written: you do not edit them
> during a rep, only your `src/`, which is deleted each time. See
> [DAILY.md](../../../DAILY.md#build-sessions).

## The problem, in plain language

C has no string type. It has no array bounds. What it has is a block of bytes and an
address pointing into it, and every one of these functions is a loop over raw memory
where the only thing stopping you running off the end is you.

A C "string" is a convention, not a type: a run of characters ending in a zero byte.

```
   char greeting[8] = "hello";

   index:   0    1    2    3    4    5    6    7
          [ h    e    l    l    o   \0    ?    ? ]
                                     ^
                            the terminator. THIS is
                            what makes it a string.
                            Bytes 6 and 7 are whatever
                            was in RAM. Not your business.
```

`strlen` walks forward counting until it hits that `\0` — so it returns **5**, not 8. The
terminator is not counted, but it does occupy a byte, which is why "a 5-character string
needs 6 bytes of storage" is a sentence you should be able to say without thinking.

Every bug in this module is one of three things:

1. You forgot the terminator existed.
2. You wrote one byte past the end of the destination.
3. You assumed the source and destination don't overlap, and they did.

### The one genuinely interesting question

**Why does `memmove` exist when `memcpy` already copies bytes?**

Because `memcpy` is allowed to copy in *any* order — front-to-back, back-to-front, or
eight bytes at a time — and the standard explicitly says the two regions must not overlap.
`memmove` makes no such demand: it works even when they do.

Here is why the direction matters. Shift four bytes one position to the right, copying
front-to-back:

```
   start:        [ A  B  C  D  .  ]        dst = src + 1
                   ^  ^
                  src dst

   copy A to slot 1:  [ A  A  C  D  . ]    ← we just destroyed B
   copy B to slot 2:  [ A  A  A  D  . ]    ← but B is gone, so we copy the A we wrote
   copy C to slot 3:  [ A  A  A  A  . ]    ← smeared
   result:            [ A  A  A  A  . ]    WRONG
```

Now the same copy, back-to-front:

```
   copy D to slot 4:  [ A  B  C  D  D ]
   copy C to slot 3:  [ A  B  C  C  D ]
   copy B to slot 2:  [ A  B  B  C  D ]
   copy A to slot 1:  [ A  A  B  C  D ]    CORRECT
```

Reverse the overlap — `dst < src` — and it flips: front-to-back is safe, back-to-front
smears. So `memmove` has to look at the two addresses and pick a direction.

**Work out on paper which direction is safe for each case before you write a line.** That
reasoning, said out loud, is the whole answer to a very common interview question. "memmove
is the safe one" is the wrong answer, because it doesn't explain why anyone would ever use
`memcpy` — and the reason is speed: no overlap check, and freedom to copy a word at a time.

---

## Why firmware needs this

Half of embedded C is moving bytes around with no safety net. You will write these by hand
more often than you expect, because a lot of firmware either has no libc or has one you do
not trust — a `memcpy` that assumes 4-byte alignment will fault on a Cortex-M0 handed an
odd address.

They are asked constantly in interviews for a specific reason: they are small enough to
write on a whiteboard and unforgiving enough to show whether you actually think about
bounds, overlap and alignment, or just remember that the functions exist.

They don't fit anywhere else in this set — `bitops` has no bit manipulation in it and
`protocol_parser` has no framing.

---

## What you need from C

```c
#include <stddef.h>   /* size_t, NULL */
#include <stdint.h>   /* uint8_t */
```

**`void *` is "a pointer to something, and I'm not saying what."** It is how `memcpy`
accepts a pointer to *any* type. You cannot dereference it directly — the compiler doesn't
know how many bytes to read — so the first thing every `mem*` function does is cast it to
`unsigned char *`, which is the one type guaranteed to mean "raw bytes":

```c
unsigned char *d = dst;   /* legal without a cast, from void * */
```

**Pointer arithmetic is in units of the pointed-to type.** If `p` is an `unsigned char *`,
`p + 1` is one byte along. If it's a `uint32_t *`, `p + 1` is *four* bytes along. This is
the single most common source of confusion coming from a language with real arrays.

**`const` on a parameter is a promise you only read it.** `const char *src` means the
function will not write through `src`. The compiler enforces it, and every one of these
functions marks its source `const` for that reason.

**`restrict`** (on `my_memcpy`) is you telling the compiler "these two pointers do not
overlap, optimise accordingly." It is a promise the compiler cannot verify. Breaking it is
undefined behaviour — which is exactly the `memcpy`-with-overlap bug, spelled out in the
type system.

---

## The API you are writing

```c
size_t my_strlen(const char *s);
char  *my_strcpy(char *dst, const char *src);
char  *my_strncpy(char *dst, const char *src, size_t n);
int    my_strcmp(const char *a, const char *b);
void  *my_memset(void *dst, int c, size_t n);
void  *my_memcpy(void *restrict dst, const void *restrict src, size_t n);
void  *my_memmove(void *dst, const void *src, size_t n);
int    my_atoi(const char *s);
```

**The return values are part of the contract, and they are not obvious.**

| Function | Returns | Why |
|---|---|---|
| `my_strlen` | length, terminator not counted | |
| `my_strcpy`, `my_strncpy` | `dst` — the original pointer | Lets you chain calls. You must save it before your loop advances it |
| `my_strcmp` | negative / 0 / positive | **Not** −1/0/1. Compare as `unsigned char`, or high-bit bytes sort wrongly |
| `my_memset`, `my_memcpy`, `my_memmove` | `dst` | Same reason as `strcpy` |
| `my_atoi` | the parsed `int` | No way to report an error. That is a real flaw in the real `atoi` |

Getting a return value wrong fails the tests and, in an interview, signals you have never
read the man page.

**Three traps worth naming before you start:**

- **`my_strncpy` does not guarantee a terminator.** If `src` is `n` characters or longer,
  you copy `n` characters and stop — no `\0`. That surprise *is* the interview question.
  And when `src` is *shorter* than `n`, it pads the rest of the destination with zeros, all
  the way to `n`. Both halves are counter-intuitive and both are correct.
- **`my_memset` takes an `int` but writes bytes.** `memset(p, 0x1FF, n)` writes `0xFF`.
  Mask the value to a byte before you use it.
- **`my_atoi` skips leading whitespace, accepts one optional sign, then stops at the first
  non-digit.** `atoi("  -42abc")` is `-42`. It does not report the stop.

---

## How to think about it

Don't write code yet. Answer these on paper:

1. Draw an 8-byte array holding `"hi"`. Mark every byte. What does `my_strlen` return, and
   how many bytes did it read?
2. For `my_memmove`, write the condition — in terms of `dst`, `src` and `n` — that decides
   which direction to copy. Which comparison is it? (Careful: comparing unrelated pointers
   is technically undefined; in practice you compare the two you were given, which do
   relate.)
3. `my_strcpy(dst, src)` has to return `dst`, but your loop is going to move a pointer
   along. Where does the original get saved?
4. `my_strcmp("apple", "apples")` — which is "less", and what is the last comparison the
   loop makes before it can tell?
5. What does every one of these functions do when `n` is 0? (Answer: nothing at all, and it
   must not touch the destination. That is a real test.)

Then write them. Each is between three and fifteen lines. Do `strlen`, `memset` and
`memcpy` first — they are the easy three and they warm up the pointer idiom.

---

## Tests it must pass

| Test | What it's protecting against |
|---|---|
| `n = 0` for every function taking a length — destination untouched | The loop that runs once when it should run zero times |
| Overlapping regions in **both** directions for `my_memmove` | The smear above. One direction will pass by accident; test both |
| `my_memcpy` tested only on non-overlapping regions | Testing it on overlap is testing undefined behaviour, which proves nothing |
| Empty strings, single characters, a string exactly filling its buffer | Off-by-one at both ends |
| `my_strncpy` with src **shorter** than `n` (zero-padded) and **longer** (no terminator) | The two surprises. Both are the specified behaviour |
| `my_strcmp` with bytes above 0x7F | The signed-`char` bug. `"\xFF"` must compare *greater* than `"a"` |
| `my_atoi` with leading whitespace, a sign, digits then letters, and a value that overflows | The parser's stopping conditions |
| A guard byte written just past every destination buffer, checked afterwards | The one-past-the-end write. ASan catches this too — belt and braces |

Use small buffers, 8 or 16 bytes. With a 1KB buffer the interesting cases never happen.

---

## Once it's boring

*Boring* means: blank file to working, sanitizer-clean, in under ten minutes, never unsure
what to type next. Then add a constraint.

**Second pass — word-at-a-time `my_memcpy`.** Real implementations copy `size_t` at a time
rather than byte at a time, which is roughly four to eight times faster. But you can only do
that when both pointers are suitably aligned, so you copy leading bytes until aligned, then
words, then trailing bytes. Now you have three loops and a lot more edge cases — do it only
once the byte version is provably clean, and keep the byte version around to test against.

**Third pass — write `my_strlen` without a loop counter**, using pointer subtraction:
advance a pointer to the terminator, return `p - s`. Then paste both versions into
[godbolt.org](https://godbolt.org) with an ARM target and compare the instruction counts.

---

> **Variants:** seven, `v1` through `v7`, written up in [VARIANTS.md](VARIANTS.md).
> `make drill` picks one and `make done` logs the rep to
> [logs/log.tsv](../../../logs/log.tsv). Time is only comparable within a variant.

## Interview questions this lets you answer from experience

Implement `strlen`/`strcpy`/`memcpy`/`memmove` · why `memmove` exists · what `strncpy` does
that surprises people · reverse a string in place · `atoi` with overflow · pointer arithmetic
and array decay.
