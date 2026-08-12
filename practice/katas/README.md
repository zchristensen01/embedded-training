# Katas

Twelve modules, all at full weight. Six carried over from the old repo, five added to close
the gaps the interview research exposed, and one (`rollover_timer`) added because C11 was
marked as a kata in `plan/COVERAGE.md` with no kata behind it.

`fixed_point_pid` and `debouncer` are **kept at full weight** even though Mimic Stage 0 covers
PID and timing. Stage 0's PID runs in floating point, so the Q-notation reps are still yours to
do, and both katas are cheap reps on topics that get asked.

| # | Kata | Topic cluster | Status |
|---|---|---|---|
| 1 | `ring_buffer` | ISR-safe queues, producer/consumer | existing |
| 2 | `debouncer` | timing, edge detection, non-blocking delays | existing |
| 3 | `fsm` | state machine design, protocol handlers | existing |
| 4 | `bitops` | bit manipulation, endianness, alignment | existing |
| 5 | `fixed_point_pid` | fixed-point math, control loops | existing |
| 6 | `protocol_parser` | framing, CRC, byte-stream parsing | existing |
| 7 | `register_map` | volatile/static/const, memory-mapped I/O, padding | **new** |
| 8 | `mem_primitives` | memcpy/memmove/strlen family from scratch | **new** |
| 9 | `pool_allocator` | fixed-block allocation, stack vs heap, alignment | **new** |
| 10 | `concurrency_sim` | mutex vs semaphore, priority inversion, deadlock | **new** |
| 11 | `test_harness_py` | pytest, fixtures, HIL, the T&I wedge | **new** |
| 12 | `rollover_timer` | tick counters, rollover-safe comparison, superloop scheduling | **new** |

Each module directory holds:

```
BRIEF.md      what it is, why firmware needs it, the API, how to think about it, what to test
VARIANTS.md   the variants the drill tool draws from
NOTES.md      one design decision and one bug, per rep. Append only.
include/      the frozen API contract. Committed. You do not edit this during a rep.
tests/        the frozen test suite. Committed. You do not edit this during a rep.
src/          GITIGNORED. Your implementation. Deleted at the start of every rep.
```

Target times, for `make report` to measure against:

| Kata | Target (clean, first compile) |
|---|---|
| `bitops` | 8 min |
| `mem_primitives` | 10 min |
| `register_map` | 12 min |
| `rollover_timer` | 12 min |
| `debouncer` | 12 min |
| `ring_buffer` | 15 min |
| `fsm` | 15 min |
| `pool_allocator` | 20 min |
| `protocol_parser` | 20 min |
| `fixed_point_pid` | 20 min |
| `concurrency_sim` | 25 min |
| `test_harness_py` | 25 min |
