# The daily checklist

`make today` tells you *what* to do. This file explains what that printout **means**, and
what you owe the log at each end of a session so that nothing you did goes unrecorded.

Read it once now, and once again in week two. After that it is a reference you glance at,
not a document you work through.

---

## How to read a line from the calendar

A weekday looks like this. [`plan/CALENDAR.md`](plan/CALENDAR.md) is the committed copy
and labels days `Day 1 · Mon`; `make dates` writes `plan/CALENDAR.dated.md` alongside it
with your real dates, and that is the one to open.

| Timer | Block | What |
|---|---|---|
| **15 min** | Kata — sprint | make drill KATA=bitops VARIANT=v1 |
| **25 min** | Kata — Python | make drill KATA=binary_frame_py VARIANT=v1 |
| **55 min** | Main block | Mimic: S0 bench, toolchain, repo · S1 motor forensics |
| **12 min** | Deck | make review  (types, pointers, strings) |
| **8 min** | Log and commit | make done, log the session, git commit |

Six things to know about that table.

**The timer is a ceiling, not an estimate.** Set an actual timer for each block. When it
rings you move on, finished or not. Running over on the main block is how the kata and the
deck slots get eaten, which is the failure mode the whole shape is designed against.

**`make drill KATA=bitops VARIANT=v1` is one command, typed exactly as written.** `KATA=`
and `VARIANT=` are make variables, not placeholders — there is no substitution for you to
do. Running it:

- **deletes** `practice/katas/bitops/src/` and everything in it,
- writes an empty stub file containing only `#include "bitops.h"`,
- starts a clock,
- and about a third of the time deals you a **constraint card** ("no dynamic allocation",
  "write it on paper first") which applies to that rep only.

`v1` names a line in `practice/katas/bitops/VARIANTS.md` — the constraint you are working
under this time. Open that file, read the one line for `v1`, open `BRIEF.md` for the API,
and read **nothing else**. Your previous solution no longer exists, and that is the point:
every rep is a genuine cold start, so what accumulates is the fluency and the lesson rather
than the code.

**Text in parentheses is context, not arguments.** `make review  (types, pointers,
strings)` is the command `make review`, alone — the bracket tells you what this week's deck
focus is, so you know what most of the due cards will be about. Likewise `make drill   (no
argument — picks your weakest built module)` is the command `make drill`, with nothing after
it. If you genuinely want to pin the deck to one topic, that is `make review N="--topic
interrupts"`.

**Two katas, two languages, most weekdays.** The C rep and the Python rep are both
`make drill`, back to back, from week 1. They are interleaved rather than phased on purpose:
an interview loop does not block by language, and identifying which kind of problem you are
looking at before solving it is part of what is being trained. Tuesday and Thursday are C
only, at 90 minutes; the three days that carry a Python rep are 115. Keeping two weekdays
clear is what stops this becoming two full rotations.

**"Main block" is not in this repo.** For weeks 1–6 it is the Mimic robotics project in its
own repo; from week 7 it is the harness work. (Week 7 used to be "pytest from zero" — it is
not from zero any more, because the Python katas have been running since week 1.) This repo *schedules*
those hours and tracks what they cover — it does not contain them. See
[`plan/REPOS.md`](plan/REPOS.md).

---

## Every session — before you start

Four things, about ninety seconds.

- [ ] `make today` — read the whole printout, not just the kata name.
- [ ] **Set a timer for the first block** before you open anything else.
- [ ] `git status` — a dirty tree from yesterday means yesterday never got committed.
- [ ] Decide the one thing you will do if the main block overruns. It comes out of
      *tomorrow's* main block, never out of the kata or the deck.

---

## Every session — the rep, in order

```bash
make drill KATA=<name> VARIANT=<vN>   # exactly as the calendar prints it
    make lap                          # the first line of code you type   -> ends `design`
    make lap                          # your first compile attempt        -> ends `write`
                                      # (a Python rep: your first run attempt)
make test                             # frozen suite, under sanitizers
    make lap                          # it compiled clean                 -> ends `compile`
make done                             # tests pass. Stop the clock and log it
```

`make lap` takes four seconds and turns a total into a diagnosis. A total time tells you
whether you are getting faster; the split tells you *what is slow*, which is the part you
can act on. Missing a call is fine — `make done` attributes the remainder to the next phase.

**When the kata timer rings, stop and run `make done` anyway.** An unfinished rep is data.
A rep that ate the main block is a lost day. Answer `n` to the clean question and say so in
the note.

---

## Every session — before you close the laptop

This is the part that decides whether any of it counted.

- [ ] **`make done`** — if you have not already. It asks two questions and both matter:
      *clean on first compile?* (`y` only if it compiled first try **and** the sanitizers
      were silent) and *one line: a decision or a bug*. That line is appended to the kata's
      `NOTES.md` and is the only thing that survives the deleted `src/`.
- [ ] **Add a deck card if anything surprised you.** `make done` offers this automatically,
      which is the moment you are most likely to have been caught out. Say yes. A card
      written now is worth several written next Sunday from memory. It will refuse a card
      with no **trap** — the wrong answer an interviewer expects to hear — because the trap
      is what makes the card worth saying out loud.
- [ ] **`make review`** — out loud, in full sentences. A card counts as correct only if you
      also said the trap. This block is not optional and not negotiable.
- [ ] **Log anything the tools could not see, by hand.** Mimic hours, bench work, project
      time: one row in `logs/log.tsv` in the same format. `make check-log` validates it.
- [ ] **Log any AI use** in `logs/ai-use.tsv` — date, what for, which rule it fell under.
      Every use, including this repo's tooling. The count should fall over ten weeks; if it
      is growing by week 6, the rule is not being followed.
- [ ] **`git commit`.** The log files are the deliverable. An uncommitted week of practice
      is an unmeasured week of practice.

---

## What each day adds

The block *order* is below; the durations are printed by `make today` and generated into
the calendar, so they live in exactly one place and are not repeated here.

| Day | Blocks, in order | Notes |
|---|---|---|
| **Mon, Fri** | kata (sprint) → **Python kata** → main → deck → log and commit | Short C modules only |
| **Tue, Thu** | kata (sprint, assigned) → main → deck → log and commit | C only. The two short days |
| **Wed** | kata (**long**) → **Python kata** → main → deck → log and commit | The modules that need real time |
| **Sat** | kata (**adaptive**, no argument) → main → rehearsal *(from week 3)* | **No deck.** The only day with no assigned module |
| **Sun** | kata (long, assigned) → weekly review → full deck pass → **then see below** | Light, except during a build session. Tuesday and Thursday are the two shortest days |

Saturday's rep has no assigned module on purpose. `make drill` with no arguments picks by
worst recent time, then longest since the last rep, then never attempted — so one day a week
catches whatever you have been quietly avoiding. It is also the only slack in the rotation,
which is where a module's fourth and fifth reps come from.

---

## Sunday, after the deck pass

**Weeks 1–3 — a kata build session.** The calendar names the modules. See below.

**Week 4 onward — a design prompt and rehearsal:**

- [ ] `make prompt` — draws one of the 60 "how would you test X" subjects and opens a
      pre-scored answer file. Ten minutes written, then said aloud. **Fill in the rubric
      total**; an unscored answer counts for nothing. Two things fail you automatically
      regardless of the rest: proposing solutions before asking for requirements, and
      stopping before you are told to stop.
- [ ] `make rehearse` — a behavioural story, out loud, timed. A story is ready at three
      takes rated strong **on three different days**; three takes in one afternoon is one
      rehearsal. Fill in `practice/rehearsal/STORIES.md` before the first take — the file
      ships as a skeleton and the stories have to be yours.

**Every Sunday, either way:**

- [ ] `make report` — the time curve, the clean-first-compile rate, the phase breakdown,
      and which katas you are avoiding.
- [ ] Copy the block in `logs/WEEKLY_REVIEW.md` and fill it in honestly. Ten minutes.
- [ ] `make progress` — rescores every capability from the logs and regenerates
      `logs/PROGRESS.md`. **Never edit those files by hand**; `make check-generated` will
      catch it.
- [ ] `make check` before you push.

---

## Build sessions

Three Sundays in weeks 1–3, plus the day-0 weekend before the plan starts. `make
check-calendar` prints which modules and how long; the order is derived from the rotation,
so it is never written down twice.

For each module named:

- [ ] `make newkata NAME=<module>` — scaffolds the directories, a header stub, and a test
      *runner*.
- [ ] **Write the contract, first, before anything else.** For a C module that is
      `include/<module>.h`. For a Python module (`*_py`) there is no header — the contract is
      the API written out in `BRIEF.md`, and the test suite is what enforces it. Either way it
      is frozen once written and you live with it for weeks.
- [ ] **List the cases** in `BRIEF.md` under "What to test", in your own words, before
      writing any of them.
- [ ] **Write every case** in `tests/`, yourself.
- [ ] `make check-frozen` — the header parses standalone and the suite compiles, on gcc and
      clang. Python modules are not compiled; run `make test MODULE=<module>` instead and
      confirm pytest collects the suite.

> **This is not setup overhead, and the AI rule bites hardest here.** AI may write the test
> runner and the assert macros — that plumbing is already in the generated file. It may not
> write a single test case. "How would you test this" is a top-three question in both
> tracks; outsourcing the suite means outsourcing the thing you are selling.

---

## Practising off-plan

The calendar is a default, not a gate. **Every command works any day, in any order, with no
argument gymnastics** — nothing in this repo checks whether you are "allowed" to do something.
If you have twenty spare minutes and want to lift, here is the menu:

| You feel like | Run |
|---|---|
| A rep on the thing I'm worst at | `make drill` — no arguments, it picks that for you |
| A rep on one specific module | `make drill KATA=fsm` — picks the variant you've done least recently |
| That exact variant | `make drill KATA=fsm VARIANT=v4` |
| Debugging instead of writing | `make hunt` — one bug planted in your own old code |
| Talking instead of typing | `make review N=40`, out loud |
| One topic only | `make review N="--topic sync"` |
| The T&I muscle | `make prompt` — ten minutes, one subject, one rubric |
| To design something instead of testing it | `make design` — 45 minutes, architect a subsystem |
| A Python rep specifically | `make drill LANG=py` — or name the module: `make drill KATA=binary_frame_py` |
| The story I always fumble | `make rehearse S=B6` |
| Just to see where I am | `make report`, `make progress`, `make log`, `make decks`, `make hunts`, `make designs` |

**Swapping the assigned module for one you know you are worse at is using the system, not
cheating it.** The score is computed from `logs/log.tsv` — what you actually did — never from
what the calendar asked for. Skip a scheduled `bitops` in favour of `pool_allocator` and the
numbers follow you automatically. The only thing that notices is `make report`, which flags
anything untouched for fourteen days, and that is the point of it.

**Nothing is ever locked or retired.** A module that has met its bar keeps appearing in the
rotation and stays available to `make drill`. "Met" only means the capability resting on it is
now proved by the log instead of by feel.

The one refusal in the whole repo: `make drill` will not hand you a module whose frozen header
and test suite do not exist yet, because a rep against an empty suite is not a rep. It tells you
what you owe it instead.

---

## What gets recorded, and by what

| What you did | What records it | What you owe by hand |
|---|---|---|
| A kata rep | `make done` → `logs/log.tsv` | The clean answer, honestly, and the one-line note |
| Where the rep's time went | `make lap` → `logs/splits.tsv` | Calling `make lap` at each transition |
| Something you got wrong | `make card` → `practice/decks/*.tsv` | The question, the answer, and the **trap** |
| A deck pass | `make review` → local box state | Saying it **out loud**, with the trap |
| A design prompt | `make prompt` → `logs/design-prompts/` | **The rubric total.** Unscored counts for nothing |
| An architecture drill | `make design` → `logs/architecture/` | **The rubric total**, and the pushback on axis 8 |
| A behavioural take | `make rehearse` → `logs/rehearsal.tsv` | The rating, on the day |
| A bug hunt | `make hunt-done` → `logs/bughunt.tsv` | Whether you actually found it |
| Mimic / bench / project hours | nothing — the tools cannot see them | A row in `logs/log.tsv` |
| Any use of AI | nothing | A row in `logs/ai-use.tsv` |
| The week | `make report`, `make progress` | `logs/WEEKLY_REVIEW.md` |

Full command reference: [`reference/COMMANDS.md`](reference/COMMANDS.md).

---

## The five ways to lose a day

1. **Reading before starting the clock.** `make drill` first, then read the BRIEF. The
   design phase is a measurement, and it only measures if it is inside the timer.
2. **Letting the main block run over.** It takes the kata slot, then the deck slot, then the
   week. Take it out of tomorrow instead.
3. **Skipping the deck because the rep went badly.** The verbal round is the one that fails
   more people, and it is twelve minutes.
4. **Answering deck cards silently.** Knowing an answer and being unable to structure it
   aloud are different skills, and only one of them is being tested.
5. **Not committing.** The logs are the deliverable. Everything else is disposable on
   purpose.
