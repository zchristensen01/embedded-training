# Calendar

Seventy days. Every day has a fixed kata, a fixed main block, and timer durations.
Set a timer for each block. When it rings, move on even if you aren't finished —
running over on the main block is how the kata and deck slots get eaten.

**Sprint days (Mon, Tue, Thu, Fri):** 10-minute kata. Short modules only.
**Long-rep days (Wed, Sun):** 25-minute kata. The modules that need real time.
**Saturday:** a 10-minute adaptive rep, then the 2-hour main block. Still no deck.
**Sunday:** the lightest day — one long rep, the weekly review, a full deck pass.

Saturday is the one day with no assigned module. `make drill` with no arguments
picks by worst recent time, then longest since last rep, then never attempted —
so Saturday is the day that catches whatever you have been avoiding.

Weekly load: about 11.0 hours, every week from week 3 on. Weeks 1 and 2
carry the build sessions on top of that — 15.2 and 14.2 hours. They are the two heavy
weeks of the ten, and they are heavy once instead of a little heavy for five.

---

## Build plan

**Generated from the rotation — do not edit this by hand, and do not copy it
anywhere else.** A kata has to exist before the first day that calls for it, so the
build order is a consequence of the schedule rather than a second list to keep in
sync. Change when a kata first appears and its build session moves with it.
`python3 tools/schedule.py --check` proves the two agree; CI runs it on every push.

Two sessions, not one a week. A weekly build slot is a running dependency: miss one
Sunday and the next week's rotation has nothing to draw from. After week 2 there is
nothing left to build.

| Built during | Modules | First drilled | Time |
|---|---|---|---|
| Day 0 weekend | `bitops`, `fsm`, `mem_primitives`, `ring_buffer` | week 1 | 4 hr 30 min |
| Week 1 Sunday | `protocol_parser`, `register_map`, `pool_allocator`, `debouncer` | weeks 2–4 | 4 hr 30 min |
| Week 2 Sunday | `fixed_point_pid`, `rollover_timer`, `concurrency_sim` | weeks 5–6 | 3 hr 30 min |

**`test_harness_py` is not in the table above, deliberately.** It is built by week 7's main block rather than by a build session. Week 7 is five consecutive days of pytest from zero — discovery, assertions, fixtures, conftest.py, parametrize — and this kata is the artifact those five days produce. Giving it its own build slot would mean writing the same suite twice. This is a deliberate exception, not an oversight: it is the one module whose build IS the main work.

So it is built in week 7 and first drilled in week 7 — inside the same week, rather than the week before like everything else. That is the one place the usual rule does not apply. It is checked separately rather than waived, so if week 7's main block ever moves later than its first rep, `--check` will say so.

---

## Week 1 — MIMIC STAGE 0

**Mimic this week:** S0 bench, toolchain, repo · S1 motor forensics and bolting it down
**Deck focus:** types, pointers, strings

### **Day 1 · Mon**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=bitops VARIANT=v1 |
| **60 min** | Main block | Mimic: S0 bench, toolchain, repo · S1 motor forensics and bolting it down |
| **12 min** | Deck | make review  (types, pointers, strings) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 2 · Tue**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=mem_primitives VARIANT=v1 |
| **60 min** | Main block | Mimic: S0 bench, toolchain, repo · S1 motor forensics and bolting it down |
| **12 min** | Deck | make review  (types, pointers, strings) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 3 · Wed**  (90 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=ring_buffer VARIANT=v1 |
| **45 min** | Main block | Mimic: S0 bench, toolchain, repo · S1 motor forensics and bolting it down |
| **12 min** | Deck | make review  (types, pointers, strings) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 4 · Thu**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=bitops VARIANT=v2 |
| **60 min** | Main block | Mimic: S0 bench, toolchain, repo · S1 motor forensics and bolting it down |
| **12 min** | Deck | make review  (types, pointers, strings) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 5 · Fri**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=mem_primitives VARIANT=v2 |
| **60 min** | Main block | Mimic: S0 bench, toolchain, repo · S1 motor forensics and bolting it down |
| **12 min** | Deck | make review  (types, pointers, strings) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 6 · Sat**  (130 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill   (no argument — picks your weakest module) |
| **120 min** | Main block | S0/S1 overflow. Get the motor bolted down before anything else. |

### **Day 7 · Sun**  (330 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=fsm VARIANT=v1 |
| **20 min** | Weekly review | make report, then fill logs/WEEKLY_REVIEW.md |
| **15 min** | Deck — full pass | make review 30 |
| **270 min** | Kata build | BUILD x4: protocol_parser, register_map, pool_allocator, debouncer. Write the header first, then list the cases in the BRIEF, then write them. Every BRIEF ships with a 'What to test' section. |

---

## Week 2 — MIMIC STAGE 0

**Mimic this week:** S2 power topology and first soldering · S3 encoder, interrupts, x4 decoding
**Deck focus:** interrupts, memory

### **Day 8 · Mon**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=mem_primitives VARIANT=v3 |
| **60 min** | Main block | Mimic: S2 power topology and first soldering · S3 encoder, interrupts, x4 decoding |
| **12 min** | Deck | make review  (interrupts, memory) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 9 · Tue**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=bitops VARIANT=v3 |
| **60 min** | Main block | Mimic: S2 power topology and first soldering · S3 encoder, interrupts, x4 decoding |
| **12 min** | Deck | make review  (interrupts, memory) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 10 · Wed**  (90 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=ring_buffer VARIANT=v2 |
| **45 min** | Main block | Mimic: S2 power topology and first soldering · S3 encoder, interrupts, x4 decoding |
| **12 min** | Deck | make review  (interrupts, memory) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 11 · Thu**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=register_map VARIANT=v1 |
| **60 min** | Main block | Mimic: S2 power topology and first soldering · S3 encoder, interrupts, x4 decoding |
| **12 min** | Deck | make review  (interrupts, memory) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 12 · Fri**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=mem_primitives VARIANT=v4 |
| **60 min** | Main block | Mimic: S2 power topology and first soldering · S3 encoder, interrupts, x4 decoding |
| **12 min** | Deck | make review  (interrupts, memory) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 13 · Sat**  (130 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill   (no argument — picks your weakest module) |
| **120 min** | Main block | S2 power. Draw the topology before you wire it. Solder. |

### **Day 14 · Sun**  (270 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=protocol_parser VARIANT=v1 |
| **20 min** | Weekly review | make report, then fill logs/WEEKLY_REVIEW.md |
| **15 min** | Deck — full pass | make review 30 |
| **210 min** | Kata build | BUILD x3: fixed_point_pid, rollover_timer, concurrency_sim (builds under -fsanitize=thread, not address). Write the header first, then list the cases in the BRIEF, then write them. Every BRIEF ships with a 'What to test' section. |

---

## Week 3 — MIMIC STAGE 0

**Mimic this week:** S4 open loop, both directions · S5 the fixed-rate loop, rate proven
**Deck focus:** volatile, static, const

### **Day 15 · Mon**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=register_map VARIANT=v2 |
| **60 min** | Main block | Mimic: S4 open loop, both directions · S5 the fixed-rate loop, rate proven |
| **12 min** | Deck | make review  (volatile, static, const) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 16 · Tue**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=bitops VARIANT=v4 |
| **60 min** | Main block | Mimic: S4 open loop, both directions · S5 the fixed-rate loop, rate proven |
| **12 min** | Deck | make review  (volatile, static, const) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 17 · Wed**  (90 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=ring_buffer VARIANT=v3 |
| **45 min** | Main block | Mimic: S4 open loop, both directions · S5 the fixed-rate loop, rate proven |
| **12 min** | Deck | make review  (volatile, static, const) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 18 · Thu**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=register_map VARIANT=v3 |
| **60 min** | Main block | Mimic: S4 open loop, both directions · S5 the fixed-rate loop, rate proven |
| **12 min** | Deck | make review  (volatile, static, const) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 19 · Fri**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=mem_primitives VARIANT=v5 |
| **60 min** | Main block | Mimic: S4 open loop, both directions · S5 the fixed-rate loop, rate proven |
| **12 min** | Deck | make review  (volatile, static, const) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 20 · Sat**  (130 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill   (no argument — picks your weakest module) |
| **120 min** | Main block | S3/S4 overflow. First logic-analyzer capture goes in docs/. |

### **Day 21 · Sun**  (80 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=pool_allocator VARIANT=v1 |
| **20 min** | Weekly review | make report, then fill logs/WEEKLY_REVIEW.md |
| **15 min** | Deck — full pass | make review 30 |
| **10 min** | Design prompt | make prompt  (T1 — ask for requirements first) |
| **10 min** | Rehearsal | make rehearse  (one story, out loud, timed) |

---

## Week 4 — MIMIC STAGE 0

**Mimic this week:** S6 units, convert at the boundary · S7 telemetry and the bandwidth budget
**Deck focus:** registers, alignment

### **Day 22 · Mon**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=register_map VARIANT=v4 |
| **60 min** | Main block | Mimic: S6 units, convert at the boundary · S7 telemetry and the bandwidth budget |
| **12 min** | Deck | make review  (registers, alignment) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 23 · Tue**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=debouncer VARIANT=v1 |
| **60 min** | Main block | Mimic: S6 units, convert at the boundary · S7 telemetry and the bandwidth budget |
| **12 min** | Deck | make review  (registers, alignment) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 24 · Wed**  (90 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=protocol_parser VARIANT=v2 |
| **45 min** | Main block | Mimic: S6 units, convert at the boundary · S7 telemetry and the bandwidth budget |
| **12 min** | Deck | make review  (registers, alignment) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 25 · Thu**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=register_map VARIANT=v5 |
| **60 min** | Main block | Mimic: S6 units, convert at the boundary · S7 telemetry and the bandwidth budget |
| **12 min** | Deck | make review  (registers, alignment) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 26 · Fri**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=bitops VARIANT=v5 |
| **60 min** | Main block | Mimic: S6 units, convert at the boundary · S7 telemetry and the bandwidth budget |
| **12 min** | Deck | make review  (registers, alignment) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 27 · Sat**  (130 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill   (no argument — picks your weakest module) |
| **120 min** | Main block | SWAP: Mimic M4.1 — EMG features on public datasets. Python, no hardware. |

### **Day 28 · Sun**  (80 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=fsm VARIANT=v2 |
| **20 min** | Weekly review | make report, then fill logs/WEEKLY_REVIEW.md |
| **15 min** | Deck — full pass | make review 30 |
| **10 min** | Design prompt | make prompt  (T1 — ask for requirements first) |
| **10 min** | Rehearsal | make rehearse  (one story, out loud, timed) |

---

## Week 5 — MIMIC STAGE 0

**Mimic this week:** S8 P only, stability boundary · S9 step-response metrics · S10 D then I
**Deck focus:** protocols, timing

### **Day 29 · Mon**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=debouncer VARIANT=v2 |
| **60 min** | Main block | Mimic: S8 P only, stability boundary · S9 step-response metrics · S10 D then I |
| **12 min** | Deck | make review  (protocols, timing) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 30 · Tue**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=register_map VARIANT=v6 |
| **60 min** | Main block | Mimic: S8 P only, stability boundary · S9 step-response metrics · S10 D then I |
| **12 min** | Deck | make review  (protocols, timing) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 31 · Wed**  (90 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=fixed_point_pid VARIANT=v1 |
| **45 min** | Main block | Mimic: S8 P only, stability boundary · S9 step-response metrics · S10 D then I |
| **12 min** | Deck | make review  (protocols, timing) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 32 · Thu**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=rollover_timer VARIANT=v1 |
| **60 min** | Main block | Mimic: S8 P only, stability boundary · S9 step-response metrics · S10 D then I |
| **12 min** | Deck | make review  (protocols, timing) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 33 · Fri**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=bitops VARIANT=v6 |
| **60 min** | Main block | Mimic: S8 P only, stability boundary · S9 step-response metrics · S10 D then I |
| **12 min** | Deck | make review  (protocols, timing) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 34 · Sat**  (130 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill   (no argument — picks your weakest module) |
| **120 min** | Main block | S8/S9 tuning runs. Save every plot, including the bad ones. |

### **Day 35 · Sun**  (80 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=ring_buffer VARIANT=v4 |
| **20 min** | Weekly review | make report, then fill logs/WEEKLY_REVIEW.md |
| **15 min** | Deck — full pass | make review 30 |
| **10 min** | Design prompt | make prompt  (T1 — ask for requirements first) |
| **10 min** | Rehearsal | make rehearse  (one story, out loud, timed) |

---

## Week 6 — MIMIC STAGE 0

**Mimic this week:** S11 safety envelope and real PWM · S12 the refactor, tests, exit gate
**Deck focus:** sync, RTOS

> **GATE WEEK.** Stage 0 exit tagged `v0.0-stage0-exit`, clean-first-compile
> above 55%, 25+ logged reps. **Applications go out Sunday.**

### **Day 36 · Mon**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=register_map VARIANT=v7 |
| **60 min** | Main block | Mimic: S11 safety envelope and real PWM · S12 the refactor, tests, exit gate |
| **12 min** | Deck | make review  (sync, RTOS) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 37 · Tue**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=debouncer VARIANT=v3 |
| **60 min** | Main block | Mimic: S11 safety envelope and real PWM · S12 the refactor, tests, exit gate |
| **12 min** | Deck | make review  (sync, RTOS) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 38 · Wed**  (90 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=pool_allocator VARIANT=v2 |
| **45 min** | Main block | Mimic: S11 safety envelope and real PWM · S12 the refactor, tests, exit gate |
| **12 min** | Deck | make review  (sync, RTOS) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 39 · Thu**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=rollover_timer VARIANT=v2 |
| **60 min** | Main block | Mimic: S11 safety envelope and real PWM · S12 the refactor, tests, exit gate |
| **12 min** | Deck | make review  (sync, RTOS) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 40 · Fri**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=mem_primitives VARIANT=v7 |
| **60 min** | Main block | Mimic: S11 safety envelope and real PWM · S12 the refactor, tests, exit gate |
| **12 min** | Deck | make review  (sync, RTOS) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 41 · Sat**  (130 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill   (no argument — picks your weakest module) |
| **120 min** | Main block | S12 tests + exit gate evidence. Tag v0.0-stage0-exit. |

### **Day 42 · Sun**  (80 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=concurrency_sim VARIANT=v1 |
| **20 min** | Weekly review | make report, then fill logs/WEEKLY_REVIEW.md |
| **15 min** | Deck — full pass | make review 30 |
| **10 min** | Design prompt | make prompt  (T1 — ask for requirements first) |
| **10 min** | Rehearsal | make rehearse  (one story, out loud, timed) |

---

## Week 7 — TEST ENGINEERING

**Deck focus:** V&V, traceability, test design

### **Day 43 · Mon**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=bitops VARIANT=v1 |
| **60 min** | Main block | pytest from zero: discovery, assertions, exit codes. 20 tests on a pure function |
| **12 min** | Deck | make review  (V&V, traceability, test design) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 44 · Tue**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=register_map VARIANT=v1 |
| **60 min** | Main block | Fixtures, scope, teardown that survives a failing test. conftest.py |
| **12 min** | Deck | make review  (V&V, traceability, test design) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 45 · Wed**  (90 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=concurrency_sim VARIANT=v2 |
| **45 min** | Main block | parametrize. Then verification vs validation, test plan structure |
| **12 min** | Deck | make review  (V&V, traceability, test design) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 46 · Thu**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=mem_primitives VARIANT=v1 |
| **60 min** | Main block | Traceability, IEC 62304 classes, one test case per requirement |
| **12 min** | Deck | make review  (V&V, traceability, test design) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 47 · Fri**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=debouncer VARIANT=v4 |
| **60 min** | Main block | make prompt x3. Score each against the rubric |
| **12 min** | Deck | make review  (V&V, traceability, test design) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 48 · Sat**  (130 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill   (no argument — picks your weakest module) |
| **120 min** | Main block | Device abstraction over a fake transport. Same tests pass on both. |

### **Day 49 · Sun**  (80 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=test_harness_py VARIANT=v1 |
| **20 min** | Weekly review | make report, then fill logs/WEEKLY_REVIEW.md |
| **15 min** | Deck — full pass | make review 30 |
| **10 min** | Design prompt | make prompt  (T1 — ask for requirements first) |
| **10 min** | Rehearsal | make rehearse  (one story, out loud, timed) |

---

## Week 8 — THE HARNESS

**Deck focus:** test infra, pytest

### **Day 50 · Mon**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=register_map VARIANT=v3 |
| **60 min** | Main block | pyserial: open, write, read with timeout, frame responses. Talk to the board |
| **12 min** | Deck | make review  (test infra, pytest) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 51 · Tue**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=bitops VARIANT=v3 |
| **60 min** | Main block | Fixture that opens/closes the port and resets the device between tests |
| **12 min** | Deck | make review  (test infra, pytest) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 52 · Wed**  (90 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=test_harness_py VARIANT=v2 |
| **45 min** | Main block | Flashing from the harness. Test isolation |
| **12 min** | Deck | make review  (test infra, pytest) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 53 · Thu**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=rollover_timer VARIANT=v3 |
| **60 min** | Main block | Fault injection: truncated frames, bad CRC, impossible lengths. Assert recovery |
| **12 min** | Deck | make review  (test infra, pytest) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 54 · Fri**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=debouncer VARIANT=v5 |
| **60 min** | Main block | Trace each test to a Stage 0 requirement. Requirement IDs in test names |
| **12 min** | Deck | make review  (test infra, pytest) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 55 · Sat**  (130 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill   (no argument — picks your weakest module) |
| **120 min** | Main block | Dockerise the harness. GitHub Actions, self-hosted runner. |

### **Day 56 · Sun**  (80 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=ring_buffer VARIANT=v6 |
| **20 min** | Weekly review | make report, then fill logs/WEEKLY_REVIEW.md |
| **15 min** | Deck — full pass | make review 30 |
| **10 min** | Design prompt | make prompt  (T1 — ask for requirements first) |
| **10 min** | Rehearsal | make rehearse  (one story, out loud, timed) |

---

## Week 9 — FINISH AND WRITE UP

**Deck focus:** hardware, debug

### **Day 57 · Mon**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=bitops VARIANT=v5 |
| **60 min** | Main block | Green CI run against real hardware. Screenshot it |
| **12 min** | Deck | make review  (hardware, debug) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 58 · Tue**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=mem_primitives VARIANT=v5 |
| **60 min** | Main block | README: what it verifies, what it cannot catch, how tests trace to requirements |
| **12 min** | Deck | make review  (hardware, debug) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 59 · Wed**  (90 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=fsm VARIANT=v3 |
| **45 min** | Main block | make prompt x4. Then the full protocol and hardware verbal set |
| **12 min** | Deck | make review  (hardware, debug) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 60 · Thu**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=register_map VARIANT=v5 |
| **60 min** | Main block | Fill rehearsal/STORIES.md from Mimic's NOTES. Then make rehearse x4 |
| **12 min** | Deck | make review  (hardware, debug) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 61 · Fri**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=debouncer VARIANT=v6 |
| **60 min** | Main block | make rehearse B3, B4, B10. Record one. Watch it back |
| **12 min** | Deck | make review  (hardware, debug) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 62 · Sat**  (130 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill   (no argument — picks your weakest module) |
| **120 min** | Main block | Publish. Harness repo public. Site updated with the Stage 0 sequence. |

### **Day 63 · Sun**  (80 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=protocol_parser VARIANT=v3 |
| **20 min** | Weekly review | make report, then fill logs/WEEKLY_REVIEW.md |
| **15 min** | Deck — full pass | make review 30 |
| **10 min** | Design prompt | make prompt  (T1 — ask for requirements first) |
| **10 min** | Rehearsal | make rehearse  (one story, out loud, timed) |

---

## Week 10 — INTERVIEW SIMULATION

**Deck focus:** full deck, no filter

### **Day 64 · Mon**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=ring_buffer VARIANT=v3 |
| **60 min** | Main block | Timed 2-hour mock take-home, AI-free: state machine, debugging, bit masking |
| **12 min** | Deck | make review  (full deck, no filter) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 65 · Tue**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=register_map VARIANT=v4 |
| **60 min** | Main block | Debrief the take-home out loud as if defending it. Record. Watch it back |
| **12 min** | Deck | make review  (full deck, no filter) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 66 · Wed**  (90 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=test_harness_py VARIANT=v3 |
| **45 min** | Main block | Full deck pass. Every card box 4+ or it goes back to daily |
| **12 min** | Deck | make review  (full deck, no filter) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 67 · Thu**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=rollover_timer VARIANT=v4 |
| **60 min** | Main block | make rehearse B10 twice, timed. Then --stats: every story ready? |
| **12 min** | Deck | make review  (full deck, no filter) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 68 · Fri**  (90 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill KATA=mem_primitives VARIANT=v6 |
| **60 min** | Main block | Second application wave — embedded and firmware roles |
| **12 min** | Deck | make review  (full deck, no filter) |
| **8 min** | Log and commit | make done, log the session, git commit |

### **Day 69 · Sat**  (130 min)

| Timer | Block | What |
|---|---|---|
| **10 min** | Kata — sprint | make drill   (no argument — picks your weakest module) |
| **120 min** | Main block | make report. Compare the week 1 and week 10 curves. Write the retro. |

### **Day 70 · Sun**  (80 min)

| Timer | Block | What |
|---|---|---|
| **25 min** | Kata — LONG rep | make drill KATA=concurrency_sim VARIANT=v4 |
| **20 min** | Weekly review | make report, then fill logs/WEEKLY_REVIEW.md |
| **15 min** | Deck — full pass | make review 30 |
| **10 min** | Design prompt | make prompt  (T1 — ask for requirements first) |
| **10 min** | Rehearsal | make rehearse  (one story, out loud, timed) |

---

## Rules for the timer

0. **Call `make lap` at each transition** — when you start typing, when you first compile,
   and when it compiles clean. Four seconds, and it turns a total into a diagnosis.
1. **Start the kata timer before you read anything.** `make drill` starts its own clock;
   the block timer is separate and it is the one that stops you.
2. **When the kata timer rings, stop.** Log the rep as unfinished. An unfinished rep is
   data. A rep that ate the main block is a lost day.
3. **The deck block is not optional and not negotiable.** Twelve minutes, out loud.
4. **Overran the main block?** Take it out of tomorrow's main block, never out of the
   kata or deck.
5. **Missed a day?** Skip it, don't stack it. Two 90-minute days back to back produces
   one good session and one bad one.
