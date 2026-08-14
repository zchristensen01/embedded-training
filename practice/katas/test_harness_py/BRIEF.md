# Kata 11 — test_harness_py

**In one sentence.** A pytest harness that drives a device under test — first against a
simulated device, then against real hardware over serial, with the same tests unchanged.

---

> **Before your first rep you owe this module its test suite** in `tests/`, in pytest,
> written by you. It is the one module with no build session — week 9's main block is five
> days on pytest itself and this kata is the artifact those days produce. `make drill`
> refuses a module whose tests do not exist. Frozen once written: you do not edit it during
> a rep, only your `src/`, which is deleted each time. See
> [DAILY.md](../../../DAILY.md#build-sessions).

## The problem, in plain language

You need to test a physical device automatically. The device is slow, occasionally absent,
sometimes wedged, and can only be talked to by one thing at a time — which is every property
that makes automated testing hard.

The structure that solves it is one idea: **put an interface between the tests and the
wire.**

```
                 ┌─────────────────────────┐
                 │      your tests         │   these never change
                 │  test_boots_and_reports │
                 │  test_rejects_bad_crc   │
                 └───────────┬─────────────┘
                             │
                 ┌───────────▼─────────────┐
                 │        Device           │   send / read_response / reset
                 │  (speaks the protocol)  │
                 └───────────┬─────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
    ┌─────────▼─────────┐        ┌──────────▼──────────┐
    │   FakeTransport   │        │  SerialTransport    │
    │  answers in RAM   │        │  answers over USB   │
    │  no hardware      │        │  real board         │
    └───────────────────┘        └─────────────────────┘
```

`Device` knows the protocol. The transports know how bytes get from here to there. Swap the
transport and the same test file runs on your laptop on a train or against the board on your
desk.

### The one genuinely interesting question

**Why build the fake first, when the real hardware is right there?**

Three reasons, and the third is the one that gets you hired:

1. **You can develop and run the suite anywhere** — a plane, CI, a machine with no board.
2. **You can inject faults the real device can't produce on demand.** Ask a real board to
   send you a truncated frame with a bad CRC. You can't. The fake does it on request, which
   is the only way to test your error paths at all.
3. **It is a design forcing function.** If the same tests pass against both transports
   unchanged, your abstraction is right. If you find yourself writing `if is_fake:` inside a
   test, it is wrong, and you have found that out in minute five instead of week three.

The fake is not a shortcut or a stand-in for the real thing. It is how you find out whether
your interface is any good.

### The second thing that separates this from a script: determinism

A test that passes 95% of the time is worse than one that always fails, because a team learns
to re-run it and stops reading it. Four rules, and they are all interview answers:

| Rule | Why |
|---|---|
| **Reset between every test** | Test A leaves the device in a mode; test B fails for no visible reason and passes when run alone |
| **Never share state across tests** | The same bug, one layer up. Tests must pass in any order |
| **Never `sleep()` when you can wait on a condition** | A fixed sleep is either too short (flaky) or too long (a slow suite). Poll for the thing you actually need, with a timeout |
| **Every timeout is bounded** | A device that never answers must *fail* the test, not hang the suite. An unbounded read is how a CI job runs for six hours |

"How do you keep tests from being flaky" is one of the most-asked T&I questions, and the
answer is this table rather than anything clever.

### The third thing: traceability

Every test should be answerable to *"which requirement does this verify?"* — in the test's
name, or a pytest marker:

```python
   @pytest.mark.requirement("REQ-SAFE-3")
   def test_command_timeout_latches_safe_state(): ...
```

That single habit is what medical and aerospace interviewers listen for, and it is nearly
free to do. It converts "we have 200 tests" — which proves nothing — into "every safety
requirement has a named test and here is the mapping", which is the actual deliverable in a
regulated shop.

---

## Why this is the wedge

A representative embedded test-automation posting asks for Python and Bash test development,
pytest, CI/CD, and hardware-in-the-loop testing with custom test rigs. The framework and CI
half of that transfers from backend work; the raw-Python half does not, which is what the
**Y** group and the other three `*_py` katas exist to fix. This kata plus the weeks 10–11
harness is the hardware half — the one that cannot be claimed without having built it.

It is a kata rather than only a project because the *structure* — fixture, device
abstraction, parametrised cases, deterministic teardown — is a pattern you should be able to
reproduce cold in an interview, and because take-homes in this track are commonly scripting
exercises.

---

## What you need from Python

```python
import pytest
```

**A fixture is setup and teardown as a value.** The test asks for it by parameter name and
pytest supplies it:

```python
   @pytest.fixture
   def device():
       d = Device(FakeTransport())
       d.reset()
       yield d              # the test runs here
       d.close()            # ALWAYS runs, even if the test raised
```

The `yield` is the whole point: everything after it is teardown, and it runs whether the test
passed, failed or exploded. That is stronger than putting cleanup at the end of the test
body, which is skipped on failure — exactly when you most need the port closed.

**Fixture scope decides how often setup runs**, and picking it is a real trade-off:

| Scope | Runs | Use when |
|---|---|---|
| `function` (default) | per test | the safe default — full isolation |
| `module` | once per file | setup is expensive |
| `session` | once per run | a device that takes 3 seconds to reset |

Wider scope is faster and leaks state between tests. That tension — isolation versus runtime
— is the question, and "session scope for the port, function scope for the reset" is usually
the right answer.

**`conftest.py`** is where fixtures shared by several test files live. pytest finds it
automatically by directory, with no import — which is worth knowing precisely because it
looks like magic the first time.

**`parametrize` turns ten near-identical tests into one:**

```python
   @pytest.mark.parametrize("cmd,expected", [
       (b'VER?', b'1.2.3'),
       (b'ID?',  b'MIMIC'),
   ])
   def test_query(device, cmd, expected): ...
```

Each case gets its own test ID and reports separately, so a failure names the case rather
than the loop. Writing a `for` loop inside one test instead is the wrong answer: the first
failure stops the loop and you learn nothing about the rest.

---

## The API you are writing

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

- **`Device` takes its transport as a constructor argument.** That one line is the entire
  abstraction — it is dependency injection, and it is what makes the fake possible. Hard-code
  `serial.Serial(...)` inside `Device` and you have written something untestable.
- **`read_response` has a timeout with a default**, and the default must be finite. This is
  the bounded-exit rule, in the signature.
- **`reset` is what gives you isolation.** Whether it is a control line, a command or a
  power cycle, the fixture calls it between tests.
- **`FakeTransport` must model failure, not just success.** A fake that only ever answers
  correctly tests nothing you were worried about. It should be able to produce, on request: a
  truncated frame, a bad CRC, an impossible length field, and silence.

---

## How to think about it

Don't write code yet. Answer these on paper:

1. List the fixtures you need and pick a scope for each. Justify every one that is not
   `function`.
2. What is the smallest interface `Device` needs from a transport? (Probably `write`, `read`
   and `close`. If it is more than four methods, you are leaking serial-port details upward.)
3. `read_response` is waiting and the device says nothing. Write the exact sequence: what is
   polled, how often, what is raised, and after how long.
4. Teardown runs while the device is mid-transmission. What must `close` cope with?
5. Which of your tests would still pass if the firmware were completely broken? Those are the
   ones that test your harness rather than the device — you want to know which they are.

Then write it. `v1`–`v3` is about 80 lines including the fake.

---

## Tests it must pass (yes, test your tests)

| Test | What it's protecting against |
|---|---|
| The fake device actually models the failure modes you claim | A fake that always succeeds, which makes every error-path test vacuous |
| A device that never responds fails the test in **bounded time**, not hangs | The six-hour CI job |
| Teardown runs even when the test body raises | Cleanup at the end of the body, which is skipped exactly when it matters |
| Tests pass in any order, and individually | Shared state between tests |
| Parametrised cases produce distinct, readable test IDs | A failure report that says `test_query[2]` and tells you nothing |
| Exit codes and JUnit XML are correct so CI can consume them | A suite CI cannot read is a suite CI ignores |
| The same test file passes against `FakeTransport` and `SerialTransport` unchanged | The abstraction. This is criterion 1 of the HIL project |

---

## Once it's boring

*Boring* means: blank file to working, tests green first run, in under twenty-five minutes,
never unsure what to type next. Then add a constraint.

**Second pass — a requirement marker and a traceability report.** Add
`@pytest.mark.requirement("REQ-...")` and a small `conftest.py` hook that prints, at the end
of a run, which requirements were covered and which were not. That report is a portfolio
artifact in its own right and directly answers "how do you know your testing is complete".

**Third pass — hardware resource locking.** Two CI jobs on one self-hosted runner both grab
`/dev/ttyUSB0` and both fail confusingly. Add a lock file so the second waits. Then work out
what happens when a job is killed while holding it — stale lock, suite wedged — and handle
that too. It is exactly the question in the deck's `ci` cards.

---

> **Variants:** seven, `v1` through `v7`, written up in [VARIANTS.md](VARIANTS.md).
> `make drill` picks one and `make done` logs the rep to
> [logs/log.tsv](../../../logs/log.tsv). Time is only comparable within a variant.

## Interview questions this lets you answer from experience

How would you test this device · test plan structure · verification vs validation ·
traceability · what makes a test flaky and how you fixed it · when would you not automate ·
walk me through your CI pipeline · how do you isolate tests that share one piece of hardware ·
what does a fixture give you over setup code in the test.
