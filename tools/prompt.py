#!/usr/bin/env python3
"""prompt.py — draw a design prompt, start a 10-minute timer, open a scored answer file.

Subjects come from the "## Subjects" section of practice/design-prompts/SUBJECTS.md and
nowhere else. That file also carries a second numbered list — the "explain your design"
prompts, which are a different exercise — and an earlier version of this script matched
both, so `make prompt` could hand you "How would you test: Walk me through your ring
buffer." The section boundary below is what stops that.
"""
import os
import random
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "practice", "design-prompts", "SUBJECTS.md")
OUT = os.path.join(ROOT, "logs", "design-prompts")

SUBJECTS_HEADING = "## Subjects"

RUBRIC = """
| # | Criterion | Score 0-2 |
|---|---|---|
| 1 | Asked for requirements FIRST | |
| 2 | Functional / happy path | |
| 3 | Boundary conditions | |
| 4 | Negative and out-of-range | |
| 5 | Environmental | |
| 6 | Electrical and power | |
| 7 | Reliability and life | |
| 8 | Safety, usability, misuse | |
| + | Bonus: named what to automate and what not to | |

**Total: __ / 16**

Fill the total in. `make progress` reads this line, and T1 is met on the score rather
than on the number of files — ten unscored answers prove nothing.

Automatic fail if: you proposed solutions before asking for requirements, or you stopped
before being told to stop.
"""


def subjects():
    """The numbered list under '## Subjects', stopping at the next heading."""
    text = open(SRC).read()
    start = text.find(SUBJECTS_HEADING)
    if start < 0:
        sys.exit(f"No '{SUBJECTS_HEADING}' heading in {os.path.relpath(SRC, ROOT)}")
    body = text[start + len(SUBJECTS_HEADING):]
    end = re.search(r"^##\s", body, re.M)
    if end:
        body = body[:end.start()]
    found = re.findall(r"^\d+\.\s+(.+?)\s*(?:\*\(.*)?$", body, re.M)
    return [s.strip() for s in found if s.strip()]


def main():
    subs = subjects()
    if not subs:
        sys.exit(f"No subjects parsed from {os.path.relpath(SRC, ROOT)}")

    subject = random.choice(subs)
    slug = re.sub(r"[^a-z0-9]+", "-", subject.lower()).strip("-")
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{date.today().isoformat()}-{slug}.md")

    if os.path.exists(path):
        # Same subject twice in one day. Give it its own file rather than silently
        # reopening the first one, or `make prompt x3` writes one answer and counts one.
        n = 2
        while os.path.exists(os.path.join(OUT, f"{date.today().isoformat()}-{slug}-{n}.md")):
            n += 1
        path = os.path.join(OUT, f"{date.today().isoformat()}-{slug}-{n}.md")

    with open(path, "w") as fh:
        fh.write(f"# How would you test: {subject}\n\n"
                 f"Date: {date.today().isoformat()}  ·  10 minutes  ·  write, then say it aloud\n\n"
                 f"## My answer\n\n\n\n## Score\n{RUBRIC}\n## What I missed\n\n")

    print("\n" + "=" * 66)
    print(f"  HOW WOULD YOU TEST:  {subject}")
    print("=" * 66)
    print(f"  10 minutes. Ask for requirements first. Do not stop early.")
    print(f"  One of {len(subs)} subjects.")
    print(f"  Write into: logs/design-prompts/{os.path.basename(path)}")
    print("  Then score yourself against the rubric already in the file, and fill in")
    print("  the total — an unscored answer does not count toward T1.")
    print("=" * 66 + "\n")


if __name__ == "__main__":
    main()
