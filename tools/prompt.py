#!/usr/bin/env python3
"""prompt.py — draw a design prompt, start a 10-minute timer, open a scored answer file."""
import os, random, re, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "practice", "design-prompts", "SUBJECTS.md")
OUT = os.path.join(ROOT, "logs", "design-prompts")

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

Automatic fail if: you proposed solutions before asking for requirements, or you stopped
before being told to stop.
"""

with open(SRC) as fh:
    text = fh.read()
subjects = re.findall(r"^\d+\.\s+(.+?)\s*(?:\*\(.*)?$", text, re.M)
subjects = [s.strip() for s in subjects if s.strip()]
if not subjects:
    sys.exit("No subjects parsed from design-prompts.md")

subject = random.choice(subjects)
slug = re.sub(r"[^a-z0-9]+", "-", subject.lower()).strip("-")
os.makedirs(OUT, exist_ok=True)
path = os.path.join(OUT, f"{date.today().isoformat()}-{slug}.md")

if not os.path.exists(path):
    with open(path, "w") as fh:
        fh.write(f"# How would you test: {subject}\n\n"
                 f"Date: {date.today().isoformat()}  ·  10 minutes  ·  write, then say it aloud\n\n"
                 f"## My answer\n\n\n\n## Score\n{RUBRIC}\n## What I missed\n\n")

print("\n" + "=" * 66)
print(f"  HOW WOULD YOU TEST:  {subject}")
print("=" * 66)
print("  10 minutes. Ask for requirements first. Do not stop early.")
print(f"  Write into: logs/design-prompts/{os.path.basename(path)}")
print("  Then score yourself against the rubric already in the file.")
print("=" * 66 + "\n")
