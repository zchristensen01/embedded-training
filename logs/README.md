# Logs

- `log.tsv` — every kata rep. date, module, variant, minutes, clean, note. Read by `make report`.
- `splits.tsv` — phase breakdown per rep: design, write, compile, debug. Written by `make lap`.
  `write + compile` as a share of total is your syntax fluency in one number.
- `ai-use.tsv` — one line every time you use AI. date, used_for, rule, note. Review it weekly.
  If this file is growing in week 6, the rules in PRACTICE_SYSTEM.md aren't being followed.
- `WEEKLY_REVIEW.md` — copy the block every Sunday.
- `prompts/` — your written answers to design prompts, with rubric scores.
- `.start_date` — created on day 1 so `make today` knows where you are:
  `date +%F > logs/.start_date`
