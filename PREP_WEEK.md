# The prep week

**Monday 17 to Sunday 23 August 2026. The plan starts Monday 24th.**

This is session 0 of the build plan, with real dates on it. It used to be a weekend; it is
now a week, because the weekend version asked for six and a half hours across two days and
left no room at all for the reading that has to happen first.

**One module a day, and the rest of the day is reading.** That is the trade. The build work
is unchanged — the same six suites, the same six and a half hours — spread thin enough that
each one gets a BRIEF read properly rather than skimmed, and thin enough that there is time
left over for Mimic and for the concepts the deck is about to start asking about.

Nothing in the ninety-eight days moves. The five Sunday build sessions stay in weeks 1 to 5,
where each suite is still written the week before it is first drilled.

> **This is not setup overhead.** Writing the API and the test suite before the
> implementation is the single most-interviewed skill in both tracks. You are doing rep zero
> of "how would you test this," which is a top-three question. Treat it as the work, not as
> preparation for the work.

---

## Before you start — 15 minutes, Monday morning

- [ ] `echo 2026-08-24 > logs/.start_date`
- [ ] `make dates` — writes `plan/CALENDAR.dated.md`, gitignored, real dates. This is the one to open daily.
- [ ] `make today` — should print **`PREP WEEK · Mon, day 1 of 7 · day 1 is 2026-08-24`** and hand you `ring_buffer`. It prints a prep day every day this week, then rolls over to week 1 on the 24th on its own.
- [ ] `make check` — all seven checks. Should print `all checks pass` on a clean tree.
- [ ] Skim [DAILY.md](DAILY.md). Read it properly on Sunday the 23rd, when it is about tomorrow.

Toolchain is already good: `pytest 9.1.1` and `gcc 13.3.0` are installed. `clang` is not —
only CI needs it, so nothing this week is blocked. Install it later if you want
`make test CC=clang` as a second opinion.

**One thing with a lead time, worth acting on now rather than in a few weeks:** T24 needs a
programmable SCPI instrument on the bench — a scope, bench supply or meter with a USB/LAN
command interface. It first bites in **week 11, the week of Monday 2 November**. Don't
discover in November that you don't have one.

---

## The shape of a prep day

| | |
|---|---|
| **One module** | 60 min, or 90 for `ring_buffer`. `make today` names it |
| **The deck** | `make review N=10`. Out loud, with the trap |
| **The rest** | Mimic reading, and the concepts behind the cards you could not answer |

**The deck is 10 cards, not the weekday's full pass, on purpose.** There are 162 cards and
all of them are unseen. This week a card you cannot answer is not a card you failed — it is
reading you have not done yet, and reading is minutes per card rather than seconds. Ten of
those is a real half hour. Answer it, go and learn the thing, and then `make card` to write
down what you learned in your own words with the trap on it. That card is worth more than
the one that caught you.

`make review N=20` any day it is going quickly. The Leitner schedule does not care which
week you are in and nothing is being scored yet — the boxes just start moving.

---

## After each suite is written — the part that gets skipped

Same four checks every day. `make today` prints them for the module you are on, and this is
what they are for.

```bash
make check-frozen                 # C modules: header parses standalone, suite compiles, gcc + clang
make test MODULE=<name>           # *_py modules instead: pytest collects the suite
make drill KATA=<name>            # must START a rep, not refuse it. Then Ctrl-C
git commit
```

**`make drill` is the real check.** It refuses any module whose suite is still the
scaffolded placeholder. If it refuses, step 3 is not finished — go back. If it starts a rep,
hit Ctrl-C: you are not drilling anything this week, you are proving the suite is real.

**What you owe the logs this week: almost nothing.**

- **`logs/log.tsv` stays untouched.** A build is not a rep. The first row in it is Monday
  the 24th, written by `make done`. Do not hand-write build hours into it — the time curve
  is a curve of *reps*, and a 90-minute build row sitting in front of your first real rep
  would poison the first thing `make report` shows you.
- **`logs/ai-use.tsv` gets a row for every use of AI**, including this repo's tooling and
  including anything you asked while reading. Date, what for, which rule it fell under.
- **`git commit`, every day.** The commit history is the second record, and it is the one a
  hiring manager can actually see. Six daily commits read better than one Sunday dump.

> **The AI rule, and it applies hardest right here.**
> AI may write the test *runner* and the assert macros — that plumbing is already in the
> generated file. **AI may not write a single test case.** If it does, you have outsourced
> the exact thing you are selling, and you will have no answer when someone asks how you'd
> test it.

These suites are **frozen for fourteen weeks**. A rushed suite is a rushed fourteen weeks.

---

## The build recipe — identical for all six

```bash
make newkata NAME=<module>      # scaffolds BRIEF/VARIANTS/NOTES, tests/, src/
```

1. **Read the whole BRIEF first.** Each one teaches the module from the ground up — the
   problem in plain language, a diagram, the API line by line, and paper questions to answer
   before you type. This is the only time you read it cold; from the 24th on it's a reference.

2. **Write the contract, deliberately. You live with it for fourteen weeks.**
   - **C module** → `practice/katas/<name>/include/<name>.h`
   - **Python module** (`*_py`) → there is **no header and no `include/`**. The contract is
     the API written out in `BRIEF.md`, and the frozen suite is what enforces it.

3. **Write every test case yourself, in `tests/`.** Each BRIEF ends with a
   **"Tests it must pass"** table listing the cases in prose, each with the bug it protects
   against. Turning that table into real cases is the job. List them in the BRIEF in your own
   words first, then write them.

4. **The four checks above.**

---

## Monday 17 August — `ring_buffer` — 90 min

*First drilled week 1 Monday.* The flagship C kata and the most-asked embedded coding
question there is. A fixed-capacity FIFO over a caller-supplied array.

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

The longest of the six, and it is on Monday for that reason.

---

## Tuesday 18 August — `log_parser_py` — 60 min

*First drilled week 1 Monday.* Stream-parse a file larger than RAM, reduce it, exit with the
right code. This is Y3, and Y3 is a gate — a 90-minute Python assessment decides it.

```python
def scan(lines: Iterable[str]) -> Report
def main(argv: list[str]) -> int
```

**6 cases owed.** No header — write the API into the BRIEF first. Remember the exit code is
part of the contract, so it's part of the suite.

---

## Wednesday 19 August — `fsm` — 60 min

*First drilled week 1 Tuesday.* A state machine done the way firmware does it, not the way a
tutorial does. The vending machine is a reported Tesla take-home item.

```c
void fsm_init(fsm_t *f);
```
(plus the event/transition API — the BRIEF has it in full)

**5 cases owed.** The BRIEF covers switch, table-driven and function-pointer patterns; pick
one for `v1` and leave the others for later variants.

---

## Thursday 20 August — `mem_primitives` — 60 min

*First drilled week 1 Tuesday.* The whiteboard classics, written correctly at every boundary.

```c
size_t my_strlen(const char *s);
int    my_strcmp(const char *a, const char *b);
void  *my_memset(void *dst, int c, size_t n);
void  *my_memcpy(void *restrict dst, const void *restrict src, size_t n);
void  *my_memmove(void *dst, const void *src, size_t n);
int    my_atoi(const char *s);
```

**8 cases owed** — the largest suite of the six. Both overlap directions for `memmove` are
non-negotiable; that pair is the entire reason the function exists, and "why does `memmove`
exist" is capability C4.

---

## Friday 21 August — `binary_frame_py` — 60 min

*First drilled week 1 Wednesday.* Decode telemetry frames on the host: correct `struct`
format and endianness, length validated *before* unpacking, frames reassembled across read
boundaries. This is Y2, and it's the shape of a real take-home.

```python
def decode(buf: bytes) -> dict
def frames(chunks: Iterable[bytes]) -> Iterator[dict]
class FrameError(Exception)
```

**8 cases owed.** No header. The split-across-chunk-boundary case is the one that matters —
a frame arriving in two `read()` calls is the bug every naive decoder has.

---

## Saturday 22 August — `bitops` — 60 min

*First drilled week 1 Wednesday.* Set, clear, toggle, test, count, extract fields, build
masks. Eight minutes is the eventual target time, so this is the cheapest rep in the rotation
and the one you'll do most.

```c
uint32_t field_get(uint32_t word, unsigned lsb, unsigned width);
uint32_t field_set(uint32_t word, unsigned lsb, unsigned width, uint32_t value);
uint32_t reverse_bits(uint32_t w);
bool     is_power_of_two(uint32_t w);
```

**5 cases owed.** Test the signed-shift and `1u` traps explicitly — those are the two bugs
this module exists to drill out of you.

---

## Sunday 23 August — buffer day, and the eve of day 1

No module. This day exists so that one bad evening earlier in the week does not cost you
Monday.

- [ ] **Anything that slipped goes here.** In first-needed order, so a short week costs you Wednesday rather than Monday.
- [ ] `make check` — all seven, clean.
- [ ] `make list` — six modules scaffolded.
- [ ] `make check-calendar` — proves no unbuilt module is scheduled in week 1.
- [ ] **Read [DAILY.md](DAILY.md) start to finish.** It is the one doc that explains what a calendar line actually asks of you. From tomorrow it is a reference you glance at; today is the last day it is worth reading cold.
- [ ] `make review` — no `N`. The full default pass, because tomorrow the deck becomes a timed block and this is the dress rehearsal for it.
- [ ] `git commit`.

**Optional but cheap:** skim [practice/rehearsal/STORIES.md](practice/rehearsal/STORIES.md).
It ships as a skeleton and the stories have to be yours. Nothing is due until week 3's
Saturday — **Saturday 12 September** — but B1, *"why hardware, coming from web?"*, is the
objection in every interviewer's head, and it's worth knowing now that you owe it an answer.

---

## Done means

```bash
make check-calendar     # no unbuilt module scheduled in week 1
make list               # six modules scaffolded
make drill KATA=ring_buffer      # starts a rep instead of refusing → Ctrl-C
```

Then Monday 24 August:

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

Ninety-eight days from there is **Sunday 29 November 2026**.

---

## If the week goes sideways

The order above is by first-needed date, so **stop where you run out and pick up on Sunday**.
A short week costs you Wednesday, not Monday.

If a module still doesn't get built, nothing breaks: `make drill` with no arguments falls
back to whatever *is* built, and refuses what isn't. You lose the calendar's rotation for a
day, not the day itself. Catch up in the week-1 Sunday session — **Sunday 30 August**, which
is otherwise `protocol_parser` + `register_map` at 2 hr 30 min.

What you must not do is write a fast, thin suite to get through the list. Six good suites
beat six complete ones, and a suite you rushed is one you'll be drilling against until
November.

**Delete this file once the six suites exist.** It is dated and it goes stale; the build plan
it is derived from lives in `plan/CALENDAR.md` and is regenerated, not written.
