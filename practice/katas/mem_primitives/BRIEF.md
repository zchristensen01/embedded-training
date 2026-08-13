# Kata 8 — mem_primitives

> **Before your first rep you owe this module two files:** `include/mem_primitives.h` — the API
> contract — and the suite in `tests/`. Write the header first, then list the cases under
> **What to test** below in your own words, then write every one of them yourself. AI writes
> neither. `make drill` refuses a module whose header and tests do not exist, because a rep
> against an empty suite is not a rep. Both are frozen once written: you do not edit them
> during a rep, only your `src/`, which is deleted each time. See
> [DAILY.md](../../../DAILY.md#build-sessions).

## What it is
The standard library's memory and string functions, written from scratch, correct at every
boundary.

## Why firmware needs it
Half of embedded C is moving bytes around with no safety net. These are asked constantly in
interviews because they are small enough to write on a whiteboard and unforgiving enough to
expose whether you actually think about bounds, overlap, and alignment. They don't fit `bitops`
(no bit manipulation) or `protocol_parser` (no framing).

## The API you implement
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

## How to think about it
- Return values matter and are part of the contract. `memcpy` returns `dst`. `strcpy` returns
  `dst`. Getting this wrong fails the tests and, in an interview, signals you've never read the
  man page.
- `memmove` copies backward when the regions overlap and `dst > src`. Work out on paper which
  direction is safe before you code it.
- `strncpy` does not guarantee a null terminator when the source is longer than `n`. That
  surprise is the interview question.
- `memset` takes an `int` but writes `unsigned char`. Mask it.
- The word-at-a-time optimisation is a good v-variant, but only after the byte version is clean.

## What to test
- n = 0 for every function that takes a length. Must not touch the destination.
- Overlapping regions in both directions for `memmove`, and confirm `memcpy` is only tested on
  non-overlapping.
- Empty strings, single characters, strings exactly at the buffer boundary.
- `strncpy` with src shorter than n (pads with zeros) and longer than n (no terminator).
- `atoi` with leading whitespace, a sign, non-digits mid-string, and overflow.
- Every test runs under ASan with a guard byte after the buffer.

## Interview questions this lets you answer from experience
Implement strlen/strcpy/memcpy/memmove · why memmove exists · what strncpy does that surprises
people · reverse a string in place · atoi with overflow · pointer arithmetic and array decay.
