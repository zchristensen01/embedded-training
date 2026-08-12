# Kata 9 — pool_allocator

## What it is
A fixed-block memory allocator over a static backing array, with the free list threaded through
the free blocks themselves.

## Why firmware needs it
Dynamic allocation is banned or heavily restricted in most firmware, and "why don't you use
malloc" is a standard interview question. The convincing answer is that you've written the thing
that replaces it. None of your other modules allocate anything.

## The API you implement
```c
typedef struct pool pool_t;

void  pool_init(pool_t *p, void *backing, size_t backing_size, size_t block_size);
void *pool_alloc(pool_t *p);
void  pool_free(pool_t *p, void *block);
size_t pool_available(const pool_t *p);
```

## How to think about it
- The free list costs no extra memory: while a block is free, its first bytes hold the pointer to
  the next free block. Drawing this on paper before coding is the whole exercise.
- `block_size` must be at least `sizeof(void *)` and aligned to `alignof(max_align_t)`. Assert
  it.
- Allocation and free are both O(1). That determinism is the actual reason firmware uses pools.
- Alignment of the backing array is your problem, not the caller's — or it is the caller's and
  you assert it. Decide, then document the decision in NOTES.md.

## What to test
- Exhaust the pool, then confirm the next alloc returns NULL rather than misbehaving.
- Free everything and confirm `pool_available` returns to the initial count.
- Alloc, free, alloc — the reused block should be usable and not corrupt the list.
- All returned pointers are correctly aligned and inside the backing array.
- Double free is detected (v3 onward).
- Freeing a pointer that didn't come from this pool is detected.
- ASan must be clean when you write to the full extent of every returned block.

## Interview questions this lets you answer from experience
Stack vs. heap in constrained memory · why malloc is avoided in firmware · fragmentation ·
alignment requirements · write your own malloc/free · what happens when allocation fails and
why returning NULL is not a plan by itself.
