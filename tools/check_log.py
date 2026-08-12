#!/usr/bin/env python3
"""Validate and summarise logs/log.tsv — the practice log.

    python3 tools/check_log.py             validate (CI runs this on every push)
    python3 tools/check_log.py --summary   print the time curve per module

Or via make: `make check-log` and `make log`.

Rows are normally written by `make done`. This exists to catch the ones you add by
hand — Mimic sessions and project hours — and to catch a file that got mangled by an
editor. Nothing here is hardcoded per kata: the module list comes from the directories
under practice/katas/ and the variant list comes from each kata's VARIANTS.md, so
adding a kata or a variant needs no change to this file.
"""

import importlib.util
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "logs" / "log.tsv"
KATAS = ROOT / "practice" / "katas"

HEADER = ["date", "module", "variant", "minutes", "clean", "note"]

# Non-kata modules PRACTICE_SYSTEM.md tells you to log by hand. Their variant field
# is free-form: a Mimic session ID (S0, S1.5) or a project phase.
FREEFORM_MODULES = {"mimic", "project"}

VARIANT_RE = re.compile(r"^(v\d+)\s+")


def targets():
    """Target minutes per kata, taken from drill.py so there's only one copy."""
    spec = importlib.util.spec_from_file_location("_drill", ROOT / "tools" / "drill.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.TARGETS


def katas():
    if not KATAS.is_dir():
        return {}
    found = {}
    for d in sorted(p for p in KATAS.iterdir() if p.is_dir()):
        variants = set()
        vf = d / "VARIANTS.md"
        if vf.exists():
            for line in vf.read_text().splitlines():
                m = VARIANT_RE.match(line.strip())
                if m:
                    variants.add(m.group(1))
        found[d.name] = variants
    return found


def fail(errors):
    for e in errors:
        print(e, file=sys.stderr)
    print(f"\n{len(errors)} problem(s) in logs/log.tsv", file=sys.stderr)
    sys.exit(1)


def parse():
    """Return (rows, errors). A row is a dict; errors are human-readable strings."""
    errors = []
    known = katas()

    if not LOG.exists():
        return [], [f"{LOG} does not exist"]

    raw = LOG.read_bytes()
    if b"\r" in raw:
        errors.append("log.tsv: contains carriage returns — save it with Unix line endings")
    if raw and not raw.endswith(b"\n"):
        errors.append("log.tsv: no trailing newline (an append would join two rows)")

    lines = raw.decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines.pop()

    if not lines:
        return [], ["log.tsv: empty — it needs at least the header row"]

    if lines[0].split("\t") != HEADER:
        errors.append(f"log.tsv:1: header must be exactly: {chr(9).join(HEADER)}")

    rows = []
    prev_date = None

    for n, line in enumerate(lines[1:], start=2):
        where = f"log.tsv:{n}"

        if not line.strip():
            errors.append(f"{where}: blank line — the log is append-only, no gaps")
            continue

        fields = line.split("\t")
        if len(fields) not in (5, 6):
            errors.append(
                f"{where}: has {len(fields)} tab-separated fields, expected 5 or 6 "
                f"(note is optional). Check you used tabs, not spaces."
            )
            continue
        if len(fields) == 5:
            fields.append("")

        d, module, variant, minutes, clean, note = fields

        for name, value in (("date", d), ("module", module), ("variant", variant),
                            ("minutes", minutes), ("clean", clean)):
            if value != value.strip():
                errors.append(f"{where}: {name} '{value}' has leading or trailing whitespace")

        row_date = None
        try:
            row_date = date.fromisoformat(d.strip())
        except ValueError:
            errors.append(f"{where}: date '{d}' is not a valid YYYY-MM-DD")

        if row_date:
            if prev_date and row_date < prev_date:
                errors.append(
                    f"{where}: date {d} is earlier than {prev_date} on the line above — "
                    f"keep rows in date order"
                )
            prev_date = row_date

        module = module.strip()
        variant = variant.strip()

        if module in FREEFORM_MODULES:
            if not variant:
                errors.append(f"{where}: module '{module}' still needs a variant "
                              f"(a Mimic session ID, or the project phase)")
        elif module not in known:
            errors.append(
                f"{where}: unknown module '{module}' — expected a directory under "
                f"practice/katas/ ({', '.join(sorted(known)) or 'none yet'}) "
                f"or one of {', '.join(sorted(FREEFORM_MODULES))}"
            )
        elif known[module] and variant not in known[module]:
            errors.append(
                f"{where}: unknown variant '{variant}' for {module} — expected one of "
                f"{', '.join(sorted(known[module]))} "
                f"(see practice/katas/{module}/VARIANTS.md)"
            )

        # drill.py writes a rounded float, so 0.0 is reachable for an abandoned rep.
        # The validator must not be stricter than the tool that writes the file.
        mins = None
        try:
            mins = float(minutes.strip())
            if mins < 0:
                errors.append(f"{where}: minutes '{minutes}' cannot be negative")
        except ValueError:
            errors.append(f"{where}: minutes '{minutes}' must be a number")

        if clean.strip() not in ("y", "n"):
            errors.append(
                f"{where}: clean '{clean}' must be y or n "
                f"(y = compiled first try under -Werror and both sanitizers stayed silent)"
            )

        if row_date and mins is not None:
            rows.append({
                "date": row_date, "module": module, "variant": variant,
                "minutes": mins, "clean": clean.strip() == "y", "note": note,
            })

    return rows, errors


def summarise(rows):
    if not rows:
        print("logs/log.tsv has no reps yet.\n")
        print("Start one:  make drill        then, when the tests pass:  make done")
        return

    tgt = targets()
    at_target = 0
    kata_rows = [r for r in rows if r["module"] not in FREEFORM_MODULES]

    for module in sorted({r["module"] for r in kata_rows}):
        mine = [r for r in kata_rows if r["module"] == module]
        target = tgt.get(module)
        print(f"{module}" + (f"   (target {target} min)" if target else ""))

        for variant in sorted({r["variant"] for r in mine}):
            sessions = [r for r in mine if r["variant"] == variant]
            curve = " -> ".join(
                f"{s['minutes']:g}{'y' if s['clean'] else 'n'}" for s in sessions
            )
            met = next((s for s in sessions
                        if target and s["minutes"] <= target and s["clean"]), None)
            if met:
                tail = f"  [target met {met['date']}]"
            else:
                cleans = [s["minutes"] for s in sessions if s["clean"]]
                tail = f"  (best clean: {min(cleans):g})" if cleans else "  (never clean yet)"
            print(f"  {variant:<6} {curve}{tail}")

        # Retirement, per PRACTICE_SYSTEM.md: three consecutive clean reps at target
        # across three different variants.
        tail3 = mine[-3:]
        retired = (
            target is not None and len(tail3) == 3
            and all(r["clean"] and r["minutes"] <= target for r in tail3)
            and len({r["variant"] for r in tail3}) == 3
        )
        at_target += retired
        print(f"  {'RETIRED — maintenance rotation' if retired else 'in progress'}\n")

    clean_rate = 100 * sum(r["clean"] for r in kata_rows) / len(kata_rows) if kata_rows else 0
    other = [r for r in rows if r["module"] in FREEFORM_MODULES]
    print(f"{len(kata_rows)} kata rep(s), {rows[0]['date']} to {rows[-1]['date']}   "
          f"clean-first-compile {clean_rate:.0f}%   retired {at_target}")
    if other:
        hours = sum(r["minutes"] for r in other) / 60
        print(f"{len(other)} hand-logged session(s) ({hours:.1f} hr) "
              f"across {', '.join(sorted({r['module'] for r in other}))}")


def main():
    rows, errors = parse()
    if errors:
        fail(errors)

    if "--summary" in sys.argv:
        summarise(rows)
    else:
        print(f"logs/log.tsv ok — {len(rows)} rep(s)")


if __name__ == "__main__":
    main()
