#!/usr/bin/env python3
"""design.py — the embedded system-design round: draw a prompt, time it, score it.

  python3 tools/design.py            draw the prompt you have done least
  python3 tools/design.py 3          that prompt by number
  python3 tools/design.py --stats    what you have written and what it scored
  python3 tools/design.py --list     the prompts

This is a different exercise from `make prompt`, and the difference is the whole point.
`make prompt` asks **how would you test this thing that already exists**. This asks you to
**invent the thing**, out loud, in 45 minutes, and then defend it when someone pushes back.
Candidate reports put it as a dedicated round at Google and Meta Reality Labs, and as a
design item inside Tesla's and Medtronic's take-homes. Nothing else in this repo produces
it: katas start from a written contract, and the design prompts start from a finished
object.

Both rubrics are out of 16 so `tools/progress.py` can parse either with one expression.
They are not the same rubric and they live in different directories.

Prompts come from `practice/design-prompts/ARCHITECTURE.md` and nowhere else.
E30's bar is three of these scored at 12+/16. B11 — defending the thing under pushback —
is rehearsal, and axis 8 below is where the two meet.
"""
import glob
import os
import re
import sys
import time
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "practice", "design-prompts", "ARCHITECTURE.md")
OUT = os.path.join(ROOT, "logs", "architecture")

MINUTES = 45
PROMPTS_HEADING = "## Prompts"

RUBRIC = """
| # | Criterion | Score 0-2 |
|---|---|---|
| 1 | Asked for constraints and requirements FIRST | |
| 2 | Partitioned ISR vs main vs task, and said why | |
| 3 | Budgeted RAM and flash, in numbers | |
| 4 | Chose a comms topology and justified it | |
| 5 | Planned power states and wake sources | |
| 6 | Failure handling: what fails, how it is detected, what safe state | |
| 7 | Testability: where the seams are, what you would fake | |
| 8 | Held the position under one round of pushback | |

**Pushback (axis 8): __ / 2**

**Total: __ / 16**

Fill in BOTH lines. `make progress` reads them, and E30 needs the total at 12+ **and axis 8
at 1 or more** — because seven perfect axes come to 14/16, so without that second gate you could
meet a bar whose stated point is surviving pushback while never being pushed. Three unscored
designs prove nothing.

Automatic fail if: you started drawing before asking what the constraints were, or you
produced a block diagram with no numbers on it. "Some RAM" is not a budget.

Axes 2-7 are the six the interviewer is actually grading. Axis 1 is the same gate as the
test-design rubric, for the same reason. Axis 8 is the behavioural half — B11 — and it is
scored here because a design you abandon under the first challenge did not survive.
"""


def prompts():
    """The numbered list under '## Prompts', and nothing else in the file."""
    if not os.path.exists(SRC):
        sys.exit(f"Missing {SRC}")
    text = open(SRC).read()
    i = text.find(PROMPTS_HEADING)
    if i < 0:
        sys.exit(f"No '{PROMPTS_HEADING}' section in {SRC}")
    body = text[i + len(PROMPTS_HEADING):]
    nxt = re.search(r"^##\s", body, re.M)
    if nxt:
        body = body[:nxt.start()]
    return re.findall(r"^\d+\.\s+(.+?)\s*$", body, re.M)


def written():
    """[(path, subject_slug, score_or_None)] for every design written so far."""
    out = []
    for path in sorted(glob.glob(os.path.join(OUT, "*.md"))):
        score = None
        try:
            m = re.search(r"Total:\s*(\d+)\s*/\s*16", open(path).read())
            if m:
                score = int(m.group(1))
        except OSError:
            pass
        out.append((path, os.path.basename(path)[11:-3], score))
    return out


def slug(subject):
    return re.sub(r"[^a-z0-9]+", "-", subject.lower()).strip("-")[:60]


def stats():
    done = written()
    scored = [s for _, _, s in done if s is not None]
    print(f"\n  {len(done)} design(s) written, {len(scored)} scored.\n")
    for path, name, score in done:
        print(f"  {os.path.basename(path):<48}  "
              f"{'—' if score is None else str(score) + '/16'}")
    if scored:
        print(f"\n  mean {sum(scored) / len(scored):.1f}/16, last {scored[-1]}/16")
    print("\n  E30 is met at three scored 12+/16. Axis 1 and axis 8 are the two that")
    print("  candidates lose on: designing before asking, and folding under pushback.\n")


def main():
    args = sys.argv[1:]
    subjects = prompts()
    if not subjects:
        sys.exit(f"No prompts found under '{PROMPTS_HEADING}' in {SRC}")

    if "--stats" in args:
        stats()
        return
    if "--list" in args:
        for i, s in enumerate(subjects, 1):
            print(f"  {i:>2}. {s}")
        return

    done = written()
    if args and args[0].isdigit():
        n = int(args[0])
        if not 1 <= n <= len(subjects):
            sys.exit(f"No prompt {n}. There are {len(subjects)}.")
        subject = subjects[n - 1]
    else:
        # Least-recently-written first, so the rotation spreads rather than converging
        # on whichever one you find least uncomfortable.
        seen = {name: i for i, (_, name, _) in enumerate(done)}
        subject = min(subjects, key=lambda s: seen.get(slug(s), -1))

    os.makedirs(OUT, exist_ok=True)
    base = f"{date.today().isoformat()}-{slug(subject)}"
    path = os.path.join(OUT, base + ".md")
    n = 2
    while os.path.exists(path):
        path = os.path.join(OUT, f"{base}-{n}.md")
        n += 1

    with open(path, "w") as fh:
        fh.write(f"# Design: {subject}\n\n")
        fh.write(f"Date: {date.today().isoformat()}  ·  {MINUTES} minutes  ·  "
                 f"draw it, then defend it out loud\n\n")
        fh.write("## Constraints I asked for\n\n_Before anything else. What did you need "
                 "to know, and what did you assume when nobody answered?_\n\n")
        fh.write("## Block diagram\n\n_Labelled. Every box, every line, every rate._\n\n")
        fh.write("## Memory and power budget\n\n_Numbers, not adjectives._\n\n")
        fh.write("## What fails, and what happens then\n\n\n")
        fh.write("## How I would test it\n\n\n")
        fh.write("## The pushback, and my answer\n\n_Argue against your own choice, then "
                 "answer it. This is the B11 half._\n\n")
        fh.write("## Score\n" + RUBRIC + "\n")
        fh.write("## What I missed\n\n")

    print("\n" + "=" * 70)
    print(f"  ARCHITECT:  {subject}")
    print("=" * 70)
    print(f"  {MINUTES} minutes. Ask for the constraints first — out loud, even alone.")
    print(f"  Numbers on the diagram or axis 3 is a zero.")
    print(f"  Written to {os.path.relpath(path, ROOT)}")
    print("=" * 70)
    input("\n  Press Enter to start the clock. ")
    t0 = time.time()
    input(f"  ...designing. Press Enter when you stop (target {MINUTES} min). ")
    mins = (time.time() - t0) / 60.0

    print(f"\n  {mins:.1f} min ({'over' if mins > MINUTES else 'under'} target).")
    print(f"  Now score it in {os.path.relpath(path, ROOT)} — honestly, against the rubric.")
    print("  Then say the whole design out loud to an empty room and log it as a B11 take:")
    print("     make rehearse S=B11\n")


if __name__ == "__main__":
    main()
