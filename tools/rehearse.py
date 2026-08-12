#!/usr/bin/env python3
"""rehearse.py — behavioural story takes: draw, time, rate, log.

  python3 tools/rehearse.py            draw the story with fewest strong takes
  python3 tools/rehearse.py B7         a specific story
  python3 tools/rehearse.py --stats    takes per story, best times, what's ready
"""
import os
import re
import sys
import time
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORIES = os.path.join(ROOT, "practice", "rehearsal", "STORIES.md")
LOG = os.path.join(ROOT, "logs", "rehearsal.tsv")

TARGET = {"B1": 60, "B2": 45, "B3": 180, "B4": 120, "B5": 90,
          "B6": 90, "B7": 90, "B8": 90, "B9": 90, "B10": 600}


def load():
    out = []
    if not os.path.exists(STORIES):
        sys.exit(f"Missing {STORIES}")
    for line in open(STORIES):
        m = re.match(r"^## (B\d+) · (.+)$", line.strip())
        if m:
            out.append((m.group(1), m.group(2)))
    return out


def read_log():
    rows = []
    if not os.path.exists(LOG):
        return rows
    for line in open(LOG):
        p = line.rstrip("\n").split("\t")
        if len(p) < 4 or p[0] == "date":
            continue
        try:
            rows.append({"date": p[0], "story": p[1], "seconds": float(p[2]),
                         "rating": int(p[3]), "note": p[4] if len(p) > 4 else ""})
        except ValueError:
            continue
    return rows


def ready(story, rows):
    strong = [r for r in rows if r["story"] == story and r["rating"] == 1]
    return len({r["date"] for r in strong}) >= 3


def stats(stories, rows):
    print(f"\n  {len(rows)} takes logged.\n")
    print(f"  {'':<5}{'story':<42}{'takes':>6}{'best':>8}{'target':>8}  ready")
    for sid, title in stories:
        mine = [r for r in rows if r["story"] == sid]
        best = min((r["seconds"] for r in mine), default=None)
        b = f"{best:.0f}s" if best else "—"
        mark = "yes" if ready(sid, rows) else ""
        print(f"  {sid:<5}{title[:40]:<42}{len(mine):>6}{b:>8}{TARGET[sid]:>7}s  {mark}")
    print("\n  Ready = three takes rated 1 (strong), on three different days.")
    print("  Record yourself every third take. You cannot hear your own filler.\n")


def main():
    args = sys.argv[1:]
    stories = load()
    rows = read_log()

    if "--stats" in args:
        stats(stories, rows)
        return

    pick = None
    if args and re.match(r"^B\d+$", args[0].upper()):
        sid = args[0].upper()
        pick = next((s for s in stories if s[0] == sid), None)
        if not pick:
            sys.exit(f"No story {sid}")
    else:
        scored = sorted(stories, key=lambda s: (
            len([r for r in rows if r["story"] == s[0] and r["rating"] == 1]),
            len([r for r in rows if r["story"] == s[0]])))
        pick = scored[0]

    sid, title = pick
    target = TARGET[sid]
    n = len([r for r in rows if r["story"] == sid]) + 1

    print("\n" + "=" * 66)
    print(f"  {sid} · {title}")
    print(f"  Take {n}.  Target {target}s.")
    print("=" * 66)
    print("  Stand up. No notes. Out loud.")
    if n % 3 == 0:
        print("  >> RECORD THIS ONE. Every third take gets watched back.")
    input("\n  Press Enter to start the clock. ")
    t0 = time.time()
    input("  ...speaking. Press Enter when you finish. ")
    secs = round(time.time() - t0)

    over = secs - target
    verdict = f"{abs(over)}s {'over' if over > 0 else 'under'} target"
    print(f"\n  {secs}s  ({verdict})")
    if over > target * 0.5:
        print("  Long. Usually means too much setup before the point.")

    while True:
        r = input("  Rate it — 1 strong / 2 ok / 3 weak: ").strip()
        if r in ("1", "2", "3"):
            break
    note = input("  One line on what was weak: ").strip()

    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    new = not os.path.exists(LOG)
    with open(LOG, "a") as fh:
        if new:
            fh.write("date\tstory\tseconds\trating\tnote\n")
        fh.write(f"{date.today().isoformat()}\t{sid}\t{secs}\t{r}\t{note}\n")

    rows = read_log()
    if ready(sid, rows):
        print(f"\n  {sid} is READY — three strong takes on three days.")
    print("  Logged.\n")


if __name__ == "__main__":
    main()
