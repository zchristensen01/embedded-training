# (a) Coding exercises — embedded

Things you write, not things you say. Each block names the kata it drills.

---

## Bit manipulation — kata `bitops`

1. Set, clear, and toggle bit N of a `uint32_t`.
2. Test whether bit N is set. Return a `bool`, not an `int`.
3. Count the set bits in a word. Then do it without a loop.
4. Find the position of the highest set bit. Then implement Count Leading Zeros without the
   hardware instruction.
5. Swap the MSB and LSB of a 16-bit value.
6. Swap two variables without a temporary.
7. Reverse the bit order of a byte.
8. Check whether a value is a power of two, in one expression.
9. Multiply by 15, 30, and 60 using only shifts and adds.
10. Clear the lowest set bit. Isolate the lowest set bit.
11. Extract a bitfield: given `value`, `start`, and `width`, return the field, right-aligned.
12. Write a macro that builds a mask of `n` bits, correct for `n == 0` and `n == 32`.

**What fails candidates here:** shifting signed types, `1 << 31` on a signed `int` (undefined),
and forgetting `unsigned` on the literal. Use `1u`. Every time.

---

## Endianness and alignment — kata `bitops`, kata `register_map`

13. Byte-swap a `uint16_t` and a `uint32_t` with shifts and masks.
14. Detect the endianness of the machine at runtime. Then explain why the compile-time answer is
    better.
15. Read a big-endian 32-bit value out of a `uint8_t` buffer, portably — no casting the buffer
    pointer to `uint32_t*`.
16. Check whether an address is 4-byte aligned. Then 8-byte, generically.
17. Given a struct, predict its `sizeof` before compiling. Then reorder the members to make it
    smaller. Verify with `offsetof`.

---

## Memory primitives — kata `mem_primitives` (new)

18. `strlen`.
19. `strcpy`, then `strncpy` — and state what `strncpy` does that surprises people (no
    guaranteed null terminator).
20. `memset`.
21. `memcpy`.
22. `memmove` — and explain why it exists when `memcpy` already does.
23. `strcmp`.
24. Reverse a string in place.
25. Reverse the words in a sentence in place.
26. `atoi`, handling sign and overflow. Then `itoa` without `sprintf`.

---

## Buffers and queues — kata `ring_buffer`

27. Ring buffer with `init`, `put`, `get`, `is_full`, `is_empty`, `count`.
28. The same, distinguishing full from empty with a sacrificial slot instead of a count.
29. The same, with a power-of-two size and no modulo anywhere.
30. Overwrite-oldest-on-full behaviour.
31. Single-producer/single-consumer, lock-free, safe against an ISR producer.
32. Generic element size using `void*` and `memcpy`.
33. A stack with a fixed backing array, no allocation.
34. A fixed-size FIFO of structs, by value, no pointers into the buffer escaping.

---

## Allocation — kata `pool_allocator` (new)

35. A fixed-block pool allocator: `pool_init`, `pool_alloc`, `pool_free`, with a free list
    threaded through the free blocks themselves.
36. Make it alignment-correct for the worst-case type.
37. Add double-free detection.
38. A bump allocator with no free at all. State when that's the right answer.
39. Sketch a general `malloc`/`free` with a linked free list and coalescing. Paper is fine.

---

## Registers and hardware access — kata `register_map` (new)

40. Declare a pointer to a memory-mapped 32-bit register at `0x40020000`, read-write.
41. Declare a read-only status register.
42. Declare a pointer that is itself constant but points to volatile data. Then all four
    combinations of `const`/`volatile` on pointer and pointee, and say what each means.
43. Set bit 3 of a register without disturbing the others. Then clear it. Then toggle it.
44. Write a `MODIFY_REG(reg, mask, value)` macro that's safe against double evaluation.
45. Given a datasheet register table, write the struct that overlays the peripheral, and check
    it with `_Static_assert(sizeof(...) == ...)`.
46. Write a delay loop the compiler cannot optimise away.

---

## State machines and timing — katas `fsm`, `debouncer`

47. Debounce a button with sample-and-count. Then with a timer. Then handle both edges.
48. Detect a long-press versus short-press versus double-press.
49. A traffic-light controller as a table-driven state machine. Then as a switch. Then with
    function pointers. Compare.
50. A state machine that parses a fixed command protocol byte-by-byte from a stream.
51. A non-blocking `millis()`-style scheduler running three tasks at different periods.
52. Handle timer rollover correctly. Show why `if (now > next)` is a bug and `if ((now - next) <
    (1u << 31))` or unsigned subtraction is the fix.

---

## Protocols and framing — kata `protocol_parser`

53. Parse a length-prefixed frame from a byte stream that arrives in arbitrary chunks.
54. The same for a delimiter-framed protocol with escaping.
55. CRC-8 or CRC-16, table-driven and bitwise. Know the difference in cost.
56. Validate a frame: length, checksum, and a bounds check that can't overflow.
57. Bit-bang a UART transmit in software given a delay function.
58. Bit-bang SPI mode 0. Then parameterise CPOL and CPHA.

---

## Concurrency — kata `concurrency_sim` (new)

59. Producer-consumer with a bounded buffer, using a mutex and condition variables.
60. Construct a priority inversion on host pthreads and demonstrate it. Then fix it.
61. Construct a deadlock and then break it by lock ordering.
62. Make a shared counter correct across threads. Then explain why `volatile` alone doesn't do
    it.
63. Implement a critical section for an 8-bit MCU: save interrupt state, disable, restore. Show
    why naive disable/enable is a bug when nested.

---

## Fixed point — kata `fixed_point_pid`

64. Q16.16 multiply and divide with correct rounding and no overflow.
65. A PID controller in fixed point with anti-windup.
66. A moving average filter with no division, using a power-of-two window.

---

## Algorithms — the small subset worth doing

The research found LeetCode largely absent at your target companies. Do these ten only, in C,
because they're the ones that actually recur in embedded screens:

67. Reverse a singly linked list, iteratively.
68. Detect a cycle in a linked list.
69. Find the middle of a linked list in one pass.
70. Two-sum on a sorted array with two pointers.
71. Merge two sorted arrays in place.
72. Binary search, and get the boundary conditions exactly right.
73. Remove duplicates from a sorted array in place.
74. Valid parentheses with a fixed-size stack.
75. Find the single non-duplicated element using XOR.
76. Rotate an array in place.

Do not go further down the LeetCode path this cycle.
