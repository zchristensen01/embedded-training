#!/usr/bin/env python3
"""check_decks.py — validate the spaced-repetition decks against the capability list.

    python3 tools/check_decks.py            validate (CI runs this on every push)
    python3 tools/check_decks.py --summary  what each card is doing, and what is thin

Or via make: `make check-decks` and `make decks`.

The decks are the evidence for most of the E group and most of T. Three things can go
wrong quietly, and all three did:

  1. A card is tagged with a capability ID that does not exist. Nothing noticed; the
     tag simply did nothing.
  2. A capability whose bar is the deck has no card, so it can never be met.
  3. A field contains a stray tab, which shifts every column after it.

None of that is visible from `make review`, which is why it is checked here.

A card tagged with a capability whose bar is NOT the deck — a kata capability, say — is
not an error. It is reinforcement, and `make progress` labels it that way. It just does
not count toward the bar, and you should know which of your cards are in that group.
"""
import glob
import importlib.util
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECKS = os.path.join(ROOT, "practice", "decks")
HEADER = ["# topic", "question", "answer", "trap", "caps"]

# Below this many cards, a capability is resting on a single question and one bad
# session sends it back to box 1. Reported, not failed — it is a judgement call.
THIN = 1


def _progress():
    spec = importlib.util.spec_from_file_location(
        "_progress", os.path.join(ROOT, "tools", "progress.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rows():
    """[(deck, lineno, fields)] for every non-comment, non-blank line."""
    out = []
    for path in sorted(glob.glob(os.path.join(DECKS, "*.tsv"))):
        for i, line in enumerate(open(path), 1):
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            out.append((os.path.basename(path), i, line.split("\t")))
    return out


def check():
    p = _progress()
    caps = p.capabilities()
    own = p.ownership()
    errors, notes = [], []

    decks = sorted(glob.glob(os.path.join(DECKS, "*.tsv")))
    if not decks:
        return [f"no decks found in {os.path.relpath(DECKS, ROOT)}"], []

    for path in decks:
        first = open(path).readline().rstrip("\n").split("\t")
        if first != HEADER:
            errors.append(
                f"{os.path.basename(path)}:1: header must be exactly: "
                f"{chr(9).join(HEADER)}")

    tagged = defaultdict(list)
    for deck, n, f in rows():
        where = f"{deck}:{n}"
        if len(f) != len(HEADER):
            errors.append(
                f"{where}: {len(f)} tab-separated fields, expected {len(HEADER)} "
                f"(topic, question, answer, trap, caps). A stray tab inside a field "
                f"shifts every column after it.")
            continue
        topic, question, answer, trap, capfield = f
        for name, value in (("topic", topic), ("question", question), ("answer", answer)):
            if not value.strip():
                errors.append(f"{where}: {name} is empty")
        if not trap.strip():
            errors.append(
                f"{where}: no trap. A card counts as correct only when you say the "
                f"wrong answer too, so a card without one cannot be scored.")
        ids = [c.strip() for c in capfield.split(",") if c.strip()]
        if not ids:
            notes.append(f"{where}: no capability tagged — it will never count "
                         f"toward anything")
        for cid in ids:
            if cid not in caps:
                errors.append(
                    f"{where}: tagged {cid}, which is not a capability in "
                    f"plan/INTERVIEW_REQUIREMENTS.md")
            else:
                tagged[cid].append(where)

    # Every capability the deck is the bar for needs at least one card, or it can
    # never be met by any amount of practice.
    for cid, rec in sorted(own.items(), key=lambda kv: (kv[0][0], int(kv[0][1:]))):
        if cid not in caps:
            continue
        if p.bar_for(cid, rec["owners"]) != "deck":
            continue
        if cid not in tagged:
            errors.append(
                f"{cid}: its evidence bar is the deck, but no card is tagged with it — "
                f"it can never be met. Add one with `make card`.")

    thin = [cid for cid, rec in own.items()
            if cid in caps and p.bar_for(cid, rec["owners"]) == "deck"
            and len(tagged.get(cid, [])) <= THIN]
    if thin:
        notes.append(f"{len(thin)} capability/capabilities rest on a single card. "
                     f"Not an error — see `make decks` for which.")

    return errors, notes


def summary():
    p = _progress()
    caps, own = p.capabilities(), p.ownership()
    tagged = defaultdict(list)
    total = 0
    for deck, n, f in rows():
        total += 1
        if len(f) < 5:
            continue
        for cid in (c.strip() for c in f[4].split(",") if c.strip()):
            tagged[cid].append(f"{deck}:{n}")

    evidence = reinforcement = untagged = 0
    for deck, n, f in rows():
        ids = [c.strip() for c in f[4].split(",") if c.strip()] if len(f) >= 5 else []
        if not ids:
            untagged += 1
        elif any(cid in own and p.bar_for(cid, own[cid]["owners"]) == "deck" for cid in ids):
            evidence += 1
        else:
            reinforcement += 1

    print(f"\n  {total} cards.  {evidence} are evidence for a capability, "
          f"{reinforcement} are reinforcement for a capability scored elsewhere, "
          f"{untagged} untagged.\n")
    print("  Capabilities whose bar is the deck:\n")
    for cid, rec in sorted(own.items(), key=lambda kv: (kv[0][0], int(kv[0][1:]))):
        if cid not in caps or p.bar_for(cid, rec["owners"]) != "deck":
            continue
        n = len(tagged.get(cid, []))
        mark = "  thin" if n <= THIN else ""
        print(f"    {cid:<5} {n} card(s){mark}   {caps[cid][:58]}")
    print("\n  Reinforcement cards (real practice, but not the bar):\n")
    for cid in sorted(tagged, key=lambda c: (c[0], int(c[1:]))):
        if cid not in own or p.bar_for(cid, own[cid]["owners"]) == "deck":
            continue
        bar = p.bar_for(cid, own[cid]["owners"])
        print(f"    {cid:<5} {len(tagged[cid])} card(s)   bar is: {bar}")
    print()


def main():
    if "--summary" in sys.argv:
        summary()
        return 0
    errors, notes = check()
    for n in notes:
        print(f"note: {n}")
    if errors:
        print()
        for e in errors:
            print(e, file=sys.stderr)
        print(f"\n{len(errors)} problem(s) in practice/decks/", file=sys.stderr)
        return 1
    print(f"decks ok — every tag names a real capability, and every deck-scored "
          f"capability has a card")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
