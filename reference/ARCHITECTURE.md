# Architecture

## The decision: three tiers, not one repo and not fifteen

Your instinct that this needs restructuring is right. But "one folder outside git with many
little repos" is the wrong fix, because it optimises for tidiness and you need it to optimise
for **habit** and **hireability**. Those pull in different directions, so split by *purpose*,
not by size.

```
~/embedded/
├── embedded-training/          TIER 1 — the gym.        ONE repo. Private or public.
├── mimic/                 TIER 2 — the robot.       Its own repo. Public. Mimic's own layout.
├── portfolio/
│   └── hil-harness/       TIER 2 — the shopfront.  Public. Points AT the Mimic Stage 0 board.
└── scratch/                TIER 3 — the bin.        Not in git. Ever.
```

### Tier 1 — `embedded-training` (this repo). One repo, no exceptions.

Everything practice-related lives here: all katas, the question bank, the curriculum, the
decks, the log. Reasons:

- **One habit surface.** A daily practice you have to `cd` between four repos to do is a
  practice you stop doing in nine days. One repo, one `make`, one commit stream.
- **One CI config.** You already have GitHub Actions running gcc/clang with sanitizers. That
  config is the expensive part. Write it once, let all eleven katas ride on it.
- **Cross-linking works.** `reference/question-bank/embedded-concepts.md` says "see kata `register_map`"
  and it's a relative link that actually resolves. Across repos it's a dead URL.
- **The log is only meaningful if it's global.** `logs/log.tsv` tracks your time curve across
  every module. Split the repos and you split the log, and the time curve is the single best
  progress signal you have.
- **Commit density is the point.** One repo with 300 commits over two months looks like
  deliberate practice. Fifteen repos with 20 commits each look abandoned.

**Your existing `embedded-c` repo becomes this.** Don't start fresh. Rename it, drop these
files in, add the five new katas. Your log.tsv history carries over and that history is worth
keeping.

### Tier 2 — `portfolio/*`. One repo per real project.

Mimic and the HIL harness. These are **separate repos and they are public**, because:

- A hiring manager who opens a repo needs to land on a clean README about one thing. Your
  flagship HIL harness must not be buried in `/projects/05-hil/` under 300 practice commits.
- These have real dependency sets, real hardware requirements, real install steps. They don't
  belong in a repo whose Makefile is tuned for freestanding C katas.
- You link to them individually from your resume and from LinkedIn outreach.
- Mimic already has its own prescribed repository layout in its Stage 0 workbook. Don't fight it;
  it lives beside this repo, not inside it.

Rule of thumb for which tier: **if you'd put the URL on your resume, it's Tier 2.** If it only
exists to make you faster, it's Tier 1.

### Tier 3 — `~/scratch/`. Not in git.

Where you type things to see what the compiler does. Nothing here is ever kept. If something
in scratch turns out to be worth keeping, it graduates to a kata or a project.

---

## The gitignore trick that makes katas repeatable

This is the important bit and it's the thing your current layout is missing.

Inside each kata module:

```
katas/ring_buffer/
├── BRIEF.md          committed   what it is, the API, how to think about it
├── VARIANTS.md       committed   the 6 variants of this kata
├── NOTES.md          committed   your design decisions and bugs, one line per rep
├── include/
│   └── ring_buffer.h committed   the API contract. Frozen. You do not edit this.
├── tests/
│   └── test_*.c      committed   the test suite. Frozen. You do not edit this.
└── src/
    └── ring_buffer.c GITIGNORED  your implementation. Deleted before every rep.
```

`.gitignore` contains `practice/katas/*/src/`.

**Why this works:** the expensive, correct, hard-won artifacts (the API contract and the tests)
are permanent and version-controlled. Your implementation — the thing you're trying to get fast
at producing — is disposable. `make drill` deletes `src/`, writes an empty stub, and starts a
timer. Every rep is a genuine cold start because your last solution isn't sitting there to
read.

You get the repeatability of a kata without the "I already solved this" problem, and your git
history stays clean because it only ever contains the parts that should be stable.

The only thing that accumulates across reps is `NOTES.md` and `logs/log.tsv`. That is exactly
right: what you keep is the *lesson* and the *time*, not the code.

---

## Starting from nothing

If your existing `embedded-c` repo has no real history — no reps logged, no implementations
written — there is nothing to migrate. Start a fresh repo named `embedded-training`, copy across
only the Makefile rules, the Actions workflow, `check_log.py`, and any BRIEF you actually wrote,
and delete the rest.

**See `SETUP.md` for the staged build order.** The short version: build four katas before day 1,
not eleven, and add one a week as the calendar reaches it.

Your toolchain choices — C11, `-Werror`, ASan + UBSan, gcc and clang, `make test`, Actions — are
good. Keep them. They are better than what most candidates have.
