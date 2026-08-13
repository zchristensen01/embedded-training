# Question bank

Everything from the interview research, split by practice format because each needs a different
mechanism:

- `embedded-coding.md` — **(a) coding exercises.** Things you write. Map to katas.
- `embedded-concepts.md` — **(b) conceptual/verbal.** Things you say. Map to deck cards.
- `test-integration.md` — the T&I track, both (a) and (b), plus process/regulatory.
- `../../practice/design-prompts/SUBJECTS.md` — **(c) explain-your-design** and "how would you
  test X." Rubric-scored, and drawn from by `make prompt`.
- `../../practice/design-prompts/ARCHITECTURE.md` — **(d) design this subsystem.** A different
  exercise with a different rubric, drawn from by `make design`. Do not confuse it with (c):
  one tests a thing that exists, the other invents one.
- **Python fluency** has no separate question file. Its questions are all deck cards, in
  `../../practice/decks/python.tsv`, because every one of them is a "what does this print and
  why" answered out loud.

---

## Topic → kata map

| Topic cluster | Existing kata | Status |
|---|---|---|
| Bit manipulation, endianness, alignment checks | `bitops` | Covered |
| ISR-safe queues, producer/consumer, SPSC | `ring_buffer` | Covered |
| Timing, edge detection, non-blocking delays | `debouncer` | Covered |
| State machine design, protocol handlers | `fsm` | Covered |
| Framing, CRC, byte-stream parsing | `protocol_parser` | Covered |
| Fixed-point math, control loops | `fixed_point_pid` | Covered |
| `volatile`/`static`/`const`, memory-mapped I/O | `register_map` | Covered |
| memcpy/memmove/strlen from scratch | `mem_primitives` | Covered |
| Fixed-block allocation, alignment | `pool_allocator` | Covered |
| Mutex vs semaphore, priority inversion | `concurrency_sim` | Covered |
| Tick counters, rollover-safe comparison | `rollover_timer` | Covered |
| pytest, fixtures, HIL | `test_harness_py` | Covered |
| struct, endianness, framing on the host | `binary_frame_py` | Covered |
| Streaming parse, reduce, exit codes | `log_parser_py` | Covered |
| argparse, device discovery, retry | `cli_tool_py` | Covered |

## Topics that needed new katas

The six original modules left six real gaps. Each is a high-frequency interview topic that does
not fit any existing module, so forcing it in would weaken both.

| # | New kata | Why it can't fold into an existing module |
|---|---|---|
| 7 | `register_map` | `volatile`/`static`/`const` + memory-mapped I/O + struct padding is **the single most-asked embedded topic** and none of the six touch it. `bitops` is arithmetic on values; this is about *access semantics* and the type system. Different skill entirely. |
| 8 | `mem_primitives` | `memcpy`/`memmove`/`memset`/`strlen`/`strncpy` from scratch. Asked constantly. Pure pointer-and-bounds work; doesn't belong in `bitops` (no bit manipulation) or `protocol_parser` (no framing). |
| 9 | `pool_allocator` | Fixed-block allocator / your own `malloc`. Covers stack-vs-heap, fragmentation, alignment, and "why no malloc in firmware." No existing module allocates anything. |
| 10 | `concurrency_sim` | Mutex vs. semaphore, priority inversion, deadlock — run on host pthreads so it's practicable with no RTOS hardware. The cluster candidates most reliably fail. `ring_buffer` v2 touches ISR-safety but not scheduling or ownership. |
| 11 | `test_harness_py` | The T&I track's kata: pytest, fixtures, parametrize, driving a device over serial. Different language, different conventions, and it is the wedge. Must exist. |
| 12 | `rollover_timer` | C11 was marked as a kata in `plan/COVERAGE.md` with no kata behind it. Tick counters, the rollover-safe comparison, and superloop scheduling — the famous bug that only shows up after 49.7 days of uptime. |

Briefs for all six are in `practice/katas/`.

## The three Python katas

A second research pass established that Python fluency is tested live and directly — Tesla
runs a standalone 90-minute Python assessment for test roles, Qualcomm quizzes decorators and
map/filter/reduce — and that this repo had no mechanism for it. `test_harness_py` covers
pytest, not the language underneath it.

| # | New kata | Why it can't fold into an existing module |
|---|---|---|
| 13 | `binary_frame_py` | The host side of a wire protocol. `protocol_parser` is the firmware side in C; this is `struct`, endianness and framing in Python, where every failure is silent. Deliberately the same problem from the other end. |
| 14 | `log_parser_py` | Streaming a file larger than RAM, reducing it, exiting with the right code. The shape of every reported T&I live-coding task. Nothing else here forbids you from loading the input. |
| 15 | `cli_tool_py` | argparse, selecting a board by USB serial number rather than enumeration order, and writing a `retry` decorator with `functools.wraps`. All three confirmed as real interview content; none of them fit a parsing kata. |

---

This repo is about building and proving the capability. It deliberately contains nothing about
where to apply or what to ask for — `.gitignore` reserves `plan/APPLICATIONS.md` and
`plan/private/` for that, so there is an obvious place to put it that is not here.
