# cli_tool_py — variants

v1  `tool list` — enumerate serial ports and print node, USB serial number and description,
    one per line. Exit 0. Fake the enumeration in the tests; no hardware.
v2  `tool ping --serial SN` — resolve the node by USB serial number, open it, send `*IDN?`,
    print the reply. Exit 1 when the serial number is not present, 2 on usage error.
v3  The retry decorator: `@retry(times=3, delay=0.1)` on the read. Preserve `__name__` with
    `functools.wraps`, re-raise the last exception on exhaustion, and prove both in a test.
v4  Timeouts as a first-class concern: a device that never answers must fail in bounded time,
    not hang. Assert the bound in a test rather than trusting a sleep.
v5  Config file plus flags, with a stated precedence: flag beats env var beats config file
    beats default. Write the precedence in `--help` and test every level of it.
v6  Structured output: `--json` emits a machine-readable result alongside the human one, and
    the exit code still carries the verdict. A CI step consumes the JSON.
v7  Do it in Bash instead. `udevadm` or a `/sys` walk to map serial number to node, export it,
    fail loudly and non-zero when absent. Same contract, no Python — this is the T20 rep.
