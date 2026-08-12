# pool_allocator — variants

v1  Fixed block size, free list threaded through free blocks, no error checking.
v2  Add alignment correctness for the worst-case type and a static assert on block size.
v3  Add double-free and foreign-pointer detection.
v4  Bump allocator: allocation only, no free. State in NOTES when this is the right answer.
v5  Two pools of different block sizes behind one facade that routes by requested size.
v6  Thread-safe / ISR-safe: protect the free list with a critical section.
v7  Instrumented: high-water mark tracking and a leak report at shutdown. This one doubles as
    test-infrastructure practice.
