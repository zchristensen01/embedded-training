# (b) Conceptual and verbal questions — embedded

Things you say. Each entry: the question, what a strong answer contains, and the common wrong
answer that fails candidates. Every one of these should end up as a deck card in
`practice/decks/embedded.tsv`.

**Practice rule:** answer out loud, in full sentences. A pass requires naming the trap.

---

## The `volatile` / `static` / `const` cluster — kata `register_map`

**Q: What does `volatile` do?**
Strong: tells the compiler the value can change outside the program's control — a hardware
register, or a variable modified by an ISR — so it must not cache it in a register or optimise
away reads and writes. Every access happens exactly as written.
Trap: believing `volatile` provides atomicity. It does not. A 32-bit access on an 8-bit MCU is
four instructions and an interrupt can land in the middle. You still need a critical section or
`stdatomic.h`.

**Q: When would you use `const volatile` together?**
Strong: a read-only hardware status register. The hardware changes it, your program must not.
Trap: calling it a contradiction.

**Q: What does `static` do?**
Strong: two different jobs. On a local variable it changes lifetime — the variable persists
across calls. On a global or a function it changes linkage to internal, so the symbol isn't
visible outside the translation unit.
Trap: saying static locals live on the stack. They live in `.data` (if initialised non-zero) or
`.bss` (if zero-initialised).

**Q: Declare a pointer to a memory-mapped register.**
Strong: `volatile uint32_t * const UART_DR = (volatile uint32_t *)0x40020000;` — and be able to
say that the pointer is constant, the data is volatile, and why both matter.
Trap: getting the `const` on the wrong side and not noticing.

**Q: Where does a `const` array live on an MCU?**
Strong: typically flash, not RAM, which is exactly why you mark large lookup tables `const` on a
2 KB-RAM part.

---

## Memory model — katas `pool_allocator`, `mem_primitives`

**Q: Stack or heap in firmware?**
Strong: prefer static and stack. Avoid `malloc`: fragmentation over long runtimes,
non-deterministic timing, and failure modes that appear after weeks of uptime. If you must
allocate, take one large block at startup, or use a fixed-block pool.
Trap: "heap is fine, we have enough RAM."

**Q: Which way does the stack grow?**
Strong: down, on most architectures — but say "on ARM Cortex-M and x86 it grows toward lower
addresses" rather than asserting universally.

**Q: How do you know your stack is big enough?**
Strong: paint the stack with a pattern at startup and measure the high-water mark; in FreeRTOS,
`uxTaskGetStackHighWaterMark`. Worst-case is nested interrupts on top of the deepest call chain.

**Q: What happens before `main()` runs?**
Strong: reset vector, set the stack pointer, copy `.data` from flash to RAM, zero `.bss`,
optionally run C++ static constructors, then call `main`.
Trap: not knowing `.bss` is zeroed by startup code rather than by the loader.

**Q: Why does this struct occupy more bytes than its members?**
Strong: padding inserted so each member meets its alignment requirement, plus tail padding so
arrays of the struct stay aligned. Reorder largest-to-smallest to shrink it. `#pragma pack`
trades access speed (and on some architectures, correctness) for size.

**Q: `memcpy` vs `memmove`?**
Strong: `memmove` is defined for overlapping regions; `memcpy` is not. `memcpy` may copy in any
order or in wide chunks.

---

## Interrupts — kata `ring_buffer`

**Q: What must you never do inside an ISR?**
Strong: block, wait on a mutex, call non-reentrant functions, allocate memory, or run long.
`printf` is the canonical banned example — it's slow, often non-reentrant, and may allocate. Do
the minimum: set a flag, push a byte into a ring buffer, or give a semaphore, and defer the rest
to a task or the main loop.
Trap: "keep it short" without being able to say *why* — the reason is interrupt latency for
everything else in the system and re-entrancy hazards.

**Q: How do you share data between an ISR and main with no OS?**
Strong: `volatile` for the flag, and a critical section (briefly disable interrupts) around any
multi-byte read-modify-write. For a single-producer/single-consumer byte queue you can do it
lock-free with careful index ordering.
Trap: `volatile` alone on a multi-byte value.

**Q: What is interrupt latency and what makes it worse?**
Strong: time from the hardware event to the first instruction of the handler. Made worse by long
critical sections, higher-priority handlers, and non-preemptible regions.

**Q: What is a nested interrupt and why would you allow it?**
Strong: a higher-priority interrupt preempting a running handler. Allowed when one source has a
hard latency requirement. Costs stack depth and re-entrancy safety.

---

## Concurrency and RTOS — kata `concurrency_sim`

**Q: Mutex vs. semaphore?**
Strong: a mutex has ownership — only the task that took it can give it — and supports priority
inheritance. Use it to protect a shared resource. A semaphore is a signalling and counting
primitive; anything, including an ISR, can give it. Use it for ISR-to-task notification or to
count available resources. You cannot take a mutex in an ISR because an ISR has no task context
to own it.
Trap: **this is the flagged failing answer.** "They're basically the same, semaphores just count
higher than one." Michael Barr of the Barr Group names exactly this as the common wrong answer,
and Niall Cooling of Feabhas has said around half of candidates claiming RTOS expertise make it.
Say the trap out loud as part of your answer.

**Q: What is priority inversion?**
Strong: a high-priority task blocks on a resource held by a low-priority task, and a
medium-priority task then preempts the low-priority holder — so the high-priority task waits on
the medium one indirectly, with no bound. Fix with priority inheritance (boost the holder to the
waiter's priority) or a priority ceiling (the resource carries a priority).
Trap: describing it as just "a low-priority task holds a lock" without the medium task, which is
what makes it unbounded.

**Q: The four conditions for deadlock?**
Strong: mutual exclusion, hold-and-wait, no preemption, circular wait. Break any one; lock
ordering breaks circular wait and is the usual practical fix.

**Q: Preemptive vs. cooperative scheduling?**
Strong: preemptive means the scheduler can take the CPU at a tick or on a higher-priority task
becoming ready; cooperative means tasks yield. Cooperative is simpler and needs less stack and
less locking, but one badly behaved task starves everything.

**Q: What is a race condition, and how is it different from a data race?**
Strong: a data race is two threads touching the same location, one writing, with no
synchronisation — undefined behaviour. A race condition is any timing-dependent incorrect
behaviour, which can exist even with perfect locking.

---

## Protocols — katas `protocol_parser`, `fsm`

**Q: Compare UART, SPI, I2C, CAN.**
Strong, in this order — wires, sync/async, duplex, addressing, topology, speed, use:
- UART: 2 wires (TX/RX), asynchronous, no clock, full-duplex, point-to-point, both ends must
  agree on baud rate. Start/stop bits, optional parity.
- SPI: 4 wires (MOSI, MISO, SCLK, SS), synchronous, full-duplex, fastest, one master, **no
  addressing** — you select by chip-select line. CPOL and CPHA define the four modes.
- I2C: 2 shared wires (SDA, SCL), synchronous, half-duplex, addressed (7- or 10-bit),
  multi-master capable, needs pull-up resistors because it's open-drain, supports clock
  stretching by the slave.
- CAN: differential pair, multi-master, arbitration by message ID (lower ID wins), built for
  electrical noise, message-oriented rather than address-oriented.
Trap: not knowing SPI has no built-in addressing, or forgetting I2C's pull-ups.

**Q: Why does I2C need pull-ups?**
Strong: the bus is open-drain — devices can only pull low. The pull-up provides the high level,
and its value trades rise time against current.

**Q: What is clock stretching?**
Strong: a slave holds SCL low to make the master wait. Some masters handle it badly, which is a
classic field bug.

**Q: What does a CRC give you that a checksum doesn't?**
Strong: much better detection of burst errors and of common corruption patterns. It's error
*detection*, not correction, and not a cryptographic integrity guarantee.

**Q: What is DMA and what goes wrong with it?**
Strong: peripheral-to-memory transfer without CPU involvement. Watch for cache coherency on
parts with a cache, buffer ownership between the CPU and the DMA engine, and handling
half-transfer versus complete interrupts. Circular DMA is the standard trick for continuous UART
receive.

---

## Hardware and debugging

**Q: You have intermittent communication failures. Walk me through it.**
Strong, in order: reproduce it and characterise when it happens; check power rails and grounds
first; check the clock; put a logic analyzer on the bus and trigger on the error condition;
compare timing against the datasheet margins; change one variable at a time; check what differs
between working and failing units. Document with captured traces.
Trap: starting with the code.

**Q: Scope or logic analyzer?**
Strong: a logic analyzer for protocol decode and timing across many lines; a scope for signal
integrity — ringing, rise time, noise, voltage levels. Bus looks right but the device
misbehaves? Scope it.

**Q: What is a pull-up resistor for?**
Strong: define a default level on a line that would otherwise float, for open-drain buses and for
inputs like buttons. Value trades current against noise immunity and rise time.

**Q: What is Nyquist and why do you care?**
Strong: sample at more than twice the highest frequency of interest or you get aliasing, which
you cannot undo after the fact. Anti-alias filter before the ADC.

**Q: JTAG vs SWD?**
Strong: both are debug interfaces; SWD uses two pins instead of JTAG's four or five and is the
usual choice on Cortex-M where pin count matters.

**Q: What is a watchdog and how do you use it correctly?**
Strong: a timer that resets the device if not serviced. Correct use kicks it from one place that
can only be reached when every critical task has reported healthy — not from inside each task,
and never from a timer interrupt, which defeats the point.
