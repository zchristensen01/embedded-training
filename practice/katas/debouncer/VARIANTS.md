# debouncer — variants

v1  Counter. Consecutive agreeing samples; any disagreement resets the count to zero. Accept
    the change at the threshold and emit an edge event, not a level.
v2  Integrator. The counter climbs toward a ceiling while the input is high and falls toward
    zero while it's low, flipping only at the extremes. Tolerates a single spurious sample,
    and gives you hysteresis for free.
v3  Shift register. `history = (history << 1) | raw`, then test the byte against `0xFF` and
    `0x00`. Eight samples of debouncing in two lines and one byte of state.
v4  Asymmetric thresholds: press must be confirmed faster than release, or the reverse. Two
    thresholds, one state machine.
v5  Eight channels in one `uint8_t`-wide struct, updated in a single call with bitwise
    operations across all channels at once — no per-channel loop.
v6  Time-based rather than sample-based: `debounce_update(d, raw, now_ms, &out)`. The caller
    is no longer required to sample at a fixed rate, which is what actually happens in a
    superloop.
v7  Pack the entire state into a single `uint8_t` and state the RAM cost in a header comment.
