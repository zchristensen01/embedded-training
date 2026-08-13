# Kata 11 — test_harness_py

> **Before your first rep you owe this module its test suite** in `tests/`, in pytest,
> written by you. It is the one module with no build session — week 7's main block is five
> days of pytest from zero and this kata is the artifact those days produce. `make drill`
> refuses a module whose tests do not exist. Frozen once written: you do not edit it during
> a rep, only your `src/`, which is deleted each time. See
> [DAILY.md](../../../DAILY.md#build-sessions).

## What it is
The test & integration kata. A pytest-based harness that drives a device under test, first
against a simulated device, then against real hardware over serial.

## Why this is the wedge
A representative embedded test-automation posting asks for Python and Bash test development,
pytest, CI/CD, and hardware-in-the-loop testing with custom test rigs. The framework and CI
half of that transfers from backend work; the raw-Python half does not, which is what the
**Y** group and the three `*_py` katas exist to fix. This kata plus the week 8 harness is the
hardware half — the one that cannot be claimed without having built it.

It is a kata rather than only a project because the *structure* — fixture, device abstraction,
parametrised cases, deterministic teardown — is a pattern you should be able to reproduce cold
in an interview, and because take-homes in this track are commonly scripting exercises.

## The API you implement
```python
class Device:
    def __init__(self, transport): ...
    def send(self, cmd: bytes) -> None: ...
    def read_response(self, timeout: float = 1.0) -> bytes: ...
    def reset(self) -> None: ...

class FakeTransport:   # for v1-v3, no hardware needed
    ...
class SerialTransport: # for v4+
    ...
```

## How to think about it
- Build against a fake first. A harness you can only run with hardware attached is a harness you
  can't develop on a plane, and can't run in CI without a self-hosted runner.
- The fake is not a shortcut, it's the design forcing function: if your tests can run against
  both a fake and real hardware unchanged, your abstraction is right.
- Determinism is the whole game. Reset between tests. Never sleep when you can wait on a
  condition. Never share state across tests.
- Every test should be answerable to "which requirement does this verify?" Put the requirement
  ID in the test name or a marker. That is traceability, and it is what the medical and space
  interviewers are listening for.

## What to test (yes, test your tests)
- The fake device: does it actually model the failure modes you claim?
- Timeout handling: a device that never responds must fail the test in bounded time, not hang.
- Teardown runs even when the test body raises.
- Parametrised cases produce distinct, readable test IDs.
- Exit codes and JUnit XML are correct so CI can consume them.

## Interview questions this lets you answer from experience
How would you test this device · test plan structure · verification vs. validation ·
traceability · what makes a test flaky and how you fixed it · when would you not automate ·
walk me through your CI pipeline · how do you isolate tests that share one piece of hardware.
