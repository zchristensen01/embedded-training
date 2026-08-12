# Project · mimic-hil

The Week 8 flagship. Its own public repo (`~/embedded/mimic-hil`), not a folder in here — this
BRIEF is the spec, the repo is the artifact.

**Owns capabilities T16–T21.** Those are the six items in `plan/INTERVIEW_REQUIREMENTS.md` that no
kata and no deck card can produce, because they only exist as a working system.

---

## What it is

A Python program on your PC that tests the Mimic Stage 0 firmware automatically.

1. Flashes firmware to the board.
2. Talks to it over USB serial — sends commands, reads telemetry back.
3. Asserts pass/fail against Stage 0's real requirements.
4. Injects faults on purpose and checks the board recovers.
5. Runs on every `git push` via GitHub Actions with your PC as a self-hosted runner.

## Why it's the flagship

Kepler Communications' embedded test automation posting asks for Python and Bash test
development, pytest, GitLab CI/CD, and hardware-in-the-loop testing with custom test rigs. You
already have four of those five from backend work. This is the fifth, and it converts a web
resume into an embedded credential.

It also collapses two portfolio pieces into one story: **you wrote the firmware, then you built
the rig that regression-tests it on every commit.**

---

## Acceptance criteria

Each maps to a capability. The project is done when all six are true and demonstrable.

| # | Criterion | Capability | Evidence |
|---|---|---|---|
| 1 | The same test suite passes against a `FakeTransport` and a `SerialTransport`, unchanged | T16 | Both runs green |
| 2 | Port discovery is by USB serial number, not `/dev/ttyUSB0` enumeration order | T17 | Works with two boards plugged in |
| 3 | Timeouts are bounded — an unresponsive board fails the test, never hangs the suite | T17 | Test with the board unplugged |
| 4 | Fault injection: truncated frame, bad CRC, impossible length field. Board recovers each time | T18 | Three passing negative tests |
| 5 | `git push` triggers a CI run that flashes real hardware and reports pass/fail | T19 | **Screenshot of a green run** |
| 6 | Every test names the Stage 0 requirement it verifies | T21 | Requirement IDs in test names or markers |
| 7 | Bash script handles device wrangling — find, reset, unlock the port | T20 | In the repo |

Criterion 5's screenshot is the single most useful image in your whole portfolio. It goes in the
README, on your site, and in outreach messages.

---

## Structure

```
mimic-hil/
├── README.md               what it verifies, what it CANNOT catch, how to run it
├── harness/
│   ├── device.py           Device: send, read_response, reset
│   ├── transport.py        FakeTransport and SerialTransport behind one interface
│   └── discovery.py        find the board by USB serial number
├── tests/
│   ├── conftest.py         fixtures: open the port, reset between tests, teardown on failure
│   ├── test_smoke.py       boots, reports version
│   ├── test_control.py     holds position, returns after disturbance
│   ├── test_limits.py      soft limits, velocity limiting  [REQ-SAFE-1, REQ-SAFE-2]
│   ├── test_timeout.py     command timeout latches         [REQ-SAFE-3]
│   └── test_faults.py      truncated, bad CRC, bad length
├── scripts/
│   └── find-board.sh
└── .github/workflows/hil.yml
```

## Build order — Week 8

Build against the fake first. A harness you can only run with hardware attached can't be
developed on a train and can't be reasoned about when the board misbehaves. The fake is the
design forcing function: if the same tests pass on both transports, your abstraction is right.

| Day | Build |
|---|---|
| Mon | `transport.py` + `device.py`. Talk to the board manually first, in a REPL |
| Tue | `conftest.py`: fixture opens/closes the port, resets between tests, teardown survives failure |
| Wed | Flash-and-verify. Test isolation — prove one test can't affect the next |
| Thu | `test_faults.py`. Truncated, bad CRC, impossible length. Assert recovery, not just rejection |
| Fri | Requirement IDs. Go back through Stage 0's exit gate and map each test to a criterion |
| Sat | Dockerise. Self-hosted runner. Green run, screenshot |

## The AI rule, restated because it matters most here

AI may write the GitHub Actions YAML, the Dockerfile, and the Bash plumbing. **AI may not write a
single test case.** "How would you test this" is a top-three interview question, this project is
your answer to it, and the tests are the answer. Write them yourself.

## What to say about it

Rehearse under B3 and B4. The strongest version names what it **cannot** catch — mechanical wear,
thermal drift over hours, anything needing human judgement — because a candidate who knows the
limits of their own test coverage sounds like an engineer, and one who claims full coverage
sounds like they've never shipped.
