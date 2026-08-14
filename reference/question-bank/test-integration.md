# Test & integration

The shape of this interview is different from embedded. Less language trivia, more structured
thinking, more process, and a resume walkthrough that *is* the technical screen. Behavioural
rounds reject more candidates here than technical ones do.

---

## (a) Coding exercises — kata `test_harness_py`

1. Write 20 pytest tests for a pure function. Get the naming and structure right first.
2. Convert 10 near-identical tests into one `@pytest.mark.parametrize`.
3. Write a fixture that opens a serial port and closes it even when the test fails.
4. Fixture scopes: function, module, session. Pick correctly for a device that takes 3 seconds
   to reset.
5. Write a device abstraction class: `send(cmd)`, `read_response(timeout)`, `reset()`. Test the
   harness itself against a fake device before you ever touch hardware.
6. Parse a telemetry log and assert no value left its valid range for more than 100 ms.
7. Write a test that flashes firmware, waits for boot, and asserts the version string.
8. Fault injection: send a truncated frame, a bad CRC, and a frame with an impossible length
   field. Assert the device recovers.
9. Make the suite return a correct exit code and a JUnit XML report for CI.
10. Write a GitHub Actions workflow that runs the suite on a self-hosted runner with hardware
    attached.
11. Bash: a script that finds the right `/dev/ttyUSB*` by USB serial number rather than
    enumeration order. This is a real problem the moment you have two boards.
12. Dockerise the harness, and state what you had to do about device passthrough.

---

## (b) Conceptual and verbal

**Q: Verification versus validation.**
Strong: verification asks "did we build the product right" — does it meet the written
requirements. Validation asks "did we build the right product" — does it meet the user's need
and intended use. Bench protocol execution is verification; simulated-use testing with a
clinician is validation.
Trap: **using them interchangeably.** This is the flagged failing answer in medical V&V.

**Q: Why does traceability matter?**
Strong: every test case traces backward to a requirement and forward to a risk or hazard from
the FMEA. It proves coverage is complete rather than assumed, and it's what an auditor asks for
first. Under FDA 21 CFR Part 820, ISO 13485 and IEC 62304 it isn't optional.
Trap: describing tests as a list someone wrote from experience.

**Q: IEC 62304 software safety classes.**
Strong: Class A — no injury possible. Class B — injury possible but not serious. Class C — death
or serious injury possible. If the manufacturer performs no classification, software defaults to
Class C. Higher class drives more verification rigour and documentation.

**Q: Walk me through the test lifecycle.**
Strong: requirements → test strategy → test plan → test cases traceable to requirements →
execution → defect logging and triage → report and coverage assessment.

**Q: A change request lands mid-project. What happens?**
Strong: impact analysis first — which requirements move, which test cases are invalidated, what
regression scope that implies, and what it costs in schedule. Then update traceability. Then
re-run.
Trap: "we just retest the changed part."

**Q: What is regression testing and how do you scope it?**
Strong: re-running existing tests to confirm a change broke nothing. Scope by impact analysis
and by risk, not by running everything, unless it's automated and cheap — which is the argument
for the HIL harness.

**Q: Smoke, sanity, regression, acceptance — distinguish them.**
Strong: smoke is a fast go/no-go on a new build; sanity is a narrow check on a specific fix;
regression is broad re-verification; acceptance is against the customer's or user's criteria.

**Q: How do you write a good defect report?**
Strong: exact build and hardware revision, environment, steps to reproduce, expected versus
actual, frequency (always, or 1 in 20), logs and captures attached, and a severity separate from
a priority.

**Q: Some customer sites fail and others don't. Find it.**
Strong: characterise the difference — firmware version, hardware revision, power quality,
temperature, cabling, configuration, usage pattern. Form hypotheses, then test one variable at a
time. Get data from the field before theorising. Structured RCA — 5 Whys or a fishbone — and
confirm the fix by reproducing the failure and then removing it.
Trap: guessing at causes without isolating what differs.

**Q: What's the difference between a test fixture, a test harness, and a HIL rig?**
Strong: a fixture holds and connects the unit under test; a harness is the software that drives
tests and reports results; a HIL rig closes the loop by simulating the rest of the system —
sensors, actuators, or the vehicle — so the real firmware runs against a simulated world.

**Q: How do you keep tests from being flaky?**
Strong: deterministic setup and teardown, reset the device between tests, no shared mutable
state, explicit waits on conditions rather than sleeps, and quarantine plus fix rather than
retry-until-green.

**Q: When would you not automate a test?**
Strong: when it runs once, when the setup cost exceeds the lifetime saving, when it needs human
judgement (usability, feel, audible or visual defects), or when the interface is changing weekly.

---

## Behavioural — often the deciding round

Write these out in STAR form in week 12. Real examples reported from these interviews:

1. A time you struggled with a problem and how you got through it.
2. A time you had a conflict with a coworker.
3. A time you pushed back on skipping a test.
4. Tell me about a project you took to completion.
5. A time you found a defect late and what you did.
6. A time you were wrong about a root cause.
7. Why hardware, coming from web? *(Have this one polished. It's the objection in their head.)*
8. Why this domain — space, subsea, medical — specifically?

---

## Process notes worth knowing before you interview

- Expect 3–5 rounds and 3 weeks to 2 months end to end. Kraken Robotics reportedly runs an HR
  pre-screen, a behavioural round, then a **6-hour take-home** with a technical writing portion
  and a programming/design portion, then a follow-up on the assessment.
- Intuitive Surgical reportedly runs recruiter → hiring manager project walkthrough → senior
  engineer walkthrough → analysis challenge → panel, with coding in C# and Python.
- Stryker reportedly runs around six rounds including a Gallup strengths interview that is a
  separate filter from technical merit.
- Rocket Lab candidates report a 45-minute virtual panel plus a 10-minute project presentation,
  focused on technical contribution rather than algorithm questions.
- The resume walkthrough is the technical screen. Rehearse how you tested each project, not just
  what it did.
