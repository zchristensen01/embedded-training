# Kata 7 — register_map

**In one sentence.** A block of memory you treat as memory-mapped hardware registers,
plus the accessor layer over it — the bottom inch of every driver ever written.

---

> **Before your first rep you owe this module two files:** `include/register_map.h` — the API
> contract — and the suite in `tests/`. Write the header first, then list the cases under
> **Tests it must pass** below in your own words, then write every one of them yourself. AI writes
> neither. `make drill` refuses a module whose header and tests do not exist, because a rep
> against an empty suite is not a rep. Both are frozen once written: you do not edit them
> during a rep, only your `src/`, which is deleted each time. See
> [DAILY.md](../../../DAILY.md#build-sessions).

## The problem, in plain language

On a microcontroller, hardware is not something you call. It is something you *write to an
address*.

There is no API to turn on a UART. What there is: a documented address — say `0x40004400` —
and a datasheet saying bit 3 of the 32-bit word at that address enables the transmitter. You
turn the transmitter on by storing a number into that address. The silicon is watching that
address and reacts.

```
   your program's view                  what's actually there
   ────────────────────                 ─────────────────────
   0x20000000  ┐
      ...      │  RAM — ordinary memory,       real storage cells
   0x2000FFFF  ┘  reads return what you wrote

   0x40004400  ┐                               ┌──────────────┐
   0x40004404  │  "memory" that is actually    │ UART         │
   0x40004408  │  a peripheral's registers     │ hardware     │
   0x4000440C  ┘                               └──────────────┘
                  writing here CHANGES THE WORLD
                  reading here may change it too
```

That second block looks like memory and is not. Three things are true of it that are not
true of RAM, and every one of them breaks an assumption the compiler is entitled to make:

1. **It can change on its own.** A status register's "byte received" bit gets set by
   hardware while your code is between two lines.
2. **Reading can have side effects.** On a great many peripherals, reading the data register
   is what *clears* the "data ready" flag. The read is not passive; it is an action.
3. **Every access is a real bus transaction with a real cost**, and the number and order of
   those transactions is part of the contract with the hardware.

### The one genuinely interesting question

**What does `volatile` actually do, and what does it not do?**

Without it, this is a legal optimisation:

```c
   uint32_t *status = (uint32_t *)0x40004400;
   while ((*status & READY) == 0) { }        /* wait for hardware */
```

The compiler reasons: nothing inside this loop writes to `*status`, so its value cannot
change, so I will read it once into a register and loop on that. If the bit was clear on
that first read, **you have compiled an infinite loop.** It is a genuine, common, and
maddening bug, and it disappears when you build with `-O0` — which is why "it works in debug
but hangs in release" is the classic symptom.

`volatile` tells the compiler: this location can change outside the program's control, so
perform *exactly* the reads and writes I wrote, in the order I wrote them, and do not cache
the value or elide anything.

**What it does not do is make anything atomic.** `*reg |= FLAG` is three separate bus
transactions:

```
     read  0x40004400  ->  0x0000_0102
     modify in the CPU ->  0x0000_0106
     write 0x40004400  <-  0x0000_0106
                 ▲
        an interrupt landing HERE, which also
        touches this register, has its write
        silently overwritten by yours
```

`volatile` guarantees all three transactions happen. It guarantees nothing about what
happens between them. That distinction — *volatile is about visibility, not atomicity* — is
one of the most reliable interview questions in embedded, and reaching for `volatile` as a
synchronisation primitive is the single most common C concurrency error.

### Saying the declaration out loud

Read C declarations right-to-left from the variable name. Practise until it's automatic,
because you will be asked to write this on a whiteboard:

```c
volatile uint32_t * const REG = (volatile uint32_t *)0x40004400;
         │           │
         │           └─ const POINTER: the address never changes
         └───────────── VOLATILE data: the thing at that address can
```

*"REG is a constant pointer to volatile 32-bit unsigned data."* The address is fixed
forever; the contents change under you. That is exactly right for a peripheral register, and
putting the `const` on the wrong side — giving you a mutable pointer to constant data — is
the trap the question is set to catch.

| Declaration | Means |
|---|---|
| `uint32_t *p` | ordinary pointer to ordinary data |
| `const uint32_t *p` | pointer to data **you** must not write. Read-only status register |
| `uint32_t * const p` | the pointer itself is fixed; the data is writable |
| `volatile uint32_t *p` | data can change behind your back |
| `const volatile uint32_t *p` | hardware changes it, you must not. **The read-only status register.** Not a contradiction — the two words are addressed at different parties |

---

## Why firmware needs this

Every driver you will ever write starts here. Before there is a UART driver there is a
`reg_write`, and the quality of that bottom inch decides whether the driver above it is
debuggable.

It is also the highest-yield interview cluster in embedded. `volatile`, `static`, `const`
and pointer semantics come up more than any other topic, and no other module in this set
touches access semantics at all: `bitops` operates on *values*, this operates on
*locations*.

---

## What you need from C

```c
#include <stdint.h>    /* uint32_t, uintptr_t */
#include <stdbool.h>   /* bool */
#include <stddef.h>    /* offsetof */
#include <assert.h>    /* static_assert */
```

**`uintptr_t`** is an unsigned integer guaranteed to be big enough to hold a pointer. The
API takes the peripheral's base as a `uintptr_t` rather than a pointer so you can do
arithmetic on it (`base + off`) without arguing with the compiler about types, then cast to
a pointer at the moment of access.

**`static` does two entirely different jobs** depending on where you put it, and being able
to name both is the question:

- on a **local variable**: changes its *lifetime* — it persists across calls and lives in
  `.data`/`.bss`, not on the stack
- on a **file-level variable or function**: changes its *linkage* — the symbol becomes
  private to that `.c` file, so two files can each have their own `count` without colliding

**`_Static_assert`** is checked at compile time and costs nothing at runtime. It is how you
prove a struct really does have the layout the hardware expects — if it doesn't, the build
fails rather than the device.

---

## The API you are writing

```c
/* frozen in include/register_map.h */
#define REG_CTRL   0x00u   /* rw */
#define REG_STATUS 0x04u   /* ro */
#define REG_DATA   0x08u   /* rw */

void     reg_write(uintptr_t base, uint32_t off, uint32_t val);
uint32_t reg_read (uintptr_t base, uint32_t off);
void     reg_set_bits  (uintptr_t base, uint32_t off, uint32_t mask);
void     reg_clear_bits(uintptr_t base, uint32_t off, uint32_t mask);
void     reg_modify(uintptr_t base, uint32_t off, uint32_t mask, uint32_t val);
bool     reg_wait_flag(uintptr_t base, uint32_t off, uint32_t mask, uint32_t timeout);
```

- **Offsets are 0x00, 0x04, 0x08** — four bytes apart, because each register is 32 bits.
  Registers are almost always spaced by their width.
- **`reg_modify(base, off, mask, val)`** is the general form: clear the bits in `mask`, then
  set the bits of `val` that fall inside `mask`. `reg_set_bits` and `reg_clear_bits` are the
  two common special cases. Write `reg_modify` first and see whether the other two fall out
  of it.
- **`reg_wait_flag`** spins until the masked bits are set or `timeout` iterations elapse,
  returning `false` on timeout. **It must have a bounded exit.** A driver that hangs forever
  because a device didn't answer is the bug that ships.
- **`reg_modify` must not evaluate its arguments twice.** This is why it is a function. As a
  macro, `reg_modify(base, off, mask, next_value())` would call `next_value()` twice, and
  you would spend an afternoon on it.

This kata's tests are unusual: because the "hardware" is a plain array you control, the
tests can check not just the resulting value but **the exact sequence of accesses** your
accessor performed. That is the point. A `reg_set_bits` that reads twice is wrong on
hardware where reading clears a flag, even though the final value looks right.

---

## How to think about it

Don't write code yet. Answer these on paper:

1. Write the declaration for a pointer to a read-only 32-bit status register at
   `0x40004400`. Now say it out loud in English. (Both `const` and `volatile`, and you
   should be able to justify each.)
2. `reg_set_bits(base, REG_CTRL, 0x8)` — write down the exact sequence of bus transactions
   it should produce. How many reads? How many writes?
3. Same question for `reg_write`. (One write, no read. If your implementation reads first,
   you have a bug on a write-only register.)
4. What is the invariant for `reg_modify`? Something like: *bits outside `mask` are
   bit-for-bit identical before and after.* That sentence is a test.
5. Why can `reg_wait_flag` not be written as `while (!(reg_read(...) & mask));`? What must
   the loop variable be, and what stops the compiler removing it?

Then write it. It is about 40 lines.

---

## Tests it must pass

| Test | What it's protecting against |
|---|---|
| Each accessor produces exactly the expected access sequence — no more, no fewer | The extra read that clears a flag on real hardware. This is the test that makes the kata worth doing |
| Set / clear / modify leave every bit outside the mask untouched | The read-modify-write done wrong, which is most of them |
| Writing a read-only register is rejected or asserts (per variant) | The contract in the header actually meaning something |
| Overlay struct has the exact expected `sizeof` and member offsets, via `_Static_assert` | Padding silently inserted between members, which puts every register at the wrong address |
| `reg_wait_flag` returns `false` on timeout and does not spin forever | The hang that ships |
| `reg_wait_flag` returns `true` as soon as the flag appears, without over-reading | Polling a side-effecting register more than necessary |
| Mask of `0` and mask of all-ones both behave | The degenerate cases, which is where the `~mask` typo shows up |

---

## Once it's boring

*Boring* means: blank file to working, sanitizer-clean, in under twelve minutes, never
unsure what to type next. Then add a constraint.

**Second pass — the overlay struct.** Instead of `base + offset`, declare a struct whose
members line up with the registers and cast the base address to a pointer to it:
`volatile regs_t *r = (volatile regs_t *)base; r->ctrl = x;`. It reads far better. It is also
how you discover padding the hard way, which is what the `_Static_assert` on `sizeof` and
`offsetof` is for. Both styles are used in the field and you should be able to argue for
each.

**Third pass — bitfields, and why not.** Re-express the control register as a struct of
bitfields. Then work out why most embedded style guides ban them: the standard does not fix
which end the first bitfield starts at, so the layout is compiler-dependent and can differ
between two compilers targeting the same chip. Being able to explain *that* is worth more
than the implementation.

**Fourth pass — a delay loop the compiler cannot remove.** Write a busy-wait of N
iterations that survives `-O2`. Then check the disassembly and confirm it is still there.

---

> **Variants:** seven, `v1` through `v7`, written up in [VARIANTS.md](VARIANTS.md).
> `make drill` picks one and `make done` logs the rep to
> [logs/log.tsv](../../../logs/log.tsv). Time is only comparable within a variant.

## Interview questions this lets you answer from experience

Declare a pointer to a memory-mapped register · all four `const`/`volatile` combinations ·
why `volatile` is not atomicity · where a `const` array lives on an MCU · struct padding and
`offsetof` · bitfields vs mask-and-shift and why bitfields are risky · a delay loop the
compiler cannot remove · the two jobs of `static`.
