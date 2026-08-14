#!/usr/bin/env python3
"""review.py — spaced repetition over decks/*.tsv.

  python3 tools/review.py            review whatever is due (default 20 cards)
  python3 tools/review.py 30         review 30 cards
  python3 tools/review.py --topic interrupts
  python3 tools/review.py --stats

Deck format, tab separated:  topic <TAB> question <TAB> answer <TAB> trap

Five Leitner boxes. Box N is due every 2^(N-1) days: 1, 2, 4, 8, 16.

Two rules that make this work:
  1. Say the answer OUT LOUD, in full sentences, before you reveal.
  2. A card is only correct if you also said the trap. Knowing the right answer is table
     stakes; naming the wrong one is what sounds like expertise.
"""
import glob
import json
import os
import random
import sys
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECKS = os.path.join(ROOT, "practice", "decks")
STATE = os.path.join(DECKS, ".state.json")
INTERVALS = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}


def load_cards():
    cards = []
    for path in sorted(glob.glob(os.path.join(DECKS, "*.tsv"))):
        with open(path) as fh:
            for i, line in enumerate(fh):
                line = line.rstrip("\n")
                if not line.strip() or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) < 3:
                    continue
                topic, q, a = parts[0], parts[1], parts[2]
                trap = parts[3] if len(parts) > 3 else ""
                cards.append({
                    "id": f"{os.path.basename(path)}:{i}",
                    "topic": topic, "q": q, "a": a, "trap": trap,
                })
    return cards


def load_state():
    if os.path.exists(STATE):
        with open(STATE) as fh:
            return json.load(fh)
    return {}


def save_state(st):
    os.makedirs(DECKS, exist_ok=True)
    with open(STATE, "w") as fh:
        json.dump(st, fh, indent=0)


def due(card, st):
    rec = st.get(card["id"])
    if not rec:
        return True
    try:
        last = datetime.strptime(rec["last"], "%Y-%m-%d").date()
    except (ValueError, KeyError):
        return True
    return date.today() >= last + timedelta(days=INTERVALS.get(rec.get("box", 1), 1))


def render(field, indent="  "):
    r"""Expand the literal two-character sequence \n into real newlines, indented.

    A deck card is one TSV line, so a card that carries a code snippet — "what does this
    print, and why" — has to escape its newlines. Y1's evidence bar is predicting the
    output of an unseen snippet cold, and that is not a question you can pose on one line.
    Cards without a \n are unaffected.
    """
    parts = field.split("\\n")
    return ("\n" + indent).join(parts)


def stats(cards, st):
    boxes = {b: 0 for b in range(1, 6)}
    unseen = 0
    for c in cards:
        rec = st.get(c["id"])
        if not rec:
            unseen += 1
        else:
            boxes[rec.get("box", 1)] = boxes.get(rec.get("box", 1), 0) + 1
    print(f"\n{len(cards)} cards. {unseen} never seen.")
    for b in range(1, 6):
        bar = "#" * boxes[b]
        print(f"  box {b} (every {INTERVALS[b]:>2}d): {boxes[b]:>3} {bar}")
    print("\nMost cards stuck in boxes 1-2 after a few weeks usually means")
    print("you're reviewing silently, or not saying the trap. Fix the method.\n")


def main():
    args = sys.argv[1:]
    cards = load_cards()
    st = load_state()

    if not cards:
        sys.exit(f"No cards found in {DECKS}/*.tsv")

    if "--stats" in args:
        stats(cards, st)
        return

    topic = None
    if "--topic" in args:
        topic = args[args.index("--topic") + 1].lower()
        matched = [c for c in cards if topic in c["topic"].lower()]
        # A topic no card carries is not the same fact as a topic with nothing due, and
        # reporting both as "Nothing due" made a typo — or a stale name off the calendar's
        # weekly focus — read as "you have finished this one".
        if not matched:
            known = sorted({c["topic"] for c in cards})
            sys.exit(f"No card carries the topic '{topic}'.\n"
                     f"Topics in the decks: {', '.join(known)}")
        cards = matched

    limit = 20
    for a in args:
        if a.isdigit():
            limit = int(a)

    pool = [c for c in cards if due(c, st)]
    if not pool:
        print("Nothing due. Run with --stats to see the schedule.")
        return
    random.shuffle(pool)
    pool = pool[:limit]

    print(f"\n{len(pool)} cards due. Answer OUT LOUD before revealing.")
    print("A card is correct only if you also said the trap.\n")

    right = 0
    for i, c in enumerate(pool, 1):
        print("=" * 66)
        print(f"[{i}/{len(pool)}] ({c['topic']})")
        print(f"\n  {render(c['q'])}\n")
        input("  ...say it out loud, then press Enter. ")
        print(f"\n  ANSWER: {render(c['a'], indent='          ')}")
        if c["trap"]:
            print(f"  TRAP:   {render(c['trap'], indent='          ')}")
        v = input("\n  Did you say all of it? [y/N]: ").strip().lower()
        ok = v in ("y", "yes")
        right += ok
        rec = st.get(c["id"], {"box": 1})
        box = rec.get("box", 1)
        rec["box"] = min(5, box + 1) if ok else 1
        rec["last"] = date.today().isoformat()
        st[c["id"]] = rec
        print()

    save_state(st)
    pct = round(100 * right / len(pool))
    print("=" * 66)
    print(f"{right}/{len(pool)} ({pct}%).")
    if pct < 60:
        print("Below 60% means these are new to you, not that you're failing. Come back tomorrow.")


if __name__ == "__main__":
    main()
