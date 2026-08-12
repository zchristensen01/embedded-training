# fixed_point_pid — variants

v1  Q16.16 proportional, integral and derivative, with output saturation and anti-windup by
    clamping the integrator. No floating point anywhere at runtime.
v2  Derivative on measurement: `-(measured - prev_measured)` instead of `error - prev_error`,
    so a setpoint step no longer spikes the derivative term.
v3  Filtered derivative and an explicit `dt`. A first-order low-pass on the D term, and gains
    that carry real per-second units instead of per-iteration fudge factors.
v4  Back-calculation anti-windup: feed the saturation error back into the integrator instead
    of clamping it. Compare the recovery from a long saturation against v1.
v5  Q8.8 in 16 bits with a 32-bit intermediate. Same controller, half the width. Find the
    input that overflows it and write down the bound.
v6  Prove the arithmetic. Every intermediate product must be shown to fit, with the input
    ranges asserted by `_Static_assert` or checked in `pid_init`.
v7  Bumpless transfer: change gains or setpoint mid-run without a step in the output. Requires
    deciding what the integrator should hold at the moment of the change.
