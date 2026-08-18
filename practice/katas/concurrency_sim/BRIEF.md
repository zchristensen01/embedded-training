# Kata 10 — concurrency_sim

**In one sentence.** Concurrency primitives and their classic failure modes, built on host
threads so you can construct the bugs deliberately, watch them happen, and then fix them.

---

> **Before your first rep you owe this module two files:** `include/concurrency_sim.h` — the API
> contract — and the suite in `tests/`. Write the header first, then list the cases under
> **Tests it must pass** below in your own words, then write every one of them yourself. AI writes
> neither. `make drill` refuses a module whose header and tests do not exist, because a rep
> against an empty suite is not a rep. Both are frozen once written: you do not edit them
> during a rep, only your `src/`, which is deleted each time. See
> [DAILY.md](../../../DAILY.md#build-sessions).

## The problem, in plain language

The moment two pieces of code can run at overlapping times — two RTOS tasks, or an interrupt
and your main loop — everything you know about reading code line by line stops being true.
Between any two of your instructions, something else may have run.

This kata is different from the others. **You are not building a useful thing; you are
building four famous bugs on purpose and watching them fire.** You cannot learn this from
reading, and it is the one area where candidates who genuinely have shipped RTOS code and
candidates who have only read about it are trivially easy to tell apart.

### Bug 1 — the racing counter, and why `volatile` doesn't fix it

Two threads each increment a shared counter a million times. The total is not two million.

`count++` looks atomic. It is not — it is three separate steps:

```
   thread A                    thread B
   ─────────                   ─────────
   read count   → 5
                               read count   → 5
   add 1        → 6
                               add 1        → 6
   write count  ← 6
                               write count  ← 6

   two increments happened.  count went from 5 to 6.  ONE was lost.
```

Now the part people get wrong: **marking `count` volatile does not help.** `volatile`
guarantees the read and the write actually happen and are not cached in a register. It says
nothing about the gap between them. Reaching for `volatile` as a synchronisation primitive is
the single most common C concurrency error, and this kata is where you prove it to yourself
rather than take it on trust.

### Bug 2 — mutex vs semaphore, the trap question

**A mutex has an owner. A semaphore does not.** Everything else follows from that one fact,
and being able to derive the rest out loud is the answer:

| | Mutex | Semaphore |
|---|---|---|
| Purpose | protect a shared **resource** | **signal** between parties, or count them |
| Ownership | only the thread that took it can give it back | anyone can give it, including an ISR |
| Priority inheritance | possible, *because* there is an owner to boost | impossible — there is nobody to boost |
| Take from an ISR? | **No.** An ISR has no task context to own it | Giving is fine; that is the standard ISR-to-task signal |

The trap answer — *"they're basically the same, a semaphore just counts higher than one"* —
is so common that Barr Group wrote a whole article about it, and Niall Cooling of Feabhas
puts it at roughly half of everyone claiming RTOS experience. **Say the trap out loud as
part of your answer**, and you have separated yourself from that half in one sentence.

### Bug 3 — priority inversion, which needs three tasks

This is the one people half-know. A high-priority task ends up waiting on a low-priority
one — fine, bounded, that's just lock contention. What makes it *inversion* is a third task
that needs no lock at all:

```
   priority

   HIGH  │        ┌── blocks on the mutex ─────────────────────────┐ runs
         │        │                                               │
   MED   │        │      ┌─ preempts LOW, needs no lock ───────┐   │
         │        │      │   runs as long as it likes          │   │
   LOW   │ ─ takes mutex ┘                                     └─ finishes, releases
         │
         └──────────────────────────────────────────────────────────────▶ time
                           ▲
                  HIGH is now waiting on MED, which it outranks,
                  for an UNBOUNDED amount of time
```

High is blocked on Low. Low can't run because Med preempted it. So High effectively waits
for Med — a task of lower priority that it never even shared a resource with — and nothing
bounds how long that lasts. **This is what put the Mars Pathfinder into a reset loop in
1997**, and it is the standard worked example.

The fix is *priority inheritance*: while Low holds a mutex that High wants, Low temporarily
runs at High's priority, so Med cannot preempt it. This is only possible because a mutex has
an owner to promote — which is why the answer loops back to Bug 2.

**If you cannot reproduce this with three threads, you do not have it yet.** Two threads
produce ordinary blocking, not inversion, and describing it without the medium-priority task
is the trap.

### Bug 4 — deadlock, and the four conditions

Two threads, two locks, taken in opposite orders:

```
   thread A               thread B
   ────────               ────────
   lock(X)   ✓            lock(Y)   ✓
   lock(Y)   ⋯ waits      lock(X)   ⋯ waits
                              ↑
                    neither will ever proceed
```

Deadlock requires **all four** of these at once, and the whole value of the list is that
breaking any *one* of them is a fix:

1. **Mutual exclusion** — the resource can't be shared
2. **Hold and wait** — you hold one while asking for another
3. **No preemption** — locks can't be forcibly taken away
4. **Circular wait** — A waits for B waits for A

Naming only "circular wait" is the trap. The practical fix is almost always to break #4 with
a **global lock ordering**: every thread takes X before Y, never the reverse. Say which
condition your fix breaks and you sound like you have done it.

---

## Why firmware needs this

Mutex-vs-semaphore and priority inversion are the two questions candidates claiming RTOS
experience most reliably get wrong. You cannot bluff them, because the follow-up is always
"give me an example" — and building a priority inversion and watching the high-priority
thread starve is worth ten articles.

Be honest about what this kata is and is not: it gets the *questions* answered well from
real experience. **It is not RTOS experience and should never be described as such.** That
comes from Mimic's Stage 1, and it lands after these fourteen weeks.

---

## What you need from C

```c
#include <pthread.h>   /* pthread_create, pthread_mutex_t, pthread_cond_t */
#include <stdatomic.h> /* atomic_int, for the "fixed" counter */
```

Host pthreads stand in for RTOS tasks. The mapping is close enough that the lessons
transfer:

| Here (pthreads) | On an RTOS |
|---|---|
| `pthread_create` | `xTaskCreate` / `osThreadNew` |
| `pthread_mutex_t` | a mutex, usually with inheritance available |
| `pthread_cond_t` | a task notification, event flag or counting semaphore |
| thread priority via scheduling attributes | task priority, and it is the whole game |

**A condition variable is how you block until something becomes true**, and it is the piece
of machinery the bounded queue needs. The shape never varies:

```c
   pthread_mutex_lock(&m);
   while (!condition)                    /* while, NOT if */
       pthread_cond_wait(&cv, &m);       /* atomically unlocks m and sleeps */
   /* ... condition is true and you hold the lock ... */
   pthread_mutex_unlock(&m);
```

**It must be `while`, not `if`.** A waiting thread can be woken without the condition being
true — a *spurious wakeup*, which is permitted by the standard — and can also lose a race to
another consumer between waking and reacquiring the lock. `if` means you carry on as though
the condition held when it does not. This is a real interview question.

---

## The API you are writing

```c
/* v1-v2 */
void bq_init(bqueue_t *q, void *storage, size_t cap, size_t elem);
bool bq_put(bqueue_t *q, const void *item);   /* blocks when full */
bool bq_get(bqueue_t *q, void *out);          /* blocks when empty */

/* v3-v4 */
void inversion_demo(bool with_inheritance, results_t *out);
```

`bq_*` is a **bounded blocking queue** — the same ring buffer from kata 1, but where a full
`put` sleeps until a consumer makes room rather than returning false. That is the standard
producer/consumer structure, and the one place a beginner's version usually has a lost
wakeup.

`inversion_demo` runs the three-thread scenario and reports High's measured wait time, with
and without inheritance. Making the *difference* the assertion is what turns a demo into a
test.

---

## Note on toolchain

This module builds with `-fsanitize=thread` instead of address+undefined, because TSan and
ASan cannot coexist in one binary. `make test` already selects it per module — nothing to do.

ThreadSanitizer is the point, not a formality: it detects a data race even on a run where the
timing happened to work out, which is exactly the class of bug that otherwise appears once a
fortnight in the field and never at your desk.

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

1. Write out the interleaving that loses an increment, as a two-column trace like the one
   above. Now add `volatile` to the counter and explain why the same trace still happens.
2. For the bounded queue: how many condition variables do you need, and what does each one
   mean? (One is workable. Two — "not full" and "not empty" — is better, and being able to
   say why is the answer.)
3. Draw the priority-inversion timeline yourself, with the three threads, and mark the exact
   moment the inversion begins.
4. For your deadlock demo, state which of the four conditions your fix breaks.
5. What is the invariant for the queue? *Every item put is got exactly once, in order, and
   the count never exceeds capacity.* That is three tests.

Then write it. `v1`–`v2` is about 80 lines; the demos are shorter than they look.

---

## Tests it must pass

| Test | What it's protecting against |
|---|---|
| Bounded queue with producers and consumers at different rates: total in equals total out, no duplicates, no losses, under TSan | Lost wakeups and the `if`-instead-of-`while` bug |
| `bq_put` on a full queue **blocks** rather than spinning or failing | Busy-waiting, which is the wrong answer and burns a core |
| Inversion demo: without inheritance, High's wait scales with Med's runtime; with it, it doesn't. Assert on the measured difference | A demo that "shows" inversion without measuring it proves nothing |
| Deadlock demo reproduces, then the lock-ordered version completes | That your fix is the fix, not a timing accident |
| Racing counter: the unsynchronised version is wrong at least once in N runs; the synchronised version is always right | The whole `volatile` argument, made empirically |

That last one needs care: a race that fails only sometimes is a test that fails only
sometimes. Assert "at least one of N runs was wrong" rather than "this run was wrong", and
let TSan catch the rest deterministically.

---

## Once it's boring

*Boring* means: blank file to working, TSan-clean, in under twenty-five minutes, never
unsure what to type next. Then add a constraint.

**Second pass — priority ceiling instead of inheritance.** Inheritance boosts the holder
when a higher-priority task blocks. Ceiling raises the holder to the lock's declared maximum
the moment it is taken, unconditionally. Implement it and work out the trade-off: ceiling
avoids the inversion ever starting but penalises every lock acquisition. Both ship in real
RTOSes.

**Third pass — lock-free single-producer single-consumer.** Take the queue back to the
sacrificed-slot ring buffer from kata 1, with `head` written only by the producer and `tail`
only by the consumer, using `stdatomic` with explicit acquire/release ordering. Then run it
under TSan and be genuinely pleased when it is clean. This is the version that goes in an
ISR.

---

> **Variants:** seven, `v1` through `v7`, written up in [VARIANTS.md](VARIANTS.md).
> `make drill` picks one and `make done` logs the rep to
> [logs/log.tsv](../../../logs/log.tsv). Time is only comparable within a variant.

## Interview questions this lets you answer from experience

Mutex vs semaphore, including the trap · priority inversion with a concrete example ·
priority inheritance and priority ceiling · the four deadlock conditions · race condition vs
data race · producer-consumer · why `volatile` isn't synchronisation · preemptive vs
cooperative scheduling.
