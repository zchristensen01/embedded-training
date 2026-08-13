#!/usr/bin/env python3
"""newkata.py — scaffold a kata module.

  python3 tools/newkata.py ring_buffer
  python3 tools/newkata.py test_harness_py --python

Creates BRIEF.md, VARIANTS.md, NOTES.md, include/<name>.h, tests/test_<name>.c, and an empty
gitignored src/. Existing files are never overwritten.

You fill in the header and the tests. That is the point — writing the contract and the test
suite before the implementation is the thing you get interviewed on. AI may write the runner
and the assert macros; it may not write a single test case.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KATAS = os.path.join(ROOT, "practice", "katas")

BRIEF = """# {name}

> **Before your first rep you owe this module two files:** `include/{name}.h` — the API
> contract — and the suite in `tests/`. Write the header first, then list the cases under
> **What to test** below in your own words, then write every one of them yourself. AI writes
> neither. `make drill` refuses a module whose header and tests do not exist, because a rep
> against an empty suite is not a rep. Both are frozen once written: you do not edit them
> during a rep, only your `src/`, which is deleted each time. See
> [DAILY.md](../../../DAILY.md#build-sessions).

## What it is
TODO: one paragraph. What are you building, in plain terms?

## Why firmware needs it
TODO: two or three sentences. If you can't answer this, you can't answer the interview
question either, and the kata is worth less.

## The API you implement
```c
/* frozen in include/{name}.h — write this FIRST, before any tests */
```

## How to think about it
TODO: the two or three things that are easy to get wrong. Draw the invariant.

## What to test
TODO: list the cases before you write them. Boundaries. Zero. Full. Empty. Overlap.
The n=0 case. The one-element case. Anything an ISR could interleave with.

## Interview questions this lets you answer from experience
TODO: pull the relevant lines from question-bank/embedded-coding.md and
question-bank/embedded-concepts.md. If none map, ask why you're building this.
"""

VARIANTS = """# {name} — variants

Each variant changes a real constraint, not just a parameter. Every shipped module has seven,
and `make check-calendar` fails if the rotation names one that is not written here. Four is
enough to start drilling; add the rest as you find the edges.

v1  TODO: the simplest correct version.
v2  TODO: change the data structure or the full/empty scheme.
v3  TODO: change the performance constraint.
v4  TODO: make it safe against an ISR, or against a second thread.
"""

NOTES = """# {name} — notes

One line per rep: a design decision you made, or a bug you hit. Appended by `make done`.
This file is where the learning actually accumulates, since the code is deleted each time.
"""

HEADER_C = """#ifndef {guard}
#define {guard}

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* The API contract. FROZEN once you start doing reps — you do not edit this
 * during a drill. Write it deliberately now; you will live with it for weeks.
 *
 * TODO: declare the types and functions. Think about:
 *   - what the caller owns vs what this module owns
 *   - what the return value means on failure
 *   - whether any of it must be safe to call from an ISR
 */

#endif /* {guard} */
"""

TEST_C = """/* tests/test_{name}.c — FROZEN. You do not edit this during a drill.
 *
 * Write these cases yourself. Every one. AI may write the runner below this line
 * and the assert macros; it may not write a case. "How would you test this" is a
 * top-three interview question in both tracks, and this file is your answer.
 */
#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "{name}.h"

static int failures = 0;

#define CHECK(cond)                                                            \\
    do {{                                                                       \\
        if (!(cond)) {{                                                         \\
            printf("FAIL %s:%d  %s\\n", __FILE__, __LINE__, #cond);             \\
            failures++;                                                        \\
        }}                                                                       \\
    }} while (0)

/* TODO: one function per case. Name them so a failure tells you what broke. */

static void test_TODO_rename_me(void)
{{
    CHECK(0 && "write a real case");
}}

int main(void)
{{
    test_TODO_rename_me();

    if (failures == 0) {{
        printf("ok: all cases passed\\n");
        return 0;
    }}
    printf("%d failure(s)\\n", failures);
    return 1;
}}
"""

TEST_PY = '''"""tests/test_{name}.py — FROZEN. Not edited during a drill.

Write every case yourself. AI may write fixtures plumbing; it may not write a case.
"""
import pytest


# TODO: a fixture that builds the thing under test and tears it down even on failure.
@pytest.fixture
def subject():
    raise NotImplementedError("build the fixture")


def test_TODO_rename_me(subject):
    assert False, "write a real case"
'''


def write(path, text):
    if os.path.exists(path):
        print(f"  skip   {os.path.relpath(path, ROOT)}")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)
    print(f"  create {os.path.relpath(path, ROOT)}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    name = args[0]
    py = "--python" in sys.argv or name.endswith("_py")

    d = os.path.join(KATAS, name)
    print(f"scaffolding katas/{name}/")
    write(os.path.join(d, "BRIEF.md"), BRIEF.format(name=name))
    write(os.path.join(d, "VARIANTS.md"), VARIANTS.format(name=name))
    write(os.path.join(d, "NOTES.md"), NOTES.format(name=name))

    if py:
        write(os.path.join(d, "tests", f"test_{name}.py"), TEST_PY.format(name=name))
    else:
        write(os.path.join(d, "include", f"{name}.h"),
              HEADER_C.format(guard=name.upper() + "_H"))
        write(os.path.join(d, "tests", f"test_{name}.c"), TEST_C.format(name=name))

    os.makedirs(os.path.join(d, "src"), exist_ok=True)
    print(f"\n  Now, in this order:")
    print(f"    1. Write include/{name}.h — the contract. Deliberately.")
    print(f"    2. List the cases in BRIEF.md under 'What to test'.")
    print(f"    3. Write those cases in tests/. Yourself.")
    print(f"    4. Only then: make drill KATA={name}\n")


if __name__ == "__main__":
    main()
