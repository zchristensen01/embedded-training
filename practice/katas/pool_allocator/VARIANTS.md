# pool_allocator — variants

v1  Fixed block size, free list threaded through free blocks, no error checking.
v2  Add alignment correctness for the worst-case type and a static assert on block size.
v3  Add double-free and foreign-pointer detection.
v4  Bump allocator: allocation only, no free. State in NOTES when this is the right answer.
v5  Two pools of different block sizes behind one facade that routes by requested size.
v6  Thread-safe / ISR-safe: protect the free list with a critical section.
v7  Instrumented: high-water mark tracking and a leak report at shutdown. This one doubles as
    test-infrastructure practice.
v8  Aligned allocation. `pool_aligned_alloc(size, align)` for any power-of-two alignment, over
    the same raw byte pool: over-allocate, round the pointer up with a mask, and stash the
    original base immediately below the pointer you return so `free` can recover it. Assert the
    alignment is a power of two. Use a mask, not a modulo, and say why in a comment.
