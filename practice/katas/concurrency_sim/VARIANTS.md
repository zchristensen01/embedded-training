# concurrency_sim — variants

v1  Bounded blocking queue with a mutex and condition variables. Single producer, single
    consumer.
v2  Same, multiple producers and consumers. Run under ThreadSanitizer.
v3  Build a priority inversion with three threads and measure it. No fix yet.
v4  Fix v3 with priority inheritance. Assert on the measured difference in wait time.
v5  Build a deadlock, then break it with lock ordering.
v6  The racing counter: unsynchronised, then volatile-only (still wrong), then atomic, then
    mutex. Four implementations, one test file, NOTES.md explains why two of them fail.
v7  Bare-metal critical section: nestable interrupt disable/restore that is correct when nested.
    No pthreads; simulate with a global interrupt-enable flag.
