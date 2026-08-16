#!/usr/bin/env python3
"""check_frozen_py.py — prove every frozen Python suite is valid and collectable.

    python3 tools/check_frozen_py.py        (CI runs this on every push)

Or via make: `make check-frozen-py`.

THE PROBLEM THIS SOLVES
-----------------------
`practice/katas/*/src/` is gitignored and deleted at the start of every rep, so on a
fresh clone — and in CI, always — there is no implementation to import. The C side does
not care: `$(CC) -c` compiles a test file against the *header* and only the link step
needs an implementation, so `make check-frozen` proves something real about a suite that
cannot be run.

Python has no such split. `pytest --collect-only` **imports** the test module, which
imports the implementation, so the obvious analogue fails the moment a suite says
`import log_parser_py` at the top:

    E   ModuleNotFoundError: No module named 'log_parser_py'

The old recipe put `src/` on PYTHONPATH and collected. That passed only while every
suite was still the scaffolded stub, which imports nothing but pytest. The first real
suite written in the prep week would have turned CI red and kept it red.

WHAT THIS DOES INSTEAD
----------------------
It supplies the missing half of the analogy. Before collecting, it reads each suite's
imports, works out which of them are not importable — the kata's own module, normally —
and generates a permissive stand-in for each in a temporary directory. Then it collects
against that.

So the C and Python checks now prove the same thing: **the frozen suite is valid against
a contract, independent of any implementation.** For C the contract is the header. For
Python there is no header — `plan/COVERAGE.md` says the contract is the API in the BRIEF
and the suite is what enforces it — so the stand-in is what stands where the header
stands. Nothing here ever looks at `src/`, which also means the check gives the same
answer in the middle of a rep as it does on a clean tree.

WHAT IT CANNOT PROVE
--------------------
That the suite is *correct*, or that its cases are real. A stand-in answers to anything,
so a suite collects here whether or not the implementation could ever satisfy it. That
is the same limit the C check has, for the same reason: `-c` says the suite is valid C,
not that it passes. `make test` is what says it passes.
"""
import ast
import glob
import importlib.util
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KATAS = os.path.join(ROOT, "practice", "katas")

# A stand-in that answers to anything, so the shape of the import in the suite does not
# constrain what the check can handle. `import x`, `from x import y`, subclassing y,
# instantiating it, reading a constant off it, iterating it and using it as a context
# manager all work — which covers every way a frozen suite has any business touching its
# subject at module scope.
#
# The metaclass is doing real work: without it, class-level attribute access
# (`Frame.MAX_LEN`) misses, because a class's attribute lookup does not go through the
# instance `__getattr__` below it.
STUB = '''"""Generated stand-in for `{name}` — written by tools/check_frozen_py.py.

Not part of the repo and never written into it. This exists for the length of one check
so a frozen suite can be imported without an implementation, the way a C test file is
compiled against a header without being linked. See the module docstring in
tools/check_frozen_py.py.
"""


class _Meta(type):
    def __getattr__(cls, name):
        return _stand_in(name)

    def __iter__(cls):
        return iter(())


class _Anything(metaclass=_Meta):
    def __init__(self, *a, **k):
        pass

    def __call__(self, *a, **k):
        return _Anything()

    def __getattr__(self, name):
        return _stand_in(name)

    def __iter__(self):
        return iter(())

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _stand_in(name):
    return _Meta(name, (_Anything,), {{}})


def __getattr__(name):
    return _stand_in(name)
'''


def suites():
    """{kata: [test file, ...]} for every kata carrying a Python suite."""
    out = {}
    if not os.path.isdir(KATAS):
        return out
    for kata in sorted(os.listdir(KATAS)):
        files = sorted(glob.glob(os.path.join(KATAS, kata, "tests", "*.py")))
        if files:
            out[kata] = files
    return out


def imported_names(path):
    """Top-level module names a file imports. Syntax errors propagate to the caller."""
    tree = ast.parse(open(path).read(), filename=path)
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                names.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            # level > 0 is a relative import — it resolves inside tests/, not against
            # an implementation, so there is nothing to stand in for.
            if node.level == 0 and node.module:
                names.add(node.module.split(".")[0])
    return names


def unresolvable(names):
    """The subset that cannot be imported as things stand — what needs a stand-in."""
    missing = set()
    for name in sorted(names):
        try:
            if importlib.util.find_spec(name) is None:
                missing.add(name)
        except (ImportError, ValueError):
            missing.add(name)
    return missing


def check_one(kata, files, stub_root):
    """Returns a list of problems for one kata's suite."""
    problems = []

    wanted = set()
    for path in files:
        rel = os.path.relpath(path, ROOT)
        try:
            wanted |= imported_names(path)
        except SyntaxError as exc:
            problems.append(
                f"{rel}:{exc.lineno}: {exc.msg}\n"
                f"    The frozen suite does not parse. Fix it before your next rep — "
                f"finding this with the drill clock running is the whole reason this "
                f"check exists."
            )
    if problems:
        return problems

    # Only the kata's own module gets a stand-in. Anything else that will not import is a
    # real defect in the suite, and standing in for it would hide exactly the class of bug
    # this check exists to catch: `import pytset` is not a missing implementation, it is a
    # typo, and it must fail here rather than mid-rep.
    #
    # `make drill` writes src/<kata>.py and nothing else (tools/drill.py:stub_for), so the
    # kata name is the one module a frozen suite may expect to appear from nowhere.
    missing = unresolvable(wanted)
    stood_in = sorted(missing & {kata})
    for name in sorted(missing - {kata}):
        problems.append(
            f"practice/katas/{kata}/tests/: imports `{name}`, which does not exist.\n"
            f"    It is not installed, not in the standard library, and not this kata's "
            f"own module.\n"
            f"    `make drill` writes src/{kata}.py, so `{kata}` is the only name a "
            f"frozen suite may expect to appear from nowhere.\n"
            f"    If `{name}` is a third-party package, it belongs in SETUP.md."
        )
    if problems:
        return problems

    stub_dir = os.path.join(stub_root, kata)
    os.makedirs(stub_dir, exist_ok=True)
    for name in stood_in:
        with open(os.path.join(stub_dir, f"{name}.py"), "w") as fh:
            fh.write(STUB.format(name=name))

    env = dict(os.environ, PYTHONPATH=stub_dir, PYTHONDONTWRITEBYTECODE="1")
    run = subprocess.run(
        [sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider",
         "--collect-only", os.path.join(KATAS, kata, "tests")],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )

    note = (f" (stood in for: {', '.join(stood_in)})" if stood_in else "")
    if run.returncode == 5:
        problems.append(
            f"practice/katas/{kata}/tests/: collected zero tests{note}.\n"
            f"    A suite that collects nothing is a suite that is not there."
        )
    elif run.returncode != 0:
        detail = (run.stdout + run.stderr).strip().splitlines()
        tail = "\n".join("    " + ln for ln in detail[-12:])
        problems.append(
            f"practice/katas/{kata}/tests/: does not collect{note}.\n"
            f"    Collected against a generated stand-in, not against your `src/`, so "
            f"this is a problem in the frozen suite itself.\n{tail}"
        )
    return problems


def main():
    found = suites()
    if not found:
        print("no Python test suites yet — see SETUP.md")
        return 0

    problems = []
    with tempfile.TemporaryDirectory(prefix="frozen-py-") as stub_root:
        for kata, files in found.items():
            print(f"=== {kata} (frozen, pytest) ===")
            problems += check_one(kata, files, stub_root)

    # stdout, not stderr, and for the same reason check_log.py does it: these problems are
    # printed after a run of "=== kata ===" progress lines, and splitting the two streams
    # makes them interleave unpredictably in a terminal and in CI logs.
    if problems:
        print()
        for p in problems:
            print(p)
        print(f"\n{len(problems)} problem(s) in the frozen Python suites.")
        return 1
    print("frozen Python suites collect")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
