# rollover_timer — variants

v1  A `volatile uint32_t` tick counter, `now_ms`, and `timer_expired` written with the correct
    signed-difference comparison. One-shot timers only, in a fixed array.
v2  Periodic timers with `deadline += period`, so a late poll doesn't shift the phase. Prove
    the no-drift property in a test that deliberately polls late.
v3  Full superloop scheduler: `scheduler_run` walks the table and dispatches callbacks with a
    `void *ctx`. Decide whether a callback may start or cancel a timer, and enforce it.
v4  Deliberately break it. Write the naive `now >= deadline` version, then write the test that
    catches it near the wrap. Keep both in NOTES.md — this is the interview story.
v5  16-bit counter. Same logic on `uint16_t`, which wraps every 65 seconds instead of every
    49.7 days, so the failure is reachable in a test in real time.
v6  Sorted deadlines: keep the next-to-fire timer at the head so `scheduler_run` inspects one
    entry instead of all of them. State the insertion cost you traded for it.
v7  ISR-safe start and cancel: the tick ISR may fire in the middle of `timer_start`. Make it
    correct with a critical section, and say exactly which lines needed protecting and why.
