# Question bank

Everything from the interview research, formatted to drop into the kata repo. Split by practice
format because they need different mechanisms:

- `embedded-coding.md` — **(a) coding exercises.** Things you write. Map to katas.
- `embedded-concepts.md` — **(b) conceptual/verbal.** Things you say. Map to deck cards.
- `test-integration.md` — the T&I track, both (a) and (b), plus process/regulatory.
- `design-prompts.md` — **(c) explain-your-design** and "how would you test X." Rubric-scored.

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

## Topics that need new katas — flagged

Your six modules leave five real gaps. Each of these is a high-frequency interview topic that
does not fit any existing module, so forcing it in would weaken both.

| # | New kata | Why it can't fold into an existing module |
|---|---|---|
| 7 | `register_map` | `volatile`/`static`/`const` + memory-mapped I/O + struct padding is **the single most-asked embedded topic** and none of the six touch it. `bitops` is arithmetic on values; this is about *access semantics* and the type system. Different skill entirely. |
| 8 | `mem_primitives` | `memcpy`/`memmove`/`memset`/`strlen`/`strncpy` from scratch. Asked constantly. Pure pointer-and-bounds work; doesn't belong in `bitops` (no bit manipulation) or `protocol_parser` (no framing). |
| 9 | `pool_allocator` | Fixed-block allocator / your own `malloc`. Covers stack-vs-heap, fragmentation, alignment, and "why no malloc in firmware." No existing module allocates anything. |
| 10 | `concurrency_sim` | Mutex vs. semaphore, priority inversion, deadlock — run on host pthreads so it's practicable with no RTOS hardware. Roughly half of candidates fail this cluster. `ring_buffer` v5 touches ISR-safety but not scheduling or ownership. |
| 11 | `test_harness_py` | The T&I track's kata: pytest, fixtures, parametrize, driving a device over serial. Different language, different repo conventions, and it's the wedge. Must exist. |

Briefs for all five are in `practice/katas/`.

---

This repo is about building and proving the capability. It deliberately contains nothing about
where to apply or what to ask for.
