# Kata 9 — pool_allocator

**In one sentence.** A fixed-block memory allocator over a static array, with the list of
free blocks stored *inside the free blocks themselves*.

---

> **Before your first rep you owe this module two files:** `include/pool_allocator.h` — the API
> contract — and the suite in `tests/`. Write the header first, then list the cases under
> **Tests it must pass** below in your own words, then write every one of them yourself. AI writes
> neither. `make drill` refuses a module whose header and tests do not exist, because a rep
> against an empty suite is not a rep. Both are frozen once written: you do not edit them
> during a rep, only your `src/`, which is deleted each time. See
> [DAILY.md](../../../DAILY.md#build-sessions).

## The problem, in plain language

You need to hand out and reclaim chunks of memory at runtime, and you are not allowed to
call `malloc`.

`malloc` is banned or heavily restricted in most firmware for three reasons, and you should
be able to give all three:

- **Fragmentation.** Repeated allocation and freeing of different sizes leaves the free
  space chopped into pieces. Eventually a 200-byte request fails even though 4KB is free,
  because no single *contiguous* 200 bytes exists. On a device that runs for a year, this is
  not hypothetical.
- **Non-deterministic timing.** `malloc` walks a data structure. How long it takes depends
  on the history of every previous call. In a control loop that must finish in 500
  microseconds, "usually fast" is not a specification.
- **No good failure story.** What does a heart monitor do at 3am when `malloc` returns
  `NULL`? There is rarely a real answer, which means the failure has to be designed out
  rather than handled.

A pool solves all three by giving up generality: **every block is the same size.** Because
they are interchangeable, there is no fragmentation — any free block satisfies any request.
Because you never search, allocation is a constant handful of instructions.

### The trick: the free list costs zero extra memory

The obvious design is an array of "is this block free?" flags. You don't need it.

A block that is *free* has, by definition, nothing useful in it. So you store the address of
the next free block **in the first few bytes of the free block itself**. The free list is
threaded through the free space.

```
   backing array, 4 blocks of 16 bytes:

   ┌────────────────┬────────────────┬────────────────┬────────────────┐
   │   block 0      │   block 1      │   block 2      │   block 3      │
   └────────────────┴────────────────┴────────────────┴────────────────┘

   after init, everything is free and chained together:

   head ──▶ blk0 ──▶ blk1 ──▶ blk2 ──▶ blk3 ──▶ NULL
            └─ the first 8 bytes of block 0 hold the address of block 1


   after two allocations (blocks 0 and 1 handed out):

   ┌────────────────┬────────────────┬────────────────┬────────────────┐
   │ IN USE         │ IN USE         │  ──▶ blk3      │  ──▶ NULL      │
   │ caller's data  │ caller's data  │                │                │
   └────────────────┴────────────────┴────────────────┴────────────────┘
   head ──▶ blk2 ──▶ blk3 ──▶ NULL

   The caller's data has overwritten the "next" pointers in blocks 0 and 1.
   That is fine — those blocks are not on the list any more.
```

`pool_alloc` is now: take the block at `head`, set `head` to whatever that block pointed at,
return the block. `pool_free` is: make the returned block point at the current `head`, then
set `head` to the returned block. Both are three or four lines and take the same time
whether one block is free or a thousand.

**Draw this on paper before you code it.** Drawing it *is* the exercise; the code is a
transcription of the picture.

### The one genuinely interesting question

**What is the minimum block size, and why?**

You are storing a pointer inside a free block, so a block must be at least
`sizeof(void *)` — 8 bytes on a 64-bit host, 4 on a typical MCU. A pool of 2-byte blocks
cannot exist, because there is nowhere to put the link.

And it must be **aligned**. If the caller is going to store a `uint32_t` in the block, the
block's address must be a multiple of 4, or on many architectures the access faults and on
the rest it is merely slow. Since every block is at `base + n * block_size`, alignment of
every block follows from the alignment of `base` *and* `block_size` being a multiple of the
alignment.

So: assert that `block_size >= sizeof(void *)`, assert it is a multiple of
`alignof(max_align_t)`, and decide — then write down in `NOTES.md` — whether aligning the
backing array is your problem or the caller's. Both are defensible. Having not thought about
it is not.

---

## Why firmware needs this

"Why don't you just use `malloc`?" is a standard interview question, and the convincing
answer is that you have written the thing that replaces it. Everyone can recite
"fragmentation"; far fewer can sketch a pool on a whiteboard in ten minutes.

It is also genuinely used: fixed-size pools back the packet buffers in almost every network
stack, the message blocks in most RTOS queues, and the event objects in most state machine
frameworks. Nothing else in this kata set allocates anything.

---

## What you need from C

```c
#include <stdint.h>    /* uintptr_t, uint8_t */
#include <stddef.h>    /* size_t, max_align_t, NULL */
#include <stdalign.h>  /* alignof */
#include <assert.h>
```

**Casting between a block and its "next" pointer.** A free block is raw bytes, and you want
to treat its first few bytes as a `void *`. That is:

```c
   void *next = *(void **)block;    /* read the link out of the block */
```

Read it inside-out: `(void **)block` is "pretend this address holds a pointer", and the
leading `*` dereferences it to get that pointer. Writing the link is the same expression on
the left of an `=`. This double-star line is the one piece of syntax in the kata that looks
harder than it is; write it out once by hand and it stops being mysterious.

**`uintptr_t` for address arithmetic.** To check "is this pointer inside my backing array
and on a block boundary", cast both to `uintptr_t` and do integer maths. Doing arithmetic on
`void *` is not portable.

**Alignment.** `alignof(max_align_t)` is the strictest alignment any basic type needs on
this platform — typically 8 or 16. Rounding a size *up* to a multiple of `A` is the idiom
`(n + A - 1) & ~(A - 1)`, which only works when `A` is a power of two. It always is.

---

## The API you are writing

```c
typedef struct pool pool_t;

void  pool_init(pool_t *p, void *backing, size_t backing_size, size_t block_size);
void *pool_alloc(pool_t *p);
void  pool_free(pool_t *p, void *block);
size_t pool_available(const pool_t *p);
```

- **`pool_init` takes the storage from the caller.** The pool does not own memory; it
  organises memory somebody else declared, exactly like `ring_buffer`. The caller writes
  `static uint8_t arena[1024]; pool_t p; pool_init(&p, arena, sizeof arena, 64);`. The
  number of blocks is `backing_size / block_size`, and any remainder at the end is simply
  unused.
- **`pool_alloc` returns `NULL` when exhausted.** It must not fault, must not return a block
  it already handed out, and must leave the pool usable.
- **`pool_free` takes a pointer you previously handed out.** From `v3` onward it must
  *detect* a double free rather than corrupting the list — see below.
- **`pool_available` is a query**, hence `const`. Deciding whether to walk the free list
  each time or keep a counter is a real trade-off: the counter is O(1) and is one more
  thing that can disagree with reality.

**Why double-free is the interesting failure.** Free the same block twice and the naive
implementation links it to itself:

```
   head ──▶ blkA ──▶ blkA ──▶ blkA ──▶ ...   (a loop)
```

Two later allocations both return `blkA`, two parts of the program now believe they own the
same memory, and the resulting bug appears somewhere else entirely, hours later. Detecting
it — by walking the free list and refusing a block already on it, or by keeping a bitmap —
turns a silent corruption into a loud failure. The cheap version is O(n) on free, and being
able to say out loud what that costs you is the point.

---

## The contract I decided

> **Fill this in before you write a single test case, and read only this section at the
> start of a rep.** Everything above is the brief teaching you the problem. This is what
> *you* committed to — the suite in `tests/` enforces it, and it is frozen for fourteen
> weeks. If it is blank, you have not finished the build session.

### Types

```
(structs, enums, typedefs · dataclasses, NamedTuples, exceptions — names and fields)
```

### Functions

```
(exact signatures, spelled as you will write them)
```

### What no signature can say

| Question | My answer |
|---|---|
| What does failure look like — return value, exception, exit code? | |
| What is left untouched when it fails? | |
| Preconditions the caller must honour, and what happens if they don't | |
| Ownership and lifetime — who owns the memory, what gets consumed | |
| Safe to call concurrently, from an ISR or a thread? Or single-threaded only? | |
| The invariant that holds after every call | |

## How to think about it

Don't write code yet. Answer these on paper:

1. Draw a 64-byte backing array with 16-byte blocks. Draw the free list after `pool_init`.
   Now draw it after `alloc, alloc, free(first)`. What is the order of the list now? (It is
   not the original order, and that is fine.)
2. `pool_alloc` on an empty pool: what exactly does it check, and what does it return?
3. `pool_free(p, ptr)` where `ptr` did not come from this pool — how would you detect it?
   (Two conditions: inside the backing array, *and* on an exact block boundary.)
4. What is the invariant? Something like: *`pool_available()` plus the number of
   outstanding allocations always equals the total block count.* Assert that in your tests.
5. What is the minimum legal `block_size`, and what should `pool_init` do if given less?

Then write it. It is about 60 lines, and `pool_alloc` and `pool_free` are four lines each —
almost all the work is in `pool_init` and the validation.

---

## Tests it must pass

| Test | What it's protecting against |
|---|---|
| Exhaust the pool, then the next `pool_alloc` returns `NULL` rather than misbehaving | Running off the end of the free list |
| Free everything; `pool_available` returns to the initial count | The counter drifting from reality |
| Alloc, free, alloc — the reused block is usable and the list is not corrupt | The link write clobbering something it shouldn't |
| Every returned pointer is correctly aligned and inside the backing array | The alignment maths, and the off-by-one on the last block |
| No two outstanding allocations return the same address | The aliasing bug, which is the one that matters |
| Double free is detected (`v3` onward) | The self-referential loop above |
| Freeing a pointer that never came from this pool is detected | The bounds-and-boundary check |
| Write to the **full extent** of every block returned, under ASan | Blocks overlapping by a byte because `block_size` was rounded wrongly |

That last one is worth spelling out: allocate every block, fill each completely with a
distinct byte pattern, then check every one still reads back correctly. If your blocks
overlap, this is the test that says so.

---

## Once it's boring

*Boring* means: blank file to working, sanitizer-clean, in under twenty minutes, never
unsure what to type next. Then add a constraint.

**Second pass — O(1) double-free detection.** Walking the list on every free is O(n). Add a
bitmap, one bit per block, set on alloc and cleared on free; a double free is then a single
bit test. Now you have two structures that must agree, which is a different kind of bug —
and the trade-off between the two designs is a genuinely good interview answer.

**Third pass — make it ISR-safe.** `pool_alloc` from an interrupt while the main loop is
inside `pool_free` corrupts the list, for exactly the reason `count++` is not atomic. The
cheap fix is a critical section around both. Write down what that costs in interrupt
latency. The expensive fix is a lock-free stack with a compare-and-swap, and knowing why
that needs a version tag to avoid the ABA problem is well above the bar — but knowing the
name is not.

---

> **Variants:** eight, `v1` through `v8`, written up in [VARIANTS.md](VARIANTS.md).
> `make drill` picks one and `make done` logs the rep to
> [logs/log.tsv](../../../logs/log.tsv). Time is only comparable within a variant.

## Interview questions this lets you answer from experience

Stack vs heap in constrained memory · why `malloc` is avoided in firmware · fragmentation ·
alignment requirements · write your own `malloc`/`free` over a fixed pool · what happens when
allocation fails and why returning `NULL` is not a plan by itself · how you would detect a
double free.
