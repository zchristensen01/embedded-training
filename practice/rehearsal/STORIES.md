# Stories

Fill each in before the first take. Keep them short — the written version is a skeleton, not a
script. Source material: Mimic's `NOTES.md`, `docs/decisions/`, and your tuning git history.

Format: **S**ituation (one line) → **T**ask → **A**ction → **R**esult, plus what you'd do
differently.

---

## B1 · Why hardware, coming from web?
**Target: 60 seconds. Asked in every interview. This is the objection in their head.**

Strong contains: a real reason rooted in what you do, not what you dislike. The working
conditions point (alone, AI writing the code, never seeing it run) is honest but lands better as
one clause than as the whole answer. Land on the kinesiology and movement thread, and on the
robot you actually built.

Fails: "I want a new challenge." Also fails: bagging on web work, which reads as running away
rather than toward.

- Situation:
- Why hardware:
- Evidence I mean it:

---

## B2 · Why this domain — space / subsea / medical?
**Target: 45 seconds. Tailor per application.**

Strong contains: something specific about *their* product, and a genuine connection. For medical,
the kinesiology background is a real differentiator — say you understand the human system the
device attaches to or measures.

Fails: a generic "meaningful work" answer that would fit any of the four domains.

- Space/satellite version:
- Subsea version:
- Medical version:
- Research robotics version:

---

## B3 · Walk me through a project end to end
**Target: 3 minutes. In T&I this IS the technical screen.**

Strong contains: constraint → options → choice → trade-off. Name a decision you'd defend and one
you'd revisit.

Fails: a feature tour. Also fails: not knowing why you chose the design you chose.

- Project:
- The constraint:
- Options considered:
- What I chose and why:
- What I gave up:

---

## B4 · How did you test it?
**Target: 2 minutes. The T&I differentiator.**

Strong contains: concrete cases, not categories. Boundary and negative tests by name. The four
Stage 0 failure demonstrations — soft limits, velocity limiting, command timeout, stall latch —
are exactly this. Then the HIL harness and what runs on every commit.

Fails: "I tested it thoroughly." Also fails: only describing happy-path verification.

- What I verified and how:
- Negative and boundary cases:
- What the harness catches automatically:
- What it can't catch:

---

## B5 · A time you struggled with a problem and got through it
**Target: 90 seconds.**

Strong contains: a real dead end, what you tried that didn't work, and the specific thing that
broke it open. Mimic's "what will go wrong" sections will hand you this repeatedly.

Fails: a struggle that resolves in one step, which sounds invented.

- Situation / Task / Action / Result:

---

## B6 · A time you had a conflict with a coworker
**Target: 90 seconds. Asked at Medtronic and widely.**

Strong contains: a genuine disagreement, your own contribution to it, and a resolution that
didn't require the other person to be wrong.

Fails: a conflict where you were entirely right. Also fails: "I don't really have conflicts."

- Situation / Task / Action / Result:

---

## B7 · A time you pushed back on skipping a test
**Target: 90 seconds. A T&I favourite.**

Strong contains: the pressure that made skipping tempting, what you argued, and what happened.
If you don't have a work example, the Stage 0 exit gate is one — you can talk about refusing to
call the loop rate proven until you had a capture.

Fails: sounding rigid. The strong version acknowledges the schedule pressure was real.

- Situation / Task / Action / Result:

---

## B8 · A bug your tests caught that you'd have missed
**Target: 90 seconds.**

Strong contains: a specific bug and the specific test. The derivative-on-measurement unit test
from Stage 0's S12 is close to perfect for this — caught on a laptop in microseconds instead of
on a bench with a motor slamming.

Fails: a generic "unit tests are valuable" answer with no bug in it.

- The bug:
- The test that caught it:
- What it would have cost in the field:

---

## B9 · A time you were wrong about a root cause
**Target: 90 seconds.**

Strong contains: the wrong hypothesis, why it was plausible, what evidence changed your mind, and
what you now do differently. Interviewers are listening for whether you update on evidence.

Fails: a story where you were only briefly wrong and it cost nothing.

- Situation / Task / Action / Result:

---

## B10 · Ten-minute project presentation
**Target: 10 minutes, timed. SpaceX and Rocket Lab both ask for one.**

Structure: problem (1 min) → architecture (2) → one hard decision in depth (3) → how it's tested
(2) → what broke and what you'd change (2).

Slides optional; a live demo or a plotted step response beats slides. Have the logic-analyzer
capture and the green CI run on screen.

- Outline:
- The one hard decision I go deep on:
- The artifact I show:
