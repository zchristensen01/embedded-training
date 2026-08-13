# Kata 12 — rollover_timer

> **Before your first rep you owe this module two files:** `include/rollover_timer.h` — the API
> contract — and the suite in `tests/`. Write the header first, then list the cases under
> **What to test** below in your own words, then write every one of them yourself. AI writes
> neither. `make drill` refuses a module whose header and tests do not exist, because a rep
> against an empty suite is not a rep. Both are frozen once written: you do not edit them
> during a rep, only your `src/`, which is deleted each time. See
> [DAILY.md](../../../DAILY.md#build-sessions).

## What it is
A millisecond counter that increments forever in a timer interrupt, plus a small set of
software timers that fire when their deadline arrives. It is how a superloop firmware project
without an RTOS is structured: blink the LED every 500 ms, read the sensor every 10 ms, kick
the watchdog every second.

## Why firmware needs it
Every bare-metal project grows one of these in the first week, and it contains one of the most
famous bugs in embedded software. A `uint32_t` millisecond counter wraps back to zero after
49.7 days. Write `if (now > deadline)` and the device works perfectly for seven weeks and then
wedges — and nobody's test run lasted seven weeks.

This is also the kata that closes C11 in `plan/COVERAGE.md`. It pairs with `fsm` (state
timeouts) and `protocol_parser` (frame timeouts), so it makes two katas you already have
better rather than sitting on its own.

## The API you implement
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

## How to think about it
- **The comparison is the whole kata.** `(int32_t)(now - deadline) >= 0` is correct across the
  wrap; `now >= deadline` is not. Unsigned subtraction wraps cleanly, and the signed cast turns
  the result into a *relative distance* rather than an absolute position. Be able to say that
  sentence out loud — it is a genuinely good interview answer.
- That comparison only works while the real interval is under half the counter range —
  2^31 ms, about 24.9 days, for a 32-bit millisecond tick. Write that limit down in the
  header; it is the constraint an interviewer will ask about next.
- Pedantically, converting an out-of-range `uint32_t` to `int32_t` is *implementation-defined*
  in C11 rather than guaranteed two's-complement wraparound; C23 finally guarantees it, and
  every compiler you will meet already did. The fully portable spelling is
  `(now - deadline) < 0x80000000u`, which is the same test written in unsigned arithmetic.
  Know both, and know why they are the same test.
- The tick counter is written by an ISR and read by the main loop. It must be `volatile`, and
  on an 8- or 16-bit machine a 32-bit read is not atomic — say what you'd do about that even
  though the host build hides it.
- Deadlines are absolute, not remaining time. Storing "milliseconds left" and decrementing it
  makes every timer depend on being polled at a fixed rate.
- Periodic timers should advance `deadline += period`, never `deadline = now + period`. The
  second form accumulates drift on every late poll.

## What to test
List these in your own words before you write them, then write every case yourself.

- The counter near `0xFFFFFFFF`: a deadline set just before the wrap fires correctly just
  after it. This is the case the whole kata exists for, and it is about six lines.
- A deadline exactly equal to `now` — fires, not "one tick late."
- A one-shot timer fires exactly once, then goes inactive.
- A periodic timer polled late fires once and keeps its original phase (no drift).
- Cancel before expiry: never fires. Cancel from inside its own callback: does not corrupt the
  scheduler.
- Zero delay, and a delay of exactly half the counter range.
- No timers active: `scheduler_run` is a cheap no-op.

## Interview questions this lets you answer from experience
Why `millis()` rollover breaks a naive comparison and what the correct one is · why the
deadline must be absolute · sharing a 32-bit counter between an ISR and main · why `volatile`
is not atomicity · how a superloop schedules work without an RTOS · drift in a periodic task ·
what limits the maximum representable interval.

---

> **Variants:** seven, `v1` through `v7`, written up in [VARIANTS.md](VARIANTS.md).
> `make drill` picks one and `make done` logs the rep to
> [logs/log.tsv](../../../logs/log.tsv). Time is only comparable within a variant.
