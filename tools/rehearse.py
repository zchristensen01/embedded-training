#!/usr/bin/env python3
"""rehearse.py — behavioural story takes: draw, time, rate, log.

  python3 tools/rehearse.py            draw the story with fewest strong takes
  python3 tools/rehearse.py B7         a specific story
  python3 tools/rehearse.py --stats    takes per story, best times, what's ready

The stories and their target times both come from practice/rehearsal/STORIES.md.
Nothing about the B group is hardcoded here, so adding a story needs no code change.

`ready()` is the single definition of a finished story, and `make progress` imports it
from this file rather than keeping a second opinion about what "three takes" means.
"""
import os
import re
import sys
import time
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORIES = os.path.join(ROOT, "practice", "rehearsal", "STORIES.md")
LOG = os.path.join(ROOT, "logs", "rehearsal.tsv")

STRONG = 1          # the rating that counts
STRONG_DAYS = 3     # ...on this many different days
DEFAULT_TARGET = 90

HEAD_RE = re.compile(r"^## (B\d+) · (.+)$")
TARGET_RE = re.compile(r"Target:\s*(\d+)\s*(second|minute)", re.I)


def load():
    """[(id, title, target_seconds)] in file order, from STORIES.md."""
    if not os.path.exists(STORIES):
        sys.exit(f"Missing {STORIES}")
    out, pending = [], None
    for line in open(STORIES):
        m = HEAD_RE.match(line.strip())
        if m:
            if pending:
                out.append(pending + (DEFAULT_TARGET,))
            pending = (m.group(1), m.group(2))
            continue
        if pending:
            t = TARGET_RE.search(line)
            if t:
                secs = int(t.group(1)) * (60 if t.group(2).lower() == "minute" else 1)
                out.append(pending + (secs,))
                pending = None
    if pending:
        out.append(pending + (DEFAULT_TARGET,))
    return out


def targets():
    return {sid: secs for sid, _, secs in load()}


def read_log():
    rows = []
    if not os.path.exists(LOG):
        return rows
    for line in open(LOG):
        p = line.rstrip("\n").split("\t")
        if len(p) < 4 or p[0] == "date":
            continue
        try:
            rows.append({"date": p[0], "story": p[1].strip(), "seconds": float(p[2]),
                         "rating": int(p[3]), "note": p[4] if len(p) > 4 else ""})
        except ValueError:
            continue
    return rows


def ready(story, rows):
    """Three takes rated strong, on three different days. The bar, in one place.

    Three takes in one afternoon is one rehearsal, not three — the point of the B
    group is that the story survives a gap. `make progress` calls this function.
    """
    strong = [r for r in rows if r["story"] == story and r["rating"] == STRONG]
    return len({r["date"] for r in strong}) >= STRONG_DAYS


def stats(stories, rows):
    print(f"\n  {len(rows)} takes logged.\n")
    print(f"  {'':<5}{'story':<42}{'takes':>6}{'strong days':>13}{'best':>8}{'target':>8}  ready")
    for sid, title, target in stories:
        mine = [r for r in rows if r["story"] == sid]
        days = len({r["date"] for r in mine if r["rating"] == STRONG})
        best = min((r["seconds"] for r in mine), default=None)
        b = f"{best:.0f}s" if best else "—"
        mark = "yes" if ready(sid, rows) else ""
        print(f"  {sid:<5}{title[:40]:<42}{len(mine):>6}{days:>13}{b:>8}"
              f"{target:>7}s  {mark}")
    print(f"\n  Ready = {STRONG_DAYS} takes rated {STRONG} (strong), on "
          f"{STRONG_DAYS} different days.")
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
            len({r["date"] for r in rows if r["story"] == s[0] and r["rating"] == STRONG}),
            len([r for r in rows if r["story"] == s[0]])))
        pick = scored[0]

    sid, title, target = pick
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
        print(f"\n  {sid} is READY — {STRONG_DAYS} strong takes on "
              f"{STRONG_DAYS} different days.")
    print("  Logged.\n")


if __name__ == "__main__":
    main()
