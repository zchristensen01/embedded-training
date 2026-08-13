# (c) Design and "explain your design" prompts

These are repeatable because the **subject rotates** and the **rubric is fixed**. Your score
across 60 different subjects measures one skill.

Run with `make prompt`. Ten minutes, written, then score yourself. Speak the answer aloud too —
this question is always verbal in the real thing.

---

## Rubric — never changes

> **This is the *testing* rubric, out of 16.** There is a second 16-point rubric in
> [`ARCHITECTURE.md`](ARCHITECTURE.md) for `make design`, which scores a different exercise on
> different axes. Same denominator so one parser reads both; not the same rubric. If you are
> being asked to *invent* the thing rather than test it, you want that one.

Score 0, 1, or 2 on each. 16 possible. Log the score in `logs/design-prompts/`.

| # | Criterion | 2 points looks like |
|---|---|---|
| 1 | Asked for requirements first | You explicitly asked what the spec says before proposing anything |
| 2 | Functional / happy path | Core function verified against stated requirements |
| 3 | Boundary conditions | Tested at the limits of the working range, both ends |
| 4 | Negative and out-of-range | Tested outside the range to prove failures aren't catastrophic |
| 5 | Environmental | Thermal cycling, vibration, humidity, EMI, altitude, immersion — whichever apply |
| 6 | Electrical and power | Brownout, over-voltage, inrush, ESD, reverse polarity, current draw |
| 7 | Reliability and life | Duty cycles to end of life, wear-out modes, MTBF thinking |
| 8 | Safety, usability, and misuse | What happens when a user does it wrong; human factors; failure is safe |

**Two automatic failures regardless of score:**
- Proposing solutions before asking for requirements.
- Stopping. Keep enumerating until the interviewer stops you. A candidate who listed the
  categories but never went deep on concrete tests was told they wanted more on testing ability.

**Bonus point:** naming how you'd *automate* the ones worth automating, and which you wouldn't.

---

## Subjects — draw at random

Everyday objects (the classic warm-up form):
1. A toaster
2. A vending machine
3. A pen
4. An elevator
5. A kettle
6. A door lock
7. A microwave
8. A bicycle brake
9. A fire extinguisher
10. An ATM

Instruments and tools:
11. A torque wrench
12. A digital multimeter
13. A bench power supply
14. A logic analyzer
15. A 3D printer
16. A barcode scanner

Space and satellite:
17. A satellite reaction wheel
18. A deployable solar array hinge
19. A CubeSat radio downlink
20. A star tracker
21. A propellant valve
22. A battery pack for orbit
23. A separation mechanism

Subsea and marine:
24. An ROV thruster
25. A pressure housing at 3000 m
26. A subsea connector mating cycle
27. A sonar transducer
28. An underwater camera and light
29. A buoyancy control system

Medical devices and imaging:
30. An infusion pump
31. A pulse oximeter
32. An MRI patient table
33. A surgical stapler
34. A defibrillator
35. A patient monitor alarm
36. A powered exoskeleton joint
37. A prosthetic knee

Robotics:
38. A robot arm joint encoder
39. An emergency stop circuit
40. A LiDAR-based obstacle stop

**Embedded subsystems.** Subjects 1–40 are objects you can hold — deliberately, because the
question is asked about consumer products as often as about instruments, and an object with no
datasheet forces you to ask for requirements. These twenty are the other half: subsystems inside
the devices these employers actually build, drawn from the second research pass. They are harder,
they assume the vocabulary the first forty teach, and they are where the medical, space and
robotics interviewers live. Rotate into them once you are scoring 12+ consistently on the first
forty.

41. An implantable pacemaker telemetry uplink over BLE
42. A surgical robot instrument force-feedback sensor channel
43. An insulin pump occlusion-detection subsystem
44. A UAV flight controller IMU sampling path
45. A satellite reaction wheel motor-control loop
46. A CubeSat watchdog and safe-mode controller
47. A brake-by-wire CAN node
48. An EV battery management system cell-balancing controller
49. A coulomb-counting battery fuel gauge
50. A keypad matrix scanner
51. An eight-channel analog-mux acquisition front end
52. A BLE smart bulb with over-the-air update
53. A smart door lock with signed firmware update
54. An always-on wearable accelerometer sampler
55. A subsea ROV tether serial link
56. A firmware over-the-air update subsystem with A/B partitions and rollback
57. A ventilator flow sensor and alarm path
58. A radiation-tolerant memory scrubber for a satellite payload
59. A cryogenic tank level sensor
60. A robot joint brake release interlock

---

## "Explain your design" prompts

Different skill: defending decisions on something you built. Rehearse three of these per session
in Week 8, out loud, recorded.

1. Walk me through your ring buffer. Why that full/empty scheme and not the other one?
2. Why a power-of-two size? What did that buy you and what did it cost?
3. How did you make your UART driver safe against the ISR? What could still go wrong?
4. Why a table-driven state machine here instead of a switch?
5. Your HIL harness — what does it actually verify, and what can it not catch?
6. How does each test in your harness trace to a firmware requirement?
7. What's the flakiest part of your test setup and what did you do about it?
8. Show me a bug this caught that you would have missed by hand.
9. What would you do differently if this had to run for five years unattended?
10. If I gave you one more week on this project, what would you spend it on and why?

**Structure every answer as:** what the constraint was → what options you considered → what you
chose → what you gave up. Candidates who only say what they built sound like they followed a
tutorial. Candidates who name the trade-off sound like engineers.
