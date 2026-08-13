# Kata 10 — concurrency_sim

> **Before your first rep you owe this module two files:** `include/concurrency_sim.h` — the API
> contract — and the suite in `tests/`. Write the header first, then list the cases under
> **What to test** below in your own words, then write every one of them yourself. AI writes
> neither. `make drill` refuses a module whose header and tests do not exist, because a rep
> against an empty suite is not a rep. Both are frozen once written: you do not edit them
> during a rep, only your `src/`, which is deleted each time. See
> [DAILY.md](../../../DAILY.md#build-sessions).

## What it is
Concurrency primitives and failure modes, built and observed on host pthreads so you can
practise without RTOS hardware. You construct the bugs deliberately, watch them happen, then fix
them.

## Why firmware needs it
Mutex vs. semaphore and priority inversion are the two questions candidates claiming RTOS
experience most reliably get wrong — Barr Group's write-up on the pair exists precisely because
the confusion is so common. You cannot bluff this and you cannot learn it from reading. Building
a priority inversion and watching the high-priority thread starve is worth ten articles.

## The API you implement
```c
/* v1-v2 */
void bq_init(bqueue_t *q, void *storage, size_t cap, size_t elem);
bool bq_put(bqueue_t *q, const void *item);   /* blocks when full */
bool bq_get(bqueue_t *q, void *out);          /* blocks when empty */

/* v3-v4 */
void inversion_demo(bool with_inheritance, results_t *out);
```

## How to think about it
- A mutex has an owner. A semaphore does not. Everything else follows from that: only the owner
  can release a mutex, which is what makes priority inheritance possible, which is why a
  semaphore cannot fix priority inversion.
- Priority inversion needs three tasks, not two. Low holds the lock, High blocks on it, and
  Medium — which needs no lock at all — preempts Low. High now waits on Medium indirectly, with
  no bound. If you can't reproduce that with three threads, you don't have it yet.
- Deadlock needs all four conditions. Break exactly one and say which.
- `volatile` does not make a shared counter correct. Prove it: build the racing counter, watch
  it produce wrong totals under ThreadSanitizer, then fix it properly.

## What to test
- Bounded queue: producers and consumers at different rates, total items in equals total out,
  no duplicates, no losses, run under ThreadSanitizer.
- Blocking behaviour: put on a full queue blocks rather than spinning or failing.
- Inversion demo: without inheritance, High's wait time scales with Medium's runtime. With
  inheritance, it doesn't. Assert on the measured difference.
- Deadlock demo: reproduce it, then assert that the lock-ordered version completes.
- Racing counter: assert the unsynchronised version is wrong at least once in N runs, and the
  synchronised version is always right.

## Note on toolchain
This module builds with `-fsanitize=thread` instead of address+undefined, because TSan and ASan
cannot coexist in one binary. `make test` already selects it per module — nothing to do.

## Interview questions this lets you answer from experience
Mutex vs. semaphore, including the trap · priority inversion with a concrete example · priority
inheritance and priority ceiling · the four deadlock conditions · race condition vs. data race ·
producer-consumer · why volatile isn't synchronisation · preemptive vs. cooperative scheduling.
