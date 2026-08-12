# Repos — the plain answer

## Rename `embedded-c` to `embedded-training` and consolidate into it

That's the right call. One repo for all practice, renamed, with this bundle dropped in.

**Why `embedded-training` and not `interview-prep`.** It names a practice engineers respect and
it doesn't announce that you're job hunting. `interview-prep` with 300 commits reads as cramming;
`embedded-training` with 300 commits and a falling time curve reads as discipline. It also ages
well — you'll still use it after you're hired.

**This repo is public.** It contains the training system and the research behind it, and nothing
about where to apply or what to ask for — that belongs in a private file, not here. A public
training log with a falling time curve is evidence; keep it that way.

```bash
# GitHub: Settings -> Repository name -> embedded-training
cd ~/embedded/embedded-c
git remote set-url origin git@github.com:you/embedded-training.git
cd .. && mv embedded-c embedded-training
```

Then follow the migration checklist in `reference/ARCHITECTURE.md`.

---


**Three separate GitHub repos. No nesting. Never a repo inside a repo.**

A folder on your laptop is not a repo. `~/embedded/` is just a folder that holds three of them.

The parent folder's name doesn't matter to anything — nothing depends on it, no tool reads it, and
you can rename it any time. `~/embedded/` is the default here only because you'll type it several
times a day and short wins. `~/embedded-journey/` or `~/robotics/` are fine if you prefer them.

---

## On your laptop

```
~/embedded/                     ← a plain folder. NOT in git. Just where things live.
│
├── embedded-training/          ← REPO 1  PRIVATE. The plan, practice, and measurement.
│   ├── plan/                   the program: requirements, coverage, calendar, applications
│   ├── practice/               katas, decks, design prompts, rehearsal
│   ├── reference/              question bank, architecture notes
│   ├── projects/               specs for the one-shot artifacts
│   ├── tools/                  the machinery
│   └── logs/                   the record
│
├── mimic/                      ← REPO 2  PUBLIC. Already set up. Untouched by this system.
│
├── mimic-hil/                  ← REPO 3  PUBLIC. Created week 8.
│
└── scratch/                    ← NOT a repo. Throwaway C. Delete freely.
```

Three `.git` directories. Three GitHub repos. They sit **side by side**, never inside each other.

---

## Moving Mimic into `~/embedded/`

Do it. It stays a completely separate git repo with its own remote — this is a filesystem move,
not a git operation:

```bash
mkdir -p ~/embedded
mv ~/wherever/mimic ~/embedded/mimic
```

Nothing else changes. No submodule, no shared history, no path in either repo points at the
other. The only benefit is convenience: one place to `cd` between, one directory to back up.

**The boundary, stated plainly:** `embedded-training` *schedules* your Mimic hours in
`plan/CALENDAR.md` and *tracks what Mimic covers* in `plan/COVERAGE.md`, so you know what not to
duplicate. It contains no Mimic content. Mimic doesn't know this repo exists.

## What `scratch/` is for

Throwaway C. When you want to know what integer promotion actually does, or whether a particular
shift is undefined, you write eight lines, compile it, look at the answer, and delete it.

Two reasons it exists: so you never feel the urge to commit junk into a real repo, and so there
is a zero-friction place to poke at the language. During the first few weeks of C you will want
that constantly. It's a habit rather than infrastructure — skip it if you don't want it.

## Why three and not one

**Because a hiring manager opens one URL and should see one clean thing.**

If Mimic lives inside `embedded-training`, then the link you put on your resume lands someone in a
repo whose front page is a study plan, with 400 practice commits burying the robot. That's the
whole reason for the split — it isn't tidiness, it's what the reader sees first.

| Repo | Audience | Visibility | Commit character |
|---|---|---|---|
| `embedded-training` | You | Private for now. Decide at week 10 | Hundreds of small daily commits |
| `mimic` | Hiring managers | **Public** | The build history, including failures |
| `mimic-hil` | Hiring managers | **Public** | Clean, focused, one job |

The rule: **if you'd put the URL on your resume, it's its own repo.**

---

## Why not git submodules

You may be tempted to nest them with submodules so there's "one main repo." Don't.

- Submodules break clone-and-run for anyone who visits, which defeats the point of a portfolio.
- They add a class of git problem you'll spend evenings on instead of writing C.
- They don't actually solve anything here. These three projects share no code.

The only thing that links them is the harness pointing at Mimic's board, and that link is a
**sentence in a README**, not a git dependency.

---

## What `mimic-hil` actually is

The week 8 project. Plain version: **a Python program on your PC that tests your robot's firmware
automatically.**

1. Flashes new firmware to the Stage 0 board.
2. Talks to it over the USB serial cable — sends commands, reads telemetry back.
3. Asserts pass/fail. Does it hold position? Does the stall latch trip? Does it reject a bad
   command?
4. Injects faults on purpose — truncated frames, bad CRCs, impossible values — and checks the
   board recovers instead of hanging.
5. Runs **automatically on every `git push`**, via GitHub Actions with your own PC registered as
   a self-hosted runner. GitHub's cloud machines don't have a motor plugged into them, which is
   the whole reason a self-hosted runner exists.

"HIL" is hardware-in-the-loop: real firmware, on real hardware, exercised by software, in a loop.

Name it whatever you like — `mimic-hil`, `mimic-testbench`, `joint-hil`. This is the wedge, and
it is the repo to pin first.

## What links them, in practice

`mimic-hil/README.md` opens with something like:

> Hardware-in-the-loop test harness for the Mimic Stage 0 joint controller
> ([firmware here](https://github.com/you/mimic)). Flashes the board, drives it over serial,
> injects faults, and runs on every commit against real hardware via a self-hosted runner.

`mimic/README.md` links back:

> Verified by an automated HIL harness — see [mimic-hil](https://github.com/you/mimic-hil).

That's the whole integration. Two links and a shared board.

---

## Which get pinned on your GitHub profile

Pin in this order:

1. **`mimic-hil`** — the wedge. Firmware test automation and CI on hardware is the thing the job
   postings ask for and almost nobody has.
2. **`mimic`** — the depth. Real motor, real control loop, real bench work.
3. **`embedded-training`** — optional, and only if you make it public. Pinning it says "I practise
   deliberately and I measure it," which some managers like and none dislike. Your call.

---

## Setup, in six commands

```bash
mkdir -p ~/embedded && cd ~/embedded

# repo 1 — rename your existing embedded-c, then drop this bundle in
mv ~/wherever/embedded-c ~/embedded/embedded-training
cd embedded-training && git remote set-url origin git@github.com:you/embedded-training.git

# repo 2 — Mimic's own workbook creates this in S0
cd ~/embedded && git clone git@github.com:you/mimic.git

# repo 3 — week 8, not now
mkdir -p ~/embedded/scratch
```

Don't create `mimic-hil` until week 8. An empty repo sitting there for two months is worse than
no repo.
