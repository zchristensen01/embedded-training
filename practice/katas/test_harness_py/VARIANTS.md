# test_harness_py — variants

v1  20 pytest tests over a pure function. Structure, naming, assertions, exit codes.
v2  Collapse duplicated tests into parametrize. Fixtures with correct scope.
v3  Device abstraction over a FakeTransport. Teardown that runs on failure.
v4  Real serial: pyserial, timeouts, framing, port discovery by USB serial number.
v5  Fault injection: truncated frames, bad CRC, impossible length. Assert recovery.
v6  Flash-and-verify: script the flash step, wait for boot, assert the version string.
v7  CI: JUnit XML output, GitHub Actions workflow, self-hosted runner notes, Docker with device
    passthrough.
