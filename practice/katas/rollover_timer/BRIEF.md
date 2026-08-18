# Kata 12 — rollover_timer

**In one sentence.** A millisecond counter that increments forever, plus software timers
that fire when their deadline arrives — and the one comparison that survives the counter
wrapping back to zero.

---

> **Before your first rep you owe this module two files:** `include/rollover_timer.h` — the API
> contract — and the suite in `tests/`. Write the header first, then list the cases under
> **Tests it must pass** below in your own words, then write every one of them yourself. AI writes
> neither. `make drill` refuses a module whose header and tests do not exist, because a rep
> against an empty suite is not a rep. Both are frozen once written: you do not edit them
> during a rep, only your `src/`, which is deleted each time. See
> [DAILY.md](../../../DAILY.md#build-sessions).

## The problem, in plain language

Bare-metal firmware with no operating system is one big loop. Something has to make "blink
the LED every 500 ms, read the sensor every 10 ms, kick the watchdog every second" happen
without any of them blocking the others.

The standard structure: a hardware timer interrupts once a millisecond and increments a
counter. Everything else compares against that counter and does its work when its deadline
has passed.

```
   hardware timer ISR, every 1 ms:        main loop, as fast as it can:
   ───────────────────────────────        ────────────────────────────────
        ticks++                                for each timer:
                                                   is it due yet?
                                                   if so, call its function
```

Nothing sleeps. Nothing blocks. Each job says "wake me at tick 41,200" and the loop checks.

### The bug this kata exists for

The counter is a `uint32_t`. It counts milliseconds. It therefore reaches its maximum —
4,294,967,295 — and wraps back to 0 after **49.7 days**.

Write the obvious comparison and you get the most famous bug in embedded software:

```c
   if (now >= deadline) { fire(); }      /* WRONG */
```

Watch what happens across the wrap. Suppose it is tick `0xFFFFFF00` and you want to fire in
`0x200` ms:

```
   now      = 0xFFFFFF00                     (4,294,967,040)
   deadline = 0xFFFFFF00 + 0x200 = 0x00000100    ← it wrapped!  (256)

   is now >= deadline?
      0xFFFFFF00 >= 0x00000100   →  TRUE, immediately

   The timer fires INSTANTLY instead of 512 ms later.
```

And the mirror case is worse: a deadline set just *before* the wrap is never reached,
because `now` has become a small number and stays below it for another 49.7 days. The device
works perfectly for seven weeks and then quietly wedges. **Nobody's test run lasted seven
weeks.**

### The one genuinely interesting question

**What comparison is correct, and why?**

```c
   if ((int32_t)(now - deadline) >= 0) { fire(); }      /* RIGHT */
```

The insight: **subtract first, then look at the sign.** Unsigned subtraction wraps cleanly —
`0x100 - 0xFFFFFF00` is `0x200` in `uint32_t` arithmetic, which is exactly the true distance
— so the difference is correct even when the absolute values are nonsense. Casting to signed
turns that difference into a *relative* answer: negative means "deadline is still ahead of
now", zero or positive means "it has arrived or passed".

```
   think of it as a circle, not a number line:

                    0
              ┌─────┴─────┐
        0xC000000        0x4000000
              │           │
              └─────┬─────┘
                0x8000000

   "now >= deadline"  asks where each point sits on a line — meaningless on a circle
   "now - deadline"   asks how far apart they are going clockwise — always meaningful
```

Being able to say *"unsigned subtraction wraps cleanly, so I compare the difference rather
than the values"* out loud is a genuinely good interview answer, and it is short.

**The limit that comes next.** This works only while the real interval is under half the
counter range — 2^31 ms, about **24.9 days** for a 32-bit millisecond tick. Past halfway,
"ahead" and "behind" are indistinguishable on the circle. Write that limit in the header; it
is the follow-up question.

**One pedantic footnote worth knowing.** Converting an out-of-range `uint32_t` to `int32_t`
is *implementation-defined* in C11 rather than guaranteed two's-complement wraparound. C23
finally guarantees it, and every compiler you will meet already did. The fully portable
spelling is `(now - deadline) < 0x80000000u` — the same test in unsigned arithmetic. Know
both, and know why they are the same test.

---

## Why firmware needs this

Every bare-metal project grows one of these in the first week. Arduino's `millis()`, ST's
`HAL_GetTick()`, and the tick counter in every RTOS all have exactly this property and
exactly this trap.

It is also the kata that closes C11 in [`plan/COVERAGE.md`](../../../plan/COVERAGE.md), and
it pairs with `fsm` (state timeouts) and `protocol_parser` (frame timeouts) — so it makes
two katas you already have better rather than sitting on its own.

---

## What you need from C

```c
#include <stdint.h>    /* uint32_t, int32_t */
#include <stdbool.h>   /* bool */
```

**A function pointer.** `typedef void (*timer_fn)(void *ctx);` declares a type meaning
"address of a function that takes a `void *` and returns nothing". You store one in a struct
and call it later with `t->fn(t->ctx)`. This is how C does callbacks, and it is the same
mechanism a table-driven state machine uses in `fsm`.

**The `void *ctx` beside it** is the standard C idiom for closing over data. The timer
doesn't know what your callback needs, so it hands back whatever pointer you gave it at
registration. Without it, every callback would have to reach for a global.

**`volatile` on the tick counter.** It is written by an ISR and read by the main loop, so
the compiler must not cache it — see `register_map` for the full argument. And note that on
an 8- or 16-bit machine, reading a 32-bit counter is *several* instructions, so the ISR can
land mid-read and hand you half of the old value and half of the new. Say what you would do
about that (read it twice and compare, or disable interrupts briefly) even though the host
build hides the problem entirely.

---

## The API you are writing

```c
/* frozen in include/rollover_timer.h */
typedef void (*timer_fn)(void *ctx);

typedef struct {
    uint32_t deadline;   /* absolute tick at which this fires */
    uint32_t period;     /* 0 = one-shot */
    timer_fn fn;
    void    *ctx;
    bool     active;
} timer_t;

void     tick(void);                                    /* called from a 1 ms ISR */
uint32_t now_ms(void);
bool     timer_expired(uint32_t deadline);              /* the interesting one */
bool     timer_start(timer_t *t, uint32_t delay_ms, uint32_t period_ms,
                     timer_fn fn, void *ctx);
void     timer_cancel(timer_t *t);
void     scheduler_run(void);                           /* superloop: run whatever is due */
```

**`timer_expired` is the whole kata.** It is one line. Everything else is bookkeeping around
it, and in the tests it is the function you can hammer at any counter value you like —
including `0xFFFFFFFE` — without waiting 49.7 days.

**Two design rules that are not obvious, and both are interview answers:**

- **Deadlines are absolute, not remaining time.** Storing "milliseconds left" and
  decrementing it makes every timer depend on being polled at a fixed rate, which a superloop
  cannot promise. An absolute deadline is correct no matter how irregularly you poll.
- **Periodic timers advance `deadline += period`, never `deadline = now + period`.** The
  second form adds however late you were polled to every single interval, so a 10 ms timer
  polled 2 ms late drifts by 2 ms *every time* and is minutes out by the end of the day:

```
   deadline += period          deadline = now + period
   ──────────────────          ───────────────────────
   fire at 100 (polled 102)    fire at 100 (polled 102)
   next deadline 110           next deadline 112
   fire at 110 (polled 113)    fire at 112 (polled 115)
   next deadline 120           next deadline 125
   ^ phase held                ^ drifting, permanently
```

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

1. Set `now = 0xFFFFFFF0` and a delay of 32. What is the deadline? Evaluate both the wrong
   comparison and the right one at `now = 0xFFFFFFF8` and at `now = 0x00000010`.
2. What is the largest delay `timer_start` can accept and still be correct? What should it do
   if handed more?
3. A periodic timer whose callback takes longer than its own period — what happens on the
   next `scheduler_run`, and what *should* happen? (There is more than one defensible
   answer. Pick one and write it in `NOTES.md`.)
4. `timer_cancel` called from inside that timer's own callback. What is the scheduler in the
   middle of doing, and what must not break?
5. State the invariant for a one-shot: *fires exactly once, then `active` is false, forever.*

Then write it. It is about 60 lines and `timer_expired` is one of them.

---

## Tests it must pass

| Test | What it's protecting against |
|---|---|
| Counter near `0xFFFFFFFF`: a deadline set just before the wrap fires correctly just after | **The reason this kata exists.** About six lines, and the only test that matters |
| A deadline exactly equal to `now` fires — not one tick late | The `>` vs `>=` off-by-one |
| A one-shot fires exactly once, then goes inactive | Re-arming something that shouldn't |
| A periodic timer polled late fires once and keeps its original phase | The drift above |
| Cancel before expiry: never fires. Cancel from inside its own callback: no corruption | Mutating the timer list while walking it |
| Zero delay, and a delay of exactly half the counter range | Both ends of the legal range |
| No timers active: `scheduler_run` is a cheap no-op | The empty case, which superloops hit constantly |

Because `tick()` is just a function, your tests can drive the counter anywhere instantly.
Set it to `0xFFFFFF00` and step it. **Never write a test that actually sleeps.**

---

## Once it's boring

*Boring* means: blank file to working, sanitizer-clean, in under twelve minutes, never
unsure what to type next. Then add a constraint.

**Second pass — a sorted timer list.** `scheduler_run` currently checks every timer on
every pass, which is O(n). Keep them sorted by deadline and only check the head. Now
insertion is the hard part, and *inserting across the wrap* is the hard part of that —
"earlier" is not a total order on a circle, which is a genuinely interesting thing to have
noticed.

**Third pass — a 16-bit tick counter.** Change the counter to `uint16_t` and watch it wrap
every 65.5 seconds instead of every 49.7 days. Every rollover bug you have becomes
reproducible in under a minute. This is the best debugging trick in the kata and worth
knowing as a technique in its own right: *shrink the counter to make the rare case common.*

---

> **Variants:** seven, `v1` through `v7`, written up in [VARIANTS.md](VARIANTS.md).
> `make drill` picks one and `make done` logs the rep to
> [logs/log.tsv](../../../logs/log.tsv). Time is only comparable within a variant.

## Interview questions this lets you answer from experience

Why `millis()` rollover breaks a naive comparison and what the correct one is · why the
deadline must be absolute · sharing a 32-bit counter between an ISR and main · why `volatile`
is not atomicity · how a superloop schedules work without an RTOS · drift in a periodic task ·
what limits the maximum representable interval.
