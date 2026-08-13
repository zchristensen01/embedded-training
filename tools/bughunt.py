#!/usr/bin/env python3
"""bughunt.py — find a bug in code you didn't write. Using your own code.

  python3 tools/bughunt.py              pick a snapshot, break it, start the clock
  python3 tools/bughunt.py start fsm    break that module specifically
  python3 tools/bughunt.py done         stop the clock, reveal the mutation, log it
  python3 tools/bughunt.py --list       which modules have a snapshot to hunt in
  python3 tools/bughunt.py --stats      your hunt history

Or via make: `make hunt`, `make hunt-done`, `make hunts`.

WHY THIS EXISTS
---------------
The research says take-homes hand you a codebase — Tesla's is reported to include
"debugging existing code" — but every other mechanism in this repo starts from an empty
editor. That gap could not be closed by writing a corpus of broken C, because the repo's
rule is that AI does not write the things you get interviewed on. An AI-written bug is an
AI-written exercise.

So the bug comes from somewhere else: a machine breaks YOUR code, mechanically.

`make done` snapshots your passing implementation into logs/.snapshots/ (gitignored, like
src/). `make hunt` takes a snapshot from a previous rep, applies exactly one mutation from
the table below, checks that the mutant still compiles but now FAILS the suite, and drops
it into src/ with the clock running. You run `make test`, read the failure, and find it.

Three properties that make this a real exercise rather than a toy:

  - The code is yours, so nothing about it is unfamiliar in an unfair way — but a rep from
    three weeks ago is genuinely code you did not write today.
  - The bug is a single-token change of the kind that actually ships: an off-by-one, a
    flipped comparison, a dropped volatile. Not a contrived puzzle.
  - You have the failing test before you have the cause, which is the real-world order and
    the opposite of how the katas work.

This is standard mutation testing pointed at the human instead of at the suite. Ordinarily
a surviving mutant means the tests are weak; here a mutant you cannot find quickly means
the debugging is weak. Both readings are useful, and `make hunt-done` records which
happened.
"""
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KATAS = os.path.join(ROOT, "practice", "katas")
SNAPS = os.path.join(ROOT, "logs", ".snapshots")
STATE = os.path.join(ROOT, "logs", ".bughunt_state.json")
LOG = os.path.join(ROOT, "logs", "bughunt.tsv")

# How long a hunt should take before you look at it as a finding rather than a rep. Not a
# hard stop — the point is that a five-minute hunt and a forty-minute hunt mean different
# things about the same bug.
TARGET_MIN = 10

# Each entry is (name, pattern, replacement, description-for-the-reveal). They are applied
# to one randomly chosen eligible line, and the result must compile AND fail the suite or
# it is discarded and another is tried. Order does not matter; selection is random.
MUTATIONS = [
    ("relational", r"(?<![<>=!])<(?![<=])", "<=", "a strict < became <="),
    ("relational", r"<=", "<", "a <= became a strict <"),
    ("relational", r"(?<![<>=!])>(?![>=])", ">=", "a strict > became >="),
    ("relational", r">=", ">", "a >= became a strict >"),
    ("equality", r"==", "!=", "an == became !="),
    ("equality", r"!=", "==", "a != became =="),
    ("logical", r"&&", "||", "an && became ||"),
    ("logical", r"\|\|", "&&", "an || became &&"),
    ("arithmetic", r"(?<![+\-*/=<>!&|^ ])\+(?![+=])", "-", "a + became -"),
    ("arithmetic", r"(?<![+\-*/=<>!&|^ ])-(?![-=>])", "+", "a - became +"),
    ("stepping", r"\+\+", "--", "an ++ became --"),
    ("stepping", r"--", "++", "a -- became ++"),
    ("bitwise", r"(?<![&|])&(?![&=])", "|", "a bitwise & became |"),
    ("bitwise", r"(?<![&|])\|(?![|=])", "&", "a bitwise | became &"),
    ("shift", r"<<(?!=)", ">>", "a << became >>"),
    ("shift", r">>(?!=)", "<<", "a >> became <<"),
    ("off-by-one", r"\b(\d+)\b", None, "a numeric literal moved by one"),
    ("volatile", r"\bvolatile\s+", "", "a volatile qualifier was deleted"),
    ("assignment", r"(?<![+\-*/%&|^!<>=])=(?!=)", "==",
     "an assignment became a comparison"),
]

# Never touch these. Mutating an include guard or a header path produces a build error, not
# a bug, and mutating the license line is just noise.
SKIP_LINE = re.compile(r"^\s*(#include|#ifndef|#define|#endif|//|/\*|\*)")


def snapshots():
    """{kata: [(path, date, variant)]}, newest last."""
    out = {}
    if not os.path.isdir(SNAPS):
        return out
    for kata in sorted(os.listdir(SNAPS)):
        d = os.path.join(SNAPS, kata)
        if not os.path.isdir(d):
            continue
        rows = []
        for f in sorted(os.listdir(d)):
            m = re.match(r"^(\d{4}-\d{2}-\d{2})-(v\d+)\.(c|py)$", f)
            if m:
                rows.append((os.path.join(d, f), m.group(1), m.group(2)))
        if rows:
            out[kata] = rows
    return out


def save_snapshot(kata, variant, src_dir):
    """Called by drill.py at `make done`. Keeps the newest few reps per kata."""
    files = [f for f in sorted(os.listdir(src_dir))] if os.path.isdir(src_dir) else []
    files = [f for f in files if f.endswith((".c", ".py"))]
    if len(files) != 1:
        return None          # multi-file implementations are out of scope for now
    ext = files[0].rsplit(".", 1)[1]
    d = os.path.join(SNAPS, kata)
    os.makedirs(d, exist_ok=True)
    dest = os.path.join(d, f"{date.today().isoformat()}-{variant}.{ext}")
    shutil.copyfile(os.path.join(src_dir, files[0]), dest)
    keep = sorted(os.listdir(d))[-6:]
    for f in os.listdir(d):
        if f not in keep:
            os.remove(os.path.join(d, f))
    return dest


def run_tests(kata):
    """(ok, output). Uses the same make target you would run yourself."""
    p = subprocess.run(["make", "test", f"MODULE={kata}"], cwd=ROOT,
                       capture_output=True, text=True)
    return p.returncode == 0, p.stdout + p.stderr


def eligible_lines(text):
    lines = text.split("\n")
    return [i for i, l in enumerate(lines)
            if l.strip() and not SKIP_LINE.match(l) and not l.strip().startswith("*")]


def strip_literals(line):
    """Blank out string and char literals so we never mutate inside one."""
    return re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                  lambda m: " " * len(m.group(0)), line)


def mutate_once(text, rng):
    """Return (new_text, record) or None if nothing could be mutated."""
    lines = text.split("\n")
    candidates = []
    for i in eligible_lines(text):
        masked = strip_literals(lines[i])
        for name, pat, rep, desc in MUTATIONS:
            for m in re.finditer(pat, masked):
                candidates.append((i, m.start(), m.end(), name, rep, desc, m.group(0)))
    if not candidates:
        return None
    i, a, b, name, rep, desc, got = rng.choice(candidates)
    if name == "off-by-one":
        n = int(got)
        rep = str(n + rng.choice([-1, 1])) if n > 0 else "1"
    original = lines[i]
    lines[i] = original[:a] + rep + original[b:]
    return "\n".join(lines), {
        "line": i + 1, "kind": name, "what": desc,
        "before": original.rstrip(), "after": lines[i].rstrip(),
    }


def cmd_start(argv):
    snaps = snapshots()
    if not snaps:
        sys.exit(
            "No snapshots yet, so there is nothing to break.\n\n"
            "A snapshot is saved automatically by `make done` whenever a rep leaves a\n"
            "single working source file behind. Do a few reps first, then come back —\n"
            "hunting in code you wrote this morning is not the exercise. Give it a week."
        )
    kata = argv[0] if argv else None
    if kata and kata not in snaps:
        sys.exit(f"No snapshot for {kata}. Have: {', '.join(sorted(snaps))}")

    rng = random.Random()
    # Prefer the oldest snapshot you have not hunted recently: the whole point is that the
    # code should feel unfamiliar. Hunting this morning's rep is a memory test.
    if not kata:
        hunted = {r["module"] for r in read_log()[-5:]}
        pool = [k for k in snaps if k not in hunted] or list(snaps)
        kata = rng.choice(sorted(pool))
    path, snap_date, variant = snaps[kata][0]      # oldest kept snapshot
    age = (date.today() - datetime.strptime(snap_date, "%Y-%m-%d").date()).days

    src = os.path.join(KATAS, kata, "src")
    os.makedirs(src, exist_ok=True)
    for f in os.listdir(src):
        os.remove(os.path.join(src, f))
    fname = f"{kata}.{path.rsplit('.', 1)[1]}"
    original = open(path).read()

    print(f"\n  Preparing a hunt in {kata} ({variant}, written {snap_date})...")
    shutil.copyfile(path, os.path.join(src, fname))
    ok, _ = run_tests(kata)
    if not ok:
        sys.exit(
            f"\n  The snapshot for {kata} does not pass its own suite any more.\n"
            f"  That usually means the frozen tests changed after the snapshot was taken.\n"
            f"  Do a fresh rep of {kata} and the next snapshot will be usable."
        )

    for attempt in range(40):
        result = mutate_once(original, rng)
        if not result:
            break
        mutant, record = result
        with open(os.path.join(src, fname), "w") as fh:
            fh.write(mutant)
        ok, out = run_tests(kata)
        if ok:
            continue                     # equivalent mutant: the tests can't see it
        if "error:" in out and "FAIL" not in out and "failure" not in out.lower():
            continue                     # it broke the build, which is not a bug hunt
        break
    else:
        sys.exit("  Could not produce a mutation that compiles and fails. Try another module.")

    with open(STATE, "w") as fh:
        json.dump({"kata": kata, "variant": variant, "file": fname,
                   "snapshot": path, "start": time.time(), "record": record}, fh)

    print("=" * 70)
    print(f"  BUG HUNT — {kata}")
    print("=" * 70)
    print(f"  This is your own {variant} implementation from {snap_date}"
          + (f", {age} days ago." if age else "."))
    print(f"  Exactly ONE line has been changed. It compiles. It fails the suite.")
    print()
    print(f"  Your job: `make test MODULE={kata}`, read the failure, find the line.")
    print(f"  Do NOT diff against the snapshot — that is the answer, and looking at it")
    print(f"  is the one thing that makes this worthless.")
    print()
    print(f"  Target: {TARGET_MIN} min to a green suite. Clock is running.")
    print(f"  `make hunt-done` when the tests pass, or when you give up.")
    print("=" * 70)


def read_log():
    rows = []
    if not os.path.exists(LOG):
        return rows
    for line in open(LOG):
        p = line.rstrip("\n").split("\t")
        if len(p) < 5 or p[0] == "date":
            continue
        try:
            rows.append({"date": p[0], "module": p[1], "kind": p[2],
                         "minutes": float(p[3]), "found": p[4].strip() == "y",
                         "note": p[5] if len(p) > 5 else ""})
        except ValueError:
            continue
    return rows


def cmd_done():
    if not os.path.exists(STATE):
        sys.exit("No hunt in progress. Run `make hunt` first.")
    st = json.load(open(STATE))
    minutes = round((time.time() - st["start"]) / 60.0, 1)
    rec = st["record"]

    kata = st["kata"]
    ok, _ = run_tests(kata)

    print(f"\n  {kata} — {minutes} min (target {TARGET_MIN}).")
    print(f"  Suite is {'GREEN' if ok else 'still failing'}.")
    print()
    print("  " + "-" * 66)
    print(f"  The mutation was on line {rec['line']}: {rec['what']}.")
    print(f"    was:  {rec['before'].strip()[:64]}")
    print(f"    became: {rec['after'].strip()[:64]}")
    print("  " + "-" * 66)

    found = input("\n  Did you find that exact line yourself? [y/N]: ").strip().lower()
    found = "y" if found in ("y", "yes") else "n"
    note = input("  One line: what led you to it, or what misled you: ").strip()

    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    new = not os.path.exists(LOG)
    with open(LOG, "a") as fh:
        if new:
            fh.write("date\tmodule\tkind\tminutes\tfound\tnote\n")
        fh.write(f"{date.today().isoformat()}\t{kata}\t{rec['kind']}\t{minutes}\t{found}\t{note}\n")

    os.remove(STATE)
    if found == "y" and minutes <= TARGET_MIN:
        print("\n  Under target and found. That is the shape of a good take-home debrief.\n")
    elif found == "n":
        print("\n  Worth writing down which signal you did not follow. The suite told you")
        print("  something; the question is what you did with it.\n")
    else:
        print("\n  Found it. Where did the time go — reading, or hypothesising?\n")


def cmd_stats():
    rows = read_log()
    if not rows:
        print("\n  No hunts logged yet. `make hunt` starts the first one.\n")
        return
    found = sum(1 for r in rows if r["found"])
    print(f"\n  {len(rows)} hunts, {round(100 * found / len(rows))}% found, "
          f"median {sorted(r['minutes'] for r in rows)[len(rows) // 2]:g} min.\n")
    by_kind = {}
    for r in rows:
        k = by_kind.setdefault(r["kind"], [0, 0])
        k[0] += 1
        k[1] += r["found"]
    print("  Which mutation kinds catch you out:\n")
    for kind, (n, f) in sorted(by_kind.items(), key=lambda kv: kv[1][1] / kv[1][0]):
        print(f"    {kind:<12} {f}/{n} found")
    print("\n  The kinds at the top are your blind spots. They are also, not by")
    print("  coincidence, the bugs you are most likely to write.\n")


def cmd_list():
    snaps = snapshots()
    if not snaps:
        print("\n  No snapshots yet. They are saved automatically by `make done`.\n")
        return
    print("\n  Snapshots available to hunt in:\n")
    for kata, rows in sorted(snaps.items()):
        dates = ", ".join(f"{d} {v}" for _, d, v in rows)
        print(f"    {kata:<18} {dates}")
    print("\n  `make hunt` picks the oldest one you have not hunted recently.\n")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--list" in args:
        cmd_list()
    elif "--stats" in args:
        cmd_stats()
    elif args and args[0] == "done":
        cmd_done()
    else:
        cmd_start([a for a in (args[1:] if args and args[0] == "start" else args)
                   if not a.startswith("-")])
