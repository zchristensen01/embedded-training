# (d) Embedded system-design prompts

**Architect the thing. Do not test a thing that already exists — that is
[`SUBJECTS.md`](SUBJECTS.md), and it is a different exercise with a different rubric.**

Candidate reports place this as a dedicated round at Google and Meta Reality Labs, and as a
design item inside Tesla's and Medtronic's take-homes. It is graded on six axes: ISR/main
partitioning, memory budget, comms topology, power states, failure handling, and
testability. Two more axes gate it — asking for constraints before you draw, and holding
your position when the interviewer pushes.

Run with `make design`. 45 minutes, written, then said aloud. `make progress` scores **E30**
on three of these at 12+/16; the out-loud defence logs as a **B11** take.

It differs from a web system-design round in both scope and axis: one device or subsystem
rather than a distributed fleet, and RAM, flash, microamps, interrupt latency and peripheral
protocols rather than sharding and availability. Candidates report the round is sometimes
run by a hardware engineer, and sometimes degenerates into generic web system design — if
that happens, steer it back by asking what the power budget is.

---

## The shape of a good answer

1. **Ask first.** What is the power source? What is the update rate? What is the BOM cost?
   What must never happen? Candidates who start drawing lose axis 1 and often the round.
2. **Draw the partition.** What runs in the ISR, what runs in the main loop or a task, and
   what the queue between them looks like. Minimal ISR, every time.
3. **Put numbers on it.** RAM per buffer, flash for the image, milliamps per mode. "Some
   RAM" scores zero. An estimate you can defend scores two.
4. **Name the failure and the safe state.** What detects it, how long detection takes, and
   what the system does while it is broken.
5. **Say where you would cut it to test it.** The seam the fake goes at.
6. **Then argue against yourself**, out loud, and answer it.

---

## Prompts

1. Design a buffered stream: incoming data and periodic outgoing data, while an ISR operates on the buffer. Overflow policy, consistent snapshot, minimal ISR work.
2. Design a firmware logging and telemetry subsystem for an implantable device: limited flash, periodic upload to an external programmer over low-bandwidth BLE.
3. Design the firmware architecture for an always-on wearable sampling an accelerometer at 100 Hz, maximising battery life.
4. Design an arbitration scheme for two client devices talking to one host on a single I2C bus.
5. Design an I2C-like data stream end to end: hardware, firmware and host software, layered driver to framing to application.
6. Design a firmware-update mechanism: how does the MCU load and validate a new image without bricking itself?
7. Design a software timer library: many concurrent timers multiplexed onto one hardware timer.
8. Design a producer-consumer FIFO shared between two cores, with no shared cache.

---

## Where these came from

Prompts 1 and 6 are reported near-verbatim from Tesla's take-home; 2 from a Medtronic
report; 4, 7 and 8 from Meta Reality Labs and general embedded design-round reports; 3 from
a Google embedded guide. 5 is a composite. Sourcing, dates and confidence ratings are in
`research/prompt1-research-results-formatted.md` §4c — several are MEDIUM, and one is LOW.

Treat the list as representative rather than exhaustive. The skill is the six axes, and the
subject rotating is what stops you memorising an answer.
