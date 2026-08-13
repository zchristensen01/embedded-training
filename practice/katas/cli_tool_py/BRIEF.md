# Kata 15 — cli_tool_py

> **Before your first rep you owe this module its test suite** in `tests/`, in pytest,
> written by you. `make drill` refuses a module whose tests do not exist. Frozen once
> written: you do not edit it during a rep, only your `src/`, which is deleted each time.
> See [DAILY.md](../../../DAILY.md#build-sessions).

## What it is
The tool that sits between you and the bench: find the device, talk to it, report what
happened, exit with a code CI can read.

## Why firmware test needs it
Every harness has one of these and it is the first thing you write on a new rig. The specific
problem it solves — **selecting a board by USB serial number rather than by enumeration
order** — is a real problem the moment two boards are attached, and `/dev/ttyUSB0` is not
stable across reboots or hotplug. It is exercise 11 in the T&I question bank for that reason.

It also carries the decorator work. Writing `@retry(times=3)` correctly, with
`functools.wraps` so pytest discovery and your logs still report the right function name, was
confirmed as a live question at Qualcomm.

## The API you implement
```python
def find_port(serial_number: str) -> str:
    """USB serial number -> device node. Raise DeviceNotFound, never guess."""

def retry(times: int = 3, delay: float = 0.1):
    """Decorator factory. Re-raise the last exception on final failure."""

def main(argv: list[str]) -> int:
    """argparse subcommands: list, ping --serial SN. 0 ok, 1 device error, 2 usage."""
```

## How to think about it
- **Never select by index.** `ports[0]` works on your desk and grabs the wrong board in the
  rack. Match on the serial number and fail loudly when it is absent.
- **A decorator factory is three nested functions.** Write the shape before the logic, and put
  `@functools.wraps(func)` on the wrapper — without it every decorated function reports as
  `wrapper` and you cannot tell from a log which test actually ran.
- **Swallowing the final exception is worse than failing.** Three silent retries against a
  dead device that then reports success is a false green.
- **Exit codes distinguish "device said no" from "you typed it wrong."** CI branches on that.
- **Test it without hardware.** Fake the port enumeration. A tool you can only test at the
  bench is a tool you cannot put in CI.

## What to test
- Two devices attached, the right one selected — with the enumeration order reversed.
- The named serial number absent: raises, does not fall back to the first port.
- `retry` succeeds on attempt 3; `retry` exhausts and re-raises the *original* exception type.
- The decorated function keeps its `__name__` and `__doc__`.
- Each exit code, driven from `main(argv)` directly — no subprocess needed.
- `--help` exits 0; an unknown subcommand exits 2.

## Interview questions this lets you answer from experience
How do you find the right board when two are plugged in · write a retry decorator · what does
`functools.wraps` do · how does your harness report to CI · how would you test a CLI.
