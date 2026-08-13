# Repos

Three repos, side by side, never nested. This file explains which is which and why the split
is drawn where it is.

```
~/embedded/                     a plain folder. NOT in git. Just where things live.
│
├── embedded-training/          REPO 1  this one. The plan, the practice, the measurement.
│   ├── plan/                   the program: requirements, coverage, calendar, curriculum
│   ├── practice/               katas, decks, design prompts, rehearsal
│   ├── reference/              question bank, architecture notes
│   ├── projects/               specs for the one-shot artifacts
│   ├── tools/                  the machinery
│   └── logs/                   the record
│
├── mimic/                      REPO 2  the robot. Its own repo, its own layout.
│
├── mimic-hil/                  REPO 3  the HIL harness. Created in week 8.
│
└── scratch/                    NOT a repo. Throwaway C. Delete freely.
```

Three `.git` directories. Three remotes. The parent folder's name doesn't matter to anything —
nothing depends on it and no tool reads it.

---

## What is in this repo, and what is deliberately not

`embedded-training` holds the training system and the interview research behind it. It holds
**nothing about where to apply or what to ask for.** That is not squeamishness, it is scope:
this repo's whole claim is that it measures capability, and a capability log stops being
readable the moment it turns into a job-search diary.

`.gitignore` reserves `plan/APPLICATIONS.md` and `plan/private/` for exactly that material, so
there is somewhere obvious to put it that is not here.

**Why the name.** `embedded-training` names a practice engineers respect and it ages well —
it is still the right name after the job search that prompted it is over. `interview-prep`
with three hundred commits reads as cramming; a training log with three hundred commits and a
falling time curve reads as discipline.

---

## Why three repos and not one

**Because a reader opens one URL and should land on one clean thing.**

If the robot lived inside `embedded-training`, its front page would be a study plan with four
hundred practice commits burying the actual project. That is the whole reason for the split.
It is not tidiness, it is what the reader sees first.

| Repo | What it is | Commit character |
|---|---|---|
| `embedded-training` | The gym. One habit surface, one `make`, one log | Hundreds of small daily commits |
| `mimic` | The robot. Real motor, real control loop, real bench work | The build history, including failures |
| `mimic-hil` | The harness. Clean, focused, one job | Small and deliberate |

The rule of thumb: **if it exists to make you faster, it belongs here. If it is the thing
itself, it gets its own repo.**

Everything practice-related stays in this one repo, without exception — all katas, the
question bank, the curriculum, the decks, the log. Four reasons:

- **One habit surface.** A daily practice that requires `cd`-ing between four repos is a
  practice you stop doing in nine days.
- **One CI config.** The Actions workflow running gcc and clang under sanitizers is the
  expensive part. Write it once; all twelve katas ride on it.
- **Cross-links resolve.** `reference/question-bank/embedded-concepts.md` can say "see kata
  `register_map`" as a relative link that works. Across repos it is a dead URL.
- **The log is only meaningful if it is global.** `logs/log.tsv` tracks one time curve across
  every module. Split the repos and you split the log.

---

## The Mimic boundary, stated plainly

`embedded-training` **schedules** Mimic hours in `plan/CALENDAR.md` and **tracks what Mimic
covers** in `plan/COVERAGE.md`, so the two systems do not duplicate each other. It contains no
Mimic content. Mimic does not know this repo exists.

That boundary has a cost and it is worth naming: capabilities owned by Mimic cannot be
verified from here. `make progress` reports them as **tracked outside this repo** and excludes
them from the score rather than counting them as done. That is not the same as evidence, and
the progress report says so in as many words.

Moving Mimic into `~/embedded/` is a filesystem move, not a git operation:

```bash
mkdir -p ~/embedded
mv ~/wherever/mimic ~/embedded/mimic
```

Nothing else changes. No submodule, no shared history, no path in either repo pointing at the
other.

## What `scratch/` is for

Throwaway C. When you want to know what integer promotion actually does, or whether a
particular shift is undefined, you write eight lines, compile it, read the answer, and delete
it. Two reasons it exists: so there is never a reason to commit junk into a real repo, and so
there is a zero-friction place to poke at the language. It is a habit rather than
infrastructure — skip it if you don't want it.

---

## Why not git submodules

Nesting these with submodules to get "one main repo" is tempting and wrong.

- Submodules break clone-and-run for anyone who visits, which defeats the point of a public
  project.
- They add a class of git problem you will spend evenings on instead of writing C.
- They solve nothing here. These three projects share no code.

The only thing linking them is the harness pointing at Mimic's board, and that link is a
**sentence in a README**, not a git dependency.

---

## What `mimic-hil` actually is

The week 8 project. Plain version: **a Python program on a PC that tests the robot's firmware
automatically.**

1. Flashes new firmware to the Stage 0 board.
2. Talks to it over the USB serial cable — sends commands, reads telemetry back.
3. Asserts pass/fail. Does it hold position? Does the stall latch trip? Does it reject a bad
   command?
4. Injects faults on purpose — truncated frames, bad CRCs, impossible values — and checks the
   board recovers instead of hanging.
5. Runs **automatically on every `git push`**, via GitHub Actions with a self-hosted runner.
   GitHub's cloud machines don't have a motor plugged into them, which is the whole reason a
   self-hosted runner exists.

"HIL" is hardware-in-the-loop: real firmware, on real hardware, exercised by software, in a
loop. The spec is [`projects/hil-harness/BRIEF.md`](../projects/hil-harness/BRIEF.md).

Don't create the repo until week 8. An empty repo sitting there for two months is worse than
no repo.

### What links them, in practice

`mimic-hil/README.md` opens with something like:

> Hardware-in-the-loop test harness for the Mimic Stage 0 joint controller
> ([firmware here](https://github.com/…/mimic)). Flashes the board, drives it over serial,
> injects faults, and runs on every commit against real hardware via a self-hosted runner.

`mimic/README.md` links back:

> Verified by an automated HIL harness — see [mimic-hil](https://github.com/…/mimic-hil).

That is the whole integration. Two links and a shared board.
