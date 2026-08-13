# Katas

Fifteen modules. Six carried over from the earlier repo, five added to close the gaps the
first interview research exposed, one (`rollover_timer`) added because C11 was marked as a
kata in `plan/COVERAGE.md` with no kata behind it, and three Python modules added when the
second research pass showed that Python fluency is tested live and directly and that this
repo had no mechanism for it.

`fixed_point_pid` and `debouncer` are **retained** even though Mimic Stage 0 covers PID and
timing. Stage 0's PID runs in floating point, so the Q-notation reps are still yours to do, and
both katas are cheap reps on topics that get asked.

**They are not all weighted equally, and they should not be.** How many slots a module gets in
the seventy-day rotation is a consequence of two things, both checked by `make check-calendar`:

- Its target time has to fit the block it is scheduled into, so short modules go on sprint days
  and long ones on Wednesday and Sunday. There are only twenty long slots.
- Any module a capability is actually *scored* on needs at least three slots ending in three
  different variants, because that is the retirement bar.

`protocol_parser` is the one long module with two slots rather than three. That is deliberate:
its only capability is E21, whose evidence bar is the deck rather than the kata, so nothing is
blocked by not retiring it. Everything else that owns a bar gets three. Saturday's adaptive rep
is where the slack lives — it is the only day that can give any module a fourth or fifth go.

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
| 13 | `binary_frame_py` | struct, endianness, framing, TLV — the host side of the wire | **Python** |
| 14 | `log_parser_py` | streaming parse larger than RAM, reduce, exit codes | **Python** |
| 15 | `cli_tool_py` | argparse, device discovery by USB serial, retry decorators | **Python** |

The three Python modules run in their own daily block alongside the C rotation, not instead
of it. `binary_frame_py` is deliberately the same problem as `protocol_parser` seen from the
test harness rather than the firmware — do them close together.

Each module directory holds:

```
BRIEF.md      what it is, why firmware needs it, the API, how to think about it, what to test
VARIANTS.md   the variants the drill tool draws from
NOTES.md      one design decision and one bug, per rep. Append only.
include/      the frozen API contract. Committed. You do not edit this during a rep.
tests/        the frozen test suite. Committed. You do not edit this during a rep.
src/          GITIGNORED. Your implementation. Deleted at the start of every rep.
```

Every module ships with `BRIEF.md` and `VARIANTS.md` written. For each you owe the tests, and
for the C modules the header as well — a `*_py` module has no header, because its contract is
the API in the BRIEF and the suite is what enforces it. Read the BRIEF's "What to test" section — it lists the
cases in prose. Turning that list into actual test cases is the work, and it is yours.

## Target times

**`tools/drill.py:TARGETS` is the source of these numbers.** Every other tool imports them from
there, and `make check-calendar` fails if a target is longer than the calendar block that kata
is scheduled into. The table below is a reading copy.

| Kata | Target | Day type |
|---|---|---|
| `bitops` | 8 min | sprint |
| `mem_primitives` | 10 min | sprint |
| `register_map` | 12 min | sprint |
| `rollover_timer` | 12 min | sprint |
| `debouncer` | 12 min | sprint |
| `ring_buffer` | 15 min | long |
| `fsm` | 15 min | long |
| `pool_allocator` | 20 min | long |
| `protocol_parser` | 20 min | long |
| `fixed_point_pid` | 20 min | long |
| `concurrency_sim` | 25 min | long |
| `test_harness_py` | 25 min | long |
| `binary_frame_py` | 20 min | Python block |
| `log_parser_py` | 20 min | Python block |
| `cli_tool_py` | 25 min | Python block |

Targets are meant to fall. A kata that is comfortable at its target is a different exercise
three minutes lower — but lower the number in `drill.py`, not in your head, so the log still
means something.
