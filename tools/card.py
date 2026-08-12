#!/usr/bin/env python3
"""card.py — add a deck card in about twenty seconds.

  python3 tools/card.py                    interactive
  python3 tools/card.py --deck test-integration
  python3 tools/card.py --topic interrupts        preseed the topic
  python3 tools/card.py --topics                  list topics already in use
  python3 tools/card.py --last 5                  show the most recent cards
  python3 tools/card.py -t interrupts -q "..." -a "..." -x "..."     non-interactive

The 56 cards that ship here cover roughly the E group plus most of T. They do not
cover all 78 capabilities and are not meant to: C is katas, B is rehearsal, and most
of H is Mimic's bench work.

What makes the deck grow correctly is this: every time a rep or a Mimic session
surprises you — something you half-knew, something you got wrong out loud — you add
a card while it still stings. S3's encoder interrupts and S10's anti-windup will
each produce two or three. A card added the same day is worth several added later
from memory, because by then you have forgotten which part actually caught you.

New cards enter the Leitner schedule at box 1 automatically; there is no state to
update. `make review` will show them tomorrow.
"""
import argparse
import difflib
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECKS = os.path.join(ROOT, "practice", "decks")
DRILL_STATE = os.path.join(ROOT, "logs", ".drill_state.json")
HEADER = "# topic\tquestion\tanswer\ttrap\tcaps"


def deck_path(name):
    if not name.endswith(".tsv"):
        name += ".tsv"
    return os.path.join(DECKS, name)


def decks():
    return sorted(os.path.basename(p) for p in glob.glob(os.path.join(DECKS, "*.tsv")))


def read_cards(path=None):
    """[(deck, topic, question, answer, trap)] across one deck or all of them."""
    out = []
    paths = [path] if path else sorted(glob.glob(os.path.join(DECKS, "*.tsv")))
    for p in paths:
        if not os.path.exists(p):
            continue
        with open(p) as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line.strip() or line.startswith("#"):
                    continue
                f = line.split("\t")
                if len(f) < 3:
                    continue
                out.append((os.path.basename(p), f[0], f[1], f[2],
                            f[3] if len(f) > 3 else "",
                            f[4] if len(f) > 4 else ""))
    return out


def topics():
    counts = {}
    for _, topic, _, _, _, _ in read_cards():
        counts[topic] = counts.get(topic, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def current_kata():
    """The kata being drilled right now, if any — the likeliest source of a card."""
    if not os.path.exists(DRILL_STATE):
        return None
    try:
        with open(DRILL_STATE) as fh:
            return json.load(fh).get("kata")
    except (ValueError, OSError):
        return None


def clean(s):
    """One line, no tabs. A tab or newline in a field silently corrupts the deck."""
    return re.sub(r"\s+", " ", s.replace("\t", " ")).strip()


def near_duplicates(question, limit=3):
    existing = read_cards()
    qs = [c[2] for c in existing]
    hits = difflib.get_close_matches(question, qs, n=limit, cutoff=0.72)
    return [c for c in existing if c[2] in hits]


def append(path, topic, q, a, trap, caps=""):
    new_file = not os.path.exists(path)
    if not new_file:
        with open(path, "rb") as fh:
            tail = fh.read()[-1:]
        needs_nl = bool(tail) and tail != b"\n"
    else:
        needs_nl = False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as fh:
        if new_file:
            fh.write(HEADER + "\n")
        if needs_nl:
            fh.write("\n")
        fh.write(f"{topic}\t{q}\t{a}\t{trap}\t{caps}\n")


def ask(prompt, required=True, default=""):
    while True:
        try:
            v = input(prompt).strip()
        except EOFError:
            print()
            sys.exit("cancelled")
        if not v and default:
            return default
        if v or not required:
            return v
        print("    (required)")


def interactive(args):
    known = topics()
    kata = current_kata()

    print()
    print("=" * 66)
    print("  NEW CARD")
    if kata:
        print(f"  mid-rep on {kata} — if this is what just caught you, say so in the question")
    print("=" * 66)
    if known:
        shown = ", ".join(list(known)[:14])
        print(f"  topics in use: {shown}")
        print("  reuse one if it fits — `make review --topic x` only works if they match")
    print()

    topic = clean(args.topic or ask("  topic     : "))
    if known and topic not in known:
        close = difflib.get_close_matches(topic, list(known), n=1, cutoff=0.8)
        if close:
            yn = input(f"  '{close[0]}' already exists. Use that instead? [Y/n]: ").strip().lower()
            if yn in ("", "y", "yes"):
                topic = close[0]

    question = clean(ask("  question  : "))
    dupes = near_duplicates(question)
    if dupes:
        print("\n  Similar cards already exist:")
        for d in dupes:
            print(f"    [{d[1]}] {d[2]}")
        yn = input("\n  Add anyway? [y/N]: ").strip().lower()
        if yn not in ("y", "yes"):
            sys.exit("  not added")

    answer = clean(ask("  answer    : "))

    print()
    print("  The trap is the wrong answer an interviewer expects to hear. A card counts")
    print("  as correct only when you say this part too, so a card without one is worth")
    print("  much less than a card with one.")
    trap = clean(ask("  trap      : ", required=False))
    if not trap:
        yn = input("  No trap. Add it anyway? [y/N]: ").strip().lower()
        if yn not in ("y", "yes"):
            sys.exit("  not added — come back when you can name the wrong answer")

    print()
    print("  Which capability does this prove? An ID from plan/INTERVIEW_REQUIREMENTS.md")
    print("  (E12, T3, C6 ...), comma-separated if more than one. Blank is allowed, but a")
    print("  tagged card is one make progress can count toward a capability being done.")
    caps = clean(ask("  capability: ", required=False))

    return topic, question, answer, trap, caps


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--deck", "-d", default="embedded")
    ap.add_argument("--topic", "-t")
    ap.add_argument("--question", "-q")
    ap.add_argument("--answer", "-a")
    ap.add_argument("--trap", "-x")
    ap.add_argument("--caps", "-c", help="capability IDs this card proves, e.g. E12 or T3,T21")
    ap.add_argument("--topics", action="store_true")
    ap.add_argument("--last", type=int, nargs="?", const=5)
    ap.add_argument("--help", "-h", action="store_true")
    args = ap.parse_args()

    if args.help:
        print(__doc__)
        return

    if args.topics:
        for topic, n in topics().items():
            print(f"  {n:>3}  {topic}")
        return

    if args.last:
        # The decks are append-only and carry no timestamps, so "most recent" means
        # the tail of each file. Taking the tail of all decks concatenated would just
        # show whichever deck sorts last, which is not the same thing.
        for name in decks():
            tail = read_cards(deck_path(name))[-args.last:]
            if not tail:
                continue
            print(f"\n  ── {name}")
            for _, topic, q, a, trap, caps in tail:
                print(f"\n  [{topic}]  {caps or '(no capability tagged)'}"
                      f"\n    Q {q}\n    A {a}\n    trap: {trap or '—'}")
        print()
        return

    path = deck_path(args.deck)
    if not os.path.exists(path):
        sys.exit(f"No deck {os.path.basename(path)}. Have: {', '.join(decks())}")

    if args.question and args.answer:
        topic = clean(args.topic or "misc")
        q, a, trap = clean(args.question), clean(args.answer), clean(args.trap or "")
        caps = clean(args.caps or "")
    else:
        topic, q, a, trap, caps = interactive(args)

    append(path, topic, q, a, trap, caps)
    total = len(read_cards())
    print(f"\n  Added to {os.path.basename(path)}. {total} cards. Due in tomorrow's review.\n")


if __name__ == "__main__":
    main()
