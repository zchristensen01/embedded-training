# log_parser_py — variants

v1  CSV telemetry, one channel. Report min, max and mean of `PRESSURE` in one streaming pass.
    Exit 0. The point is the loop and the exit code, nothing else.
v2  Range violations with a dwell window: report every timestamp where the channel left
    0–100 for more than 100 ms. Carry the excursion start across lines. Exit 1 if any.
v3  Malformed input: the same as v2 against a log with a truncated last line, a blank line,
    and a row with a missing field. Skip and count them; exit 2 if more than 1% are bad.
v4  Many channels, one pass. Per-channel limits from a config dict. Do not read the file
    once per channel — state in a header comment what that would have cost.
v5  Prove the memory property. Same output, but the test feeds a generator of a million rows
    and asserts completion. Any implementation that materialises the input fails.
v6  Two logs, one question: correlate a device log and a host log on timestamp and report the
    largest clock skew. Streaming merge, not two lists.
v7  Report as an artifact: emit a summary table and a JUnit XML file CI can consume, with the
    firmware build hash carried through from the log header into the report. Maps onto T21.
