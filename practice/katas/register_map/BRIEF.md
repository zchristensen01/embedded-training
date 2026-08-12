# Kata 7 — register_map

## What it is
A simulated peripheral: a block of memory you treat as memory-mapped hardware registers, plus
the accessor layer over it. You write the header declarations, the read/modify/write helpers,
and the overlay struct. The tests poke the backing memory the way hardware would and check that
your accessors did exactly the right reads and writes, in the right order, with nothing
optimised away.

## Why firmware needs it
Every driver you will ever write starts here. And the `volatile` / `static` / `const` /
pointer cluster is the single most-asked embedded interview topic — none of your other six
modules touch access semantics at all. `bitops` operates on values; this operates on
*locations*.

## The API you implement
```c
/* frozen in include/register_map.h */
#define REG_CTRL   0x00u   /* rw */
#define REG_STATUS 0x04u   /* ro */
#define REG_DATA   0x08u   /* rw */

void     reg_write(uintptr_t base, uint32_t off, uint32_t val);
uint32_t reg_read (uintptr_t base, uint32_t off);
void     reg_set_bits  (uintptr_t base, uint32_t off, uint32_t mask);
void     reg_clear_bits(uintptr_t base, uint32_t off, uint32_t mask);
void     reg_modify(uintptr_t base, uint32_t off, uint32_t mask, uint32_t val);
bool     reg_wait_flag(uintptr_t base, uint32_t off, uint32_t mask, uint32_t timeout);
```

## How to think about it
- Volatility is a property of the *pointee*, not the pointer. Say the declaration out loud in
  English every time you write it: "a constant pointer to volatile 32-bit unsigned data."
- Read-modify-write on a register is three bus transactions and is not atomic. If an ISR touches
  the same register, you need a critical section.
- Some hardware registers have read side effects — reading clears a flag. That is why an extra
  read the compiler inserted, or one it removed, is a real bug.
- `reg_modify` must not evaluate its arguments twice. This is why it's a function, or a very
  carefully written macro.

## What to test
- Each accessor produces exactly the expected sequence of accesses, no more and no less.
- Set/clear/modify leave untouched bits untouched.
- Read-only register write is rejected or asserts, depending on the variant.
- Overlay struct has the exact expected `sizeof` and member offsets (`_Static_assert`).
- Timeout path in `reg_wait_flag` returns false and does not spin forever.
- Mask of 0 and mask of all-ones both behave.

## Interview questions this lets you answer from experience
Declare a pointer to a memory-mapped register · all four const/volatile combinations · why
volatile is not atomicity · where a const array lives on an MCU · struct padding and
`offsetof` · bitfields vs. mask-and-shift and why bitfields are risky · a delay loop the
compiler cannot remove.
