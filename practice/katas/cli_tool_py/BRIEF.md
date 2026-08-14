# Kata 15 — cli_tool_py

**In one sentence.** The tool that sits between you and the bench: find the right device,
talk to it, report what happened, and exit with a code CI can read.

---

> **Before your first rep you owe this module its test suite** in `tests/`, in pytest,
> written by you. `make drill` refuses a module whose tests do not exist. Frozen once
> written: you do not edit it during a rep, only your `src/`, which is deleted each time.
> See [DAILY.md](../../../DAILY.md#build-sessions).

## The problem, in plain language

You have two identical boards plugged into the same machine. One is the device under test;
the other is a reference unit. Your script needs the right one.

```
   /dev/ttyUSB0  ──▶  which board is this?
   /dev/ttyUSB1  ──▶  and this?

   The numbers are assigned in the order the kernel enumerated them.
   Reboot, or unplug and replug, and they can swap.
   There is nothing in the name that identifies the hardware.
```

Take `ports[0]` and your test suite works all afternoon and then, after someone bumps a USB
cable, flashes the wrong board — or worse, passes a test against the reference unit and
reports the device under test as good.

The fix is that every USB device carries a **serial number** in its descriptor, burned in at
manufacture and stable forever. `pyserial`'s `list_ports.comports()` gives you that, and you
match on it:

```
   port          vid:pid     serial_number
   ─────────     ────────    ─────────────
   /dev/ttyUSB0  0403:6001   AB0KX3QT      ◀── the one you want, wherever it lands
   /dev/ttyUSB1  0403:6001   AB0KX4RM
```

**Never select by index. Match on the serial number and fail loudly when it is absent.**
This is exercise 11 in the [T&I question bank](../../../reference/question-bank/test-integration.md)
and it is a real problem the moment there are two boards.

### The one genuinely interesting question

**What does a decorator actually do, and what do people forget?**

A decorator is a function that takes a function and returns a replacement. `@retry(times=3)`
means "wrap this function in retry logic". A decorator *factory* — one that takes arguments —
is three nested functions, and writing that shape from memory is a live interview question at
Qualcomm:

```python
   def retry(times=3, delay=0.1):        # 1. takes the ARGUMENTS
       def decorator(func):              # 2. takes the FUNCTION
           def wrapper(*args, **kwargs): # 3. takes the CALL's arguments
               ...
           return wrapper
       return decorator
```

Read it from the call site outward: `retry(times=3)` runs first and returns `decorator`;
`decorator(read_sensor)` runs next and returns `wrapper`; `wrapper` is what gets called
forever after. Three functions, three sets of arguments, one per layer.

**The line everyone forgets** is `@functools.wraps(func)` on the wrapper. Without it, the
replacement function has its own identity:

```python
   read_sensor.__name__   # 'wrapper'   ← without functools.wraps
   read_sensor.__name__   # 'read_sensor' ← with it
```

That is not cosmetic. pytest discovers tests by name, logs print function names, and
tracebacks name the frame — so a whole suite of decorated tests all report as `wrapper` and
you cannot tell from a CI log which one failed. Naming this trap unprompted is a strong
signal.

**And the second trap: never swallow the final exception.** Three silent retries against a
dead device, followed by returning `None` as though it worked, is a *false green* — the worst
possible outcome for a test harness, because it reports success for hardware that is
broken. Re-raise the last exception. And re-raise the **original type**, not a generic one,
so the caller can still tell a timeout from a protocol error.

---

## Why firmware test needs this

Every harness has one of these and it is the first thing you write on a new rig. It is also
the glue that everything else in the T&I track hangs off: `binary_frame_py` decodes what
comes back, `test_harness_py` drives it from pytest, and the weeks 10–11 HIL project is this
grown up.

The three skills in it — device discovery, retry semantics, and exit codes — are each
separately interview-relevant, which is unusual for one 22-minute kata.

---

## What you need from Python

```python
import argparse, functools
from serial.tools import list_ports
```

**`argparse` with subcommands** is the standard shape for a tool that does more than one
thing:

```python
   p = argparse.ArgumentParser()
   sub = p.add_subparsers(dest='cmd', required=True)
   sub.add_parser('list')
   ping = sub.add_parser('ping'); ping.add_argument('--serial', required=True)
```

That gives you `tool list` and `tool ping --serial AB0KX3QT`, plus `--help` and usage errors
for free. **`argparse` exits with code 2 on a usage error by default** — which is why the API
below reserves 2 for exactly that, rather than fighting it.

**`*args, **kwargs`** is "whatever positional arguments there were, and whatever keyword
arguments there were." A wrapper uses it to pass a call through untouched without knowing
anything about the function it wraps. `args` is a tuple; `kwargs` is a dict.

**Exceptions, not sentinel returns.** `find_port` raising `DeviceNotFound` rather than
returning `None` means a caller who forgets to check gets a loud traceback instead of
`AttributeError: 'NoneType'` somewhere unrelated.

---

## The API you are writing

```python
def find_port(serial_number: str) -> str:
    """USB serial number -> device node. Raise DeviceNotFound, never guess."""

def retry(times: int = 3, delay: float = 0.1):
    """Decorator factory. Re-raise the last exception on final failure."""

def main(argv: list[str]) -> int:
    """argparse subcommands: list, ping --serial SN. 0 ok, 1 device error, 2 usage."""
```

- **`find_port` raises rather than falling back.** "Couldn't find AB0KX3QT, so I used the
  first port" is how you flash the wrong board.
- **`retry` is a factory**, so it is used as `@retry(times=3)` with parentheses — three
  layers, as above.
- **`main` takes `argv`** rather than reading `sys.argv`, for the same reason as
  `log_parser_py`: your tests call it directly with a list, no subprocess, no mocking of
  `sys`. The real entry point is a two-line `if __name__ == '__main__':` that passes
  `sys.argv[1:]` and calls `sys.exit()`.

**Three exit codes, three different readers:**

```
   0  →  it worked                          CI proceeds
   1  →  the DEVICE said no or is absent    a hardware or firmware person looks
   2  →  YOU typed it wrong                 the caller fixes their command
```

CI branches on that distinction. Collapsing 1 and 2 into "nonzero" means a typo in a
pipeline definition looks identical to a failing board.

**Test it without hardware.** The port enumeration is one function call, so fake it — your
tests supply a fabricated list of ports and never touch a USB stack. A tool you can only test
at the bench is a tool you cannot put in CI, and this kata is drilled long before you have a
board.

---

## How to think about it

Don't write code yet. Answer these on paper:

1. Write the three-layer decorator skeleton from memory — just the `def` lines and the
   `return`s, no bodies. Do it until it is automatic; that is the interview question.
2. Where does `@functools.wraps` go, and what exactly breaks without it?
3. `retry(times=3)` where the call fails all three times — what does the caller see? What
   about `times=1`? What about `times=0`? (Decide what `0` means and write it down.)
4. How does `find_port` distinguish "no such serial number" from "no ports at all"? Should
   they be the same error?
5. Which exit code does `ping --serial NOPE` produce, and why is it not 2?

Then write it. It is about 60 lines, and `retry` is a third of them.

---

## Tests it must pass

| Test | What it's protecting against |
|---|---|
| Two devices attached, the right one selected — **with the enumeration order reversed** | The `ports[0]` bug. Reversing the fake list is the whole test |
| The named serial number absent: raises, does not fall back to the first port | Silent wrong-board selection |
| `retry` succeeds on attempt 3 | That it retries at all, and stops when it works |
| `retry` exhausts and re-raises the **original exception type** | The false green, and generic-exception laundering |
| The decorated function keeps its `__name__` and `__doc__` | The missing `functools.wraps` |
| Each exit code, driven from `main(argv)` directly — no subprocess | That the codes are what you think, and that the tool is testable at all |
| `--help` exits 0; an unknown subcommand exits 2 | argparse's own conventions, which you should not fight |

Note what is *not* here: no test opens a serial port. Every one of these runs on a laptop on
a train, which is the property that lets this kata be drilled from week 6.

---

## Once it's boring

*Boring* means: blank file to working, tests green first run, in under twenty-two minutes,
never unsure what to type next. Then add a constraint.

**Second pass — exponential backoff with a cap.** `delay` doubles each attempt up to a
maximum. Then work out why a fixed retry interval is actively harmful when several test jobs
retry against the same busy rig at once — they synchronise — and add jitter. That reasoning is
the answer to "how do you deal with a flaky hardware CI job", and the first half of the
answer is that a blanket auto-retry is the *wrong* first move.

**Third pass — structured output.** Add `--json` so the tool emits a machine-readable result
alongside its exit code, and make the human output go to stderr so stdout stays parseable.
That separation is what lets a shell pipeline consume your tool, and it is a small thing that
reads as experience.

---

> **Variants:** seven, `v1` through `v7`, written up in [VARIANTS.md](VARIANTS.md).
> `make drill` picks one and `make done` logs the rep to
> [logs/log.tsv](../../../logs/log.tsv). Time is only comparable within a variant.

## Interview questions this lets you answer from experience

How do you find the right board when two are plugged in · write a retry decorator · what does
`functools.wraps` do · how does your harness report to CI · how would you test a CLI · why is
a blanket auto-retry the wrong first move on a flaky hardware job.
