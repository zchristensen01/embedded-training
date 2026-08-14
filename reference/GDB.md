# gdb, for this repo

Enough to drive a debugger under time pressure. Not a manual — the twelve commands that
cover almost everything, plus how they fit the katas and the bug hunts.

**When to reach for it.** Not on every rep. `make test` builds under AddressSanitizer and
UndefinedBehaviorSanitizer with `-fno-sanitize-recover=all`, so most memory bugs abort and
hand you the file, the line and a stack trace — reading that is faster than any debugger.
The debugger is for the bug that raises *nothing*: a comparison that should be `<=`, an
index that is one too far, a `volatile` that went missing. Those produce a wrong answer and
no diagnostic, and they are exactly what `make hunt` plants.

---

## Getting a debuggable binary

```bash
make debug MODULE=ring_buffer        # -g -O0, sanitizers still on. Does NOT run it
gdb build/ring_buffer-debug
```

`make test` builds at `-O1` with no debug info, which is why there is a separate target.
Optimisation reorders and inlines, so `-O0` is what makes stepping match the source. The
sanitizers stay on — they work fine under gdb and you want them there.

`make hunt` builds this for you and prints the command.

---

## The twelve commands

### Getting there

| Command | Short | What |
|---|---|---|
| `run` | `r` | Start it. Add arguments after: `run 5 foo` |
| `break rb_push` | `b rb_push` | Stop when that function is entered |
| `break ring_buffer.c:42` | `b ring_buffer.c:42` | Stop at that line |
| `break rb_pop if count == 0` | | Conditional — the one that saves you in a loop |
| `continue` | `c` | Run until the next breakpoint |

### Moving

| Command | Short | What |
|---|---|---|
| `next` | `n` | One line. Steps **over** calls |
| `step` | `s` | One line. Steps **into** calls |
| `finish` | `fin` | Run to the end of this function and print its return value |

`next` versus `step` is the one people get wrong under pressure. Default to `next`; use
`step` only when you actually suspect the callee.

### Looking

| Command | Short | What |
|---|---|---|
| `backtrace` | `bt` | The call stack. **The first thing to type on a crash** |
| `print rb->count` | `p rb->count` | Any expression, including calls: `p rb_count(rb)` |
| `info locals` | `i lo` | Every local in this frame at once |
| `x/8xb buf` | | Examine memory: 8 values, heX, Byte-sized. `x/4dw` for 4 decimal words |
| `frame 2` | `f 2` | Move up the stack to inspect a caller's locals |

### The one that finds silent bugs

```
watch rb->head
```

A **watchpoint**: execution stops the instant that expression's value changes, and gdb
prints the old and new values. When you know *what* went wrong but not *where*, this is
the fastest route in the whole tool. It is also the answer to the classic interview
question "how would you find what's corrupting this variable."

---

## The three-minute routine

Most bugs fall to this without any cleverness:

1. **`bt`** — where are you, and how did you get here.
2. **`i lo`** at the failing frame — what does the state actually look like, versus what you
   assumed when you wrote it.
3. **`b <the suspicious line>`, `r`, then `p` the invariant** — the buffer's `count` against
   `head - tail`, the index against the capacity. Katas are invariant machines; the bug is
   almost always an invariant that stopped holding one line before you noticed.

If two minutes of that produces nothing, the bug is usually not where you are looking.
Re-read the failing test and ask what it is really asserting.

---

## Reading a sanitizer report instead

Half the time you will not need gdb, because ASan already told you. The shape:

```
==12345==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x60200000eff4
WRITE of size 1 at 0x60200000eff4 thread T0
    #0 0x... in rb_push practice/katas/ring_buffer/src/ring_buffer.c:31
```

Three things to take from it, in order: **what kind** (`heap-buffer-overflow`,
`stack-use-after-return`, `heap-use-after-free`), **read or write**, and **the first frame
in your own code** — ignore the frames inside libc. `-fno-sanitize-recover=all` means it
aborts there rather than printing and continuing, so the first report is the real one.

UBSan reads differently — one line, no stack:

```
ring_buffer.c:47:20: runtime error: left shift of 1 by 31 places cannot be represented in type 'int'
```

That one is a signed-shift bug, and it is a deck card as well as a compiler finding.

---

## Python

There is no gdb, and `pytest` already prints the assertion and the values. When that is not
enough:

```bash
PYTHONPATH=practice/katas/log_parser_py/src \
  python3 -m pytest --pdb practice/katas/log_parser_py/tests
```

`--pdb` drops you into a shell at the point of failure with the frame intact. The commands
are close cousins: `l` list, `n` next, `s` step, `c` continue, `p expr`, `u`/`d` to move up
and down the stack, `q` quit. `breakpoint()` in the source stops there too.

---

## What this is worth in an interview

**H9** in [`plan/INTERVIEW_REQUIREMENTS.md`](../plan/INTERVIEW_REQUIREMENTS.md) is *"explain
JTAG vs SWD and what a debugger actually does"*, and its evidence bar is a deck card — the
verbal answer, not the driving. This file covers the driving, which the spec does not score
and an interviewer will still watch you do.

The reported shape of it: Intel runs a dedicated debug round, and Tesla's take-home is
reported to hand you a C module and ask you to find the errors. In both, the failure mode is
not ignorance of gdb — it is reaching for `printf`, rebuilding, and burning ten minutes
you did not have. `make hunt` exists to drill exactly that, and it now asks you afterwards
which route you took.
