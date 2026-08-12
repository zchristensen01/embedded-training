# Rehearsal

The B group in `plan/INTERVIEW_REQUIREMENTS.md` — ten narrative capabilities. Behavioural rounds
reject more test & integration candidates than technical rounds do, so this is not the soft part
of the plan.

Rehearsal is Format C-shaped: repeatable, because you re-tell the same story until it's tight,
and recorded, because you can't hear your own filler words.

```
make rehearse          # draws a story, starts the clock, logs the take
make rehearse S=B7     # a specific one
make rehearse --stats  # takes per story, best times, what you're avoiding
```

## How a take works

1. The tool draws a story and starts timing.
2. **Say it out loud, standing up, no notes.** Ninety seconds is the target for most; B10 is ten
   minutes.
3. Stop the clock. Rate it 1–3 and write one line on what was weak.
4. Record yourself on every third take and watch it back. You will find filler, hedging, and a
   habit of explaining the setup for forty seconds before reaching the point.

A story is **ready** when you've done three takes at 1 (strong) on different days, with at least
one of them recorded and watched.

## The rules

- **Written first, then spoken.** Fill in `STORIES.md` before the first take. An unwritten story
  wanders.
- **Structure every technical answer as:** constraint → options considered → what you chose →
  what you gave up. Candidates who only say what they built sound like they followed a tutorial.
- **Specific beats impressive.** "The stall latch fired at 1.8 A and I found the threshold was
  set from a datasheet typical instead of a measured value" beats "I'm detail-oriented."
- **Your failures are the material.** Mimic's `NOTES.md` and your tuning git history are where
  B5, B8, and B9 come from. Log them as they happen, not from memory in week 9.
