# register_map — variants

v1  Basic accessors over a `volatile uint32_t *` base. Read, write, set, clear.
v2  Add `reg_modify` with a single read-modify-write and no double evaluation of arguments.
v3  Add a read-only register: writes must be rejected. Introduces `const volatile`.
v4  Overlay struct version: define a packed peripheral struct, assert its layout with
    `_Static_assert`, and reimplement the accessors through it.
v5  Bitfield version: same peripheral via C bitfields. Then write NOTES.md on what portability
    guarantees you just gave up.
v6  Interrupt-safe: an ISR simulator mutates the register between your read and your write. Make
    read-modify-write correct with a critical section.
v7  8-bit device: registers are `uint8_t`, the bus is byte-wide, and a 32-bit field spans four
    registers. Get the ordering right.
