# This weekend — Day 0

**Saturday 15 and Sunday 16 August 2026. The plan starts Monday 17th.**

This is the day-0 build weekend from [SETUP.md](SETUP.md), with real dates on it. It is the
largest single session in the fourteen weeks and the only one not capped by
`make check-calendar`, because it is not a calendar day.

You are building the gym. Right now **nothing is built** — all fifteen kata directories ship
with a `BRIEF.md` and a `VARIANTS.md`, but not one has a written test suite, and
`make drill` refuses every one of them. Monday Day 1 asks for `ring_buffer v1` and
`log_parser_py v1`. If those two do not exist by Sunday night, Monday has nothing to drill.

Six modules. **6 hr 30 min**, split 3.5 / 3.0 across the two days.

> **This is not setup overhead.** Writing the API and the test suite before the
> implementation is the single most-interviewed skill in both tracks. You are doing rep zero
> of "how would you test this," which is a top-three question. Treat it as the work, not as
> preparation for the work.

---

## Before you start — 15 minutes

- [ ] `echo 2026-08-17 > logs/.start_date`
- [ ] `make dates` — writes `plan/CALENDAR.dated.md`, gitignored, real dates. This is the one to open daily.
- [ ] `make today` — should say `Plan starts 2026-08-17.` That is correct; it starts Monday.
- [ ] `make check` — all seven checks. Should print `all checks pass` on a clean tree.
- [ ] Read [DAILY.md](DAILY.md) once, start to finish. It is the one doc that explains what a calendar line actually asks of you.

Toolchain is already good: `pytest 9.1.1` and `gcc 13.3.0` are installed. `clang` is not —
only CI needs it, so nothing this weekend is blocked. Install it later if you want
`make test CC=clang` as a second opinion.

**One thing with a lead time, worth reading now and acting on in a few weeks:** T24 needs a
programmable SCPI instrument on the bench — a scope, bench supply or meter with a USB/LAN
command interface. It first bites in **week 11**. Don't discover in week 11 that you don't
have one.

---

## The build recipe — identical for all six

Same four steps every time. Step 3 is the one that matters and the one nobody else can do
for you.

```bash
make newkata NAME=<module>      # scaffolds BRIEF/VARIANTS/NOTES, tests/, src/
```

1. **Read the whole BRIEF first.** Each one teaches the module from the ground up — the
   problem in plain language, a diagram, the API line by line, and paper questions to answer
   before you type. This is the only time you read it cold; from Monday on it's a reference.

2. **Write the contract, deliberately. You live with it for fourteen weeks.**
   - **C module** → `practice/katas/<name>/include/<name>.h`
   - **Python module** (`*_py`) → there is **no header and no `include/`**. The contract is
     the API written out in `BRIEF.md`, and the frozen suite is what enforces it.

3. **Write every test case yourself, in `tests/`.** Each BRIEF ends with a
   **"Tests it must pass"** table listing the cases in prose, each with the bug it protects
   against. Turning that table into real cases is the job. List them in the BRIEF in your own
   words first, then write them.

4. **Check it took.**
   ```bash
   make drill KATA=<module>
   ```
   It **refuses** a module whose suite is still the scaffolded placeholder. If it refuses,
   step 3 is not finished. If it starts a rep, hit Ctrl-C — you are not drilling today.

> **The rule, and it applies hardest right here.**
> AI may write the test *runner* and the assert macros — that plumbing is already in the
> generated file. **AI may not write a single test case.** If it does, you have outsourced
> the exact thing you are selling, and you will have no answer when someone asks how you'd
> test it.

These suites are **frozen for fourteen weeks**. A rushed suite is a rushed fourteen weeks.

---

## Saturday 15 August — 3 hr 30 min

Ordered by when the calendar first needs it. Everything here is needed by **Tuesday**.

### 1 · `ring_buffer` — 90 min · needed Monday
The flagship C kata and the most-asked embedded coding question there is. A fixed-capacity
FIFO over a caller-supplied array.

```c
void   rb_init(rb_t *rb, uint8_t *storage, size_t capacity);
bool   rb_push(rb_t *rb, uint8_t byte);   /* false if full  */
bool   rb_pop (rb_t *rb, uint8_t *out);   /* false if empty */
bool   rb_is_empty(const rb_t *rb);
bool   rb_is_full (const rb_t *rb);
size_t rb_count   (const rb_t *rb);
```

**6 cases owed.** Keep the capacity small in tests — 4 or 8. With 1024 you'd need a thousand
operations before the interesting case happens. The one that earns its keep is the
interleaved partial fill (push 3, pop 1, push 3, pop 4) checking `count` throughout — that's
the one that catches index drift.

### 2 · `log_parser_py` — 60 min · needed Monday
Stream-parse a file larger than RAM, reduce it, exit with the right code. This is Y3, and Y3
is a gate — a 90-minute Python assessment decides it.

```python
def scan(lines: Iterable[str]) -> Report
def main(argv: list[str]) -> int
```

**6 cases owed.** No header — write the API into the BRIEF first. Remember the exit code is
part of the contract, so it's part of the suite.

### 3 · `mem_primitives` — 60 min · needed Tuesday
The whiteboard classics, written correctly at every boundary.

```c
size_t my_strlen(const char *s);
int    my_strcmp(const char *a, const char *b);
void  *my_memset(void *dst, int c, size_t n);
void  *my_memcpy(void *restrict dst, const void *restrict src, size_t n);
void  *my_memmove(void *dst, const void *src, size_t n);
int    my_atoi(const char *s);
```

**8 cases owed** — the largest suite of the day. Both overlap directions for `memmove` are
non-negotiable; that pair is the entire reason the function exists, and "why does `memmove`
exist" is capability C4.

---

## Sunday 16 August — 3 hr

Everything here is needed by **Wednesday**.

### 4 · `fsm` — 60 min · needed Tuesday
A state machine done the way firmware does it, not the way a tutorial does. The vending
machine is a reported Tesla take-home item.

```c
void fsm_init(fsm_t *f);
```
(plus the event/transition API — the BRIEF has it in full)

**5 cases owed.** The BRIEF covers switch, table-driven and function-pointer patterns; pick
one for `v1` and leave the others for later variants.

### 5 · `binary_frame_py` — 60 min · needed Wednesday
Decode telemetry frames on the host: correct `struct` format and endianness, length validated
*before* unpacking, frames reassembled across read boundaries. This is Y2, and it's the shape
of a real take-home.

```python
def decode(buf: bytes) -> dict
def frames(chunks: Iterable[bytes]) -> Iterator[dict]
class FrameError(Exception)
```

**8 cases owed.** No header. The split-across-chunk-boundary case is the one that matters —
a frame arriving in two `read()` calls is the bug every naive decoder has.

### 6 · `bitops` — 60 min · needed Wednesday
Set, clear, toggle, test, count, extract fields, build masks. Eight minutes is the eventual
target time, so this is the cheapest rep in the rotation and the one you'll do most.

```c
uint32_t field_get(uint32_t word, unsigned lsb, unsigned width);
uint32_t field_set(uint32_t word, unsigned lsb, unsigned width, uint32_t value);
uint32_t reverse_bits(uint32_t w);
bool     is_power_of_two(uint32_t w);
```

**5 cases owed.** Test the signed-shift and `1u` traps explicitly — those are the two bugs
this module exists to drill out of you.

---

## Also on Sunday — 20 minutes, don't skip

- [ ] `make check` — all seven, clean.
- [ ] `make review` — the deck doesn't wait for Monday. 162 cards, all unseen, all due. Out loud, and say the trap.
- [ ] `git commit` the six suites. The commit history is the second record, and it's the one a hiring manager can see.

**Optional but cheap:** skim [practice/rehearsal/STORIES.md](practice/rehearsal/STORIES.md).
It ships as a skeleton and the stories have to be yours. Nothing is due until week 3's
Saturday, but B1 — *"why hardware, coming from web?"* — is the objection in every
interviewer's head, and it's worth knowing now that you owe it an answer.

---

## Done means

```bash
make check-calendar     # no unbuilt module scheduled in week 1
make list               # six modules scaffolded
make drill KATA=ring_buffer      # starts a rep instead of refusing → Ctrl-C
```

Then Monday morning:

```bash
make today
```

which will print **Week 1 · Mon · day 1 of 98**, and ask you for:

| Timer | Block |
|---|---|
| 18 min | `make drill KATA=ring_buffer VARIANT=v1` |
| 28 min | `make drill KATA=log_parser_py VARIANT=v1` |
| 49 min | Main block — Mimic S0: bench, toolchain, repo · S1 motor forensics |
| 12 min | `make review` (deck focus: bitops, memory) |
| 8 min | `make done`, log the session, `git commit` |

---

## If the weekend goes sideways

Do them **in the order above** and stop when you run out of time. The order is by first-needed
date, so a short weekend costs you Wednesday, not Monday.

If a module doesn't get built, nothing breaks: `make drill` with no arguments falls back to
whatever *is* built, and refuses what isn't. You lose the calendar's rotation for a day, not
the day itself. Catch up in the week-1 Sunday session, which is otherwise
`protocol_parser` + `register_map` at 2 hr 30 min.

What you must not do is write a fast, thin suite to get through the list. Six good suites beat
six complete ones, and a suite you rushed is one you'll be drilling against until November.
