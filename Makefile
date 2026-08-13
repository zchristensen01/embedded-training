# embedded-training — the command interface.
#
# Practice commands are at the top; the build rules for the katas are below them.
# `make help` lists everything.
PY := python3

.PHONY: help today calendar dates newkata drill lap done status review stats prompt \
        design designs rehearse report card progress test debug analyze valgrind list log decks \
        hunt hunt-done hunts snapshots \
        check-log check-frozen check-frozen-py check-calendar check-coverage check-decks \
        check-generated check clean

help:
	@echo "  the daily loop"
	@echo "    make today    what to do right now"
	@echo "    make drill    start a kata rep (wipes src/, starts the clock)"
	@echo "    make lap      record a phase split: design -> write -> compile -> debug"
	@echo "    make test     build + run the frozen suites under sanitizers"
	@echo "    make done     stop the clock, log the rep"
	@echo "    make review   spaced-repetition deck pass, ANSWER OUT LOUD"
	@echo "    make card     something surprised you? add a deck card, 20 seconds"
	@echo ""
	@echo "  free practice — none of this needs the calendar's permission"
	@echo "    make drill KATA=fsm            any module, any time. Picks the variant"
	@echo "                                   you have done least recently"
	@echo "    make drill KATA=fsm VARIANT=v4 exactly that one"
	@echo "    make drill LANG=py             a Python rep now; LANG=c for a C one"
	@echo "    make hunt                      find a bug planted in your own old code"
	@echo "    make review N=40               a bigger deck pass"
	@echo "    make review N=\"--topic sync\"   just one topic"
	@echo "    make prompt                    a 'how would you test X' subject"
	@echo "    make design                    architect a subsystem in 45 min, then defend it"
	@echo "    make rehearse                  a behavioural story, timed"
	@echo ""
	@echo "  where you stand"
	@echo "    make report   time curve, clean-compile rate, phase split, what you avoid"
	@echo "    make progress every capability scored against its evidence bar"
	@echo "    make log      the per-module time curve and which have met their bar"
	@echo "    make decks    what each deck card is doing, and what is thin"
	@echo "    make hunts    bug-hunt history: which bug kinds catch you out"
	@echo "    make designs  architecture drills written, and what they scored"
	@echo "    make stats    deck box distribution"
	@echo "    make status   what rep is in flight right now"
	@echo "    make snapshots which modules have code old enough to hunt in"
	@echo ""
	@echo "  occasional"
	@echo "    make hunt-done  stop the hunt clock, reveal the mutation, log it"
	@echo "    make newkata  NAME=x  scaffold a new kata module"
	@echo "    make calendar regenerate plan/CALENDAR.md (committed, relative days)"
	@echo "    make dates    write plan/CALENDAR.dated.md with your real dates"
	@echo ""
	@echo "  the build, and second opinions on it"
	@echo "    make test MODULE=ring_buffer   ... just one kata"
	@echo "    make test CC=clang             build with a second compiler"
	@echo "    make debug MODULE=fsm          -g -O0 for gdb (does not run it)"
	@echo "    make analyze                   gcc -fanalyzer, finds bugs without running"
	@echo "    make valgrind MODULE=fsm       second opinion on memory (no sanitizers)"
	@echo "    make list                      which katas have an implementation"
	@echo "    make clean                     remove build/"
	@echo ""
	@echo "  the checks. CI runs all seven on every push; 'make check' runs them here"
	@echo "    make check-frozen              the C headers and suites still compile"
	@echo "    make check-frozen-py           the Python suites still import and collect"
	@echo "    make check-log                 validate logs/log.tsv"
	@echo "    make check-calendar            schedule, build plan and timer blocks agree"
	@echo "    make check-coverage            spec and coverage map describe the same set"
	@echo "    make check-decks               every card tag names a real capability"
	@echo "    make check-generated           the generated files match their generators"
	@echo ""
	@echo "  DAILY.md explains what a calendar line means and how to practise off-plan."

# ---------------------------------------------------------------- practice ---

today:    ; @$(PY) tools/today.py
calendar: ; @$(PY) tools/schedule.py --write
dates:    ; @$(PY) tools/schedule.py --dates
newkata:  ; @$(PY) tools/newkata.py $(NAME)
drill:    ; @$(PY) tools/drill.py start $(KATA) $(VARIANT) $(LANG)
lap:      ; @$(PY) tools/drill.py lap $(P)
done:     ; @$(PY) tools/drill.py done
status:   ; @$(PY) tools/drill.py status
review:   ; @$(PY) tools/review.py $(N)
stats:    ; @$(PY) tools/review.py --stats
prompt:   ; @$(PY) tools/prompt.py
design:   ; @$(PY) tools/design.py $(N)
designs:  ; @$(PY) tools/design.py --stats
# Accept both `make rehearse S=B7` and the bare `make rehearse B7`. The bare form is what
# the calendar and `make design` print, and what anyone would type. Without this, make
# treats B7 as a second target: `rehearse` runs with no argument, silently draws the FIRST
# story, LOGS A TAKE AGAINST IT, and only then fails with "No rule to make target 'B7'".
# A wrong row in logs/rehearsal.tsv is worse than an error, so both forms now work.
STORY := $(if $(S),$(S),$(filter B%,$(MAKECMDGOALS)))
rehearse: ; @$(PY) tools/rehearse.py $(STORY)

# Swallow the story id so it is not treated as an unbuildable target. Derived from
# STORIES.md rather than a `B%` wildcard, which also matched `make Build` and any other
# capital-B word — succeeding silently while doing nothing.
STORY_IDS := $(shell sed -n 's/^## \(B[0-9]\+\) .*/\1/p' practice/rehearsal/STORIES.md)
$(STORY_IDS): ; @:
report:   ; @$(PY) tools/report.py
card:     ; @$(PY) tools/card.py $(ARGS)
progress: ; @$(PY) tools/progress.py --write
log:      ; @$(PY) tools/check_log.py --summary
hunt:     ; @$(PY) tools/bughunt.py start $(KATA)
hunt-done:; @$(PY) tools/bughunt.py done
hunts:    ; @$(PY) tools/bughunt.py --stats
snapshots:; @$(PY) tools/bughunt.py --list
decks:    ; @$(PY) tools/check_decks.py --summary
check-log:; @$(PY) tools/check_log.py
check-calendar:  ; @$(PY) tools/schedule.py --check
check-coverage:  ; @$(PY) tools/progress.py --check
check-decks:     ; @$(PY) tools/check_decks.py
check-generated: ; @$(PY) tools/check_generated.py

# Everything CI runs, in one command. Run it before you push.
check: check-frozen check-frozen-py check-log check-calendar check-coverage check-decks check-generated
	@echo "all checks pass"

# ------------------------------------------------------------------- build ---

CC     ?= gcc
CSTD    = -std=c11
WARN    = -Wall -Wextra -Werror
# -fno-sanitize-recover is not optional: by default UBSan prints a diagnostic and
# lets the program carry on, so a run with real undefined behaviour still exits 0
# and CI goes green. This makes it abort like ASan does.
SAN      = -fsanitize=address,undefined -fno-sanitize-recover=all
# TSan and ASan cannot coexist in one binary, so concurrency_sim gets its own set.
SAN_TSAN = -fsanitize=thread -fno-sanitize-recover=all -pthread

KATAS := practice/katas
BUILD := build

# A kata is buildable once it has at least one source file. src/ is gitignored and
# `make drill` empties it, so this list is deliberately short on a fresh clone and
# grows as you build each module.
ALL_MODULES := $(sort $(patsubst $(KATAS)/%/src/,%,$(dir $(wildcard $(KATAS)/*/src/*.c))))

# Python katas are run by pytest, not compiled. MODULE= filters both lists rather than
# being trusted blindly, so `make test MODULE=test_harness_py` doesn't try to hand a
# directory full of .py files to the C compiler.
#
# Keyed on src/*.py, exactly like ALL_MODULES is keyed on src/*.c — a kata is testable
# once it has an implementation. It used to key on tests/*.py, which meant every Python
# kata was always in the list: a bare `make test` during an unrelated C rep would build
# and pass that rep, then hard-fail on a scaffolded stub suite it had no reason to run.
ALL_PY := $(sort $(patsubst $(KATAS)/%/src/,%,$(dir $(wildcard $(KATAS)/*/src/*.py))))

MODULES    := $(if $(MODULE),$(filter $(MODULE),$(ALL_MODULES)),$(ALL_MODULES))
PY_MODULES := $(if $(MODULE),$(filter $(MODULE),$(ALL_PY)),$(ALL_PY))

# TSan and ASLR fight on some kernels — WSL2 in particular. The loader hands back a
# mapping TSan refuses and the process dies with "unexpected memory mapping" before a
# single test runs, intermittently, which reads exactly like a flaky test and isn't
# one. Disabling ASLR for that one binary fixes it and changes nothing else.
TSAN_RUN := $(shell command -v setarch >/dev/null 2>&1 && echo "setarch $$(uname -m) -R")

# Per-module sanitizer selection. This has to happen in the shell rather than with
# $(call ...): the loop variable is a shell variable, and a make function expanded
# in the recipe would only ever see the literal string "$m".
SAN_SELECT = case $$m in \
	  concurrency_sim) san="$(SAN_TSAN)"; runner="$(TSAN_RUN)";; \
	  *)               san="$(SAN)";      runner="";; \
	esac

test: | $(BUILD)
	@if [ -z "$(MODULES)" ] && [ -z "$(PY_MODULES)" ]; then \
	    if [ -n "$(MODULE)" ]; then \
	        echo "$(MODULE): nothing to run. A C kata needs src/*.c, a Python one tests/*.py."; \
	        echo "Start a rep with: make drill KATA=$(MODULE)"; \
	        exit 1; \
	    fi; \
	    echo "No kata has an implementation yet. See SETUP.md, then: make newkata NAME=bitops"; \
	fi
	@for m in $(MODULES); do \
	    echo "=== $$m ==="; \
	    if [ ! -d $(KATAS)/$$m/tests ]; then \
	        echo "  no tests/ — write the suite before the implementation"; exit 1; \
	    fi; \
	    $(SAN_SELECT); \
	    $(CC) $(CSTD) $(WARN) -O1 $$san -I$(KATAS)/$$m/include \
	        $(KATAS)/$$m/src/*.c $(KATAS)/$$m/tests/*.c -o $(BUILD)/$$m || exit 1; \
	    $$runner $(BUILD)/$$m || exit 1; \
	done
	@for m in $(PY_MODULES); do \
	    echo "=== $$m (pytest) ==="; \
	    PYTHONPATH=$(KATAS)/$$m/src $(PY) -B -m pytest -q -p no:cacheprovider \
	        $(KATAS)/$$m/tests || exit 1; \
	done

# Sanitizers stay on: they work fine under gdb and you want them there.
debug: | $(BUILD)
	@for m in $(MODULES); do \
	    echo "=== $$m (debug) ==="; \
	    $(SAN_SELECT); \
	    $(CC) $(CSTD) $(WARN) -g -O0 $$san -I$(KATAS)/$$m/include \
	        $(KATAS)/$$m/src/*.c $(KATAS)/$$m/tests/*.c -o $(BUILD)/$$m-debug || exit 1; \
	    echo "built $(BUILD)/$$m-debug — run: gdb $(BUILD)/$$m-debug"; \
	done

# Advisory, not gating: -fanalyzer occasionally produces false positives, so read
# the path it prints rather than obeying it blindly. No -Werror for that reason.
analyze:
	@for m in $(MODULES); do \
	    echo "=== $$m (analyzer) ==="; \
	    for f in $(KATAS)/$$m/src/*.c $(KATAS)/$$m/tests/*.c; do \
	        $(CC) $(CSTD) -Wall -Wextra -fanalyzer -I$(KATAS)/$$m/include \
	            -c $$f -o /dev/null || exit 1; \
	    done; \
	done
	@echo "analyzer clean"

# Valgrind and ASan conflict, so this build drops the sanitizers.
valgrind: | $(BUILD)
	@for m in $(MODULES); do \
	    echo "=== $$m (valgrind) ==="; \
	    $(CC) $(CSTD) $(WARN) -g -O1 -I$(KATAS)/$$m/include \
	        $(KATAS)/$$m/src/*.c $(KATAS)/$$m/tests/*.c -o $(BUILD)/$$m-vg || exit 1; \
	    valgrind --error-exitcode=1 --leak-check=full \
	             --track-origins=yes $(BUILD)/$$m-vg || exit 1; \
	done

# src/ is gitignored, so a fresh clone has no implementations and `make test` has
# nothing to build. What CI can still prove is that every frozen artifact is valid
# C: each header parses standalone, and each test suite compiles against it. Only
# the link step needs an implementation, and that is deliberately not committed.
FROZEN := $(sort $(patsubst $(KATAS)/%/tests/,%,$(dir $(wildcard $(KATAS)/*/tests/*.c))))

check-frozen:
	@if [ -z "$(FROZEN)" ]; then echo "no C test suites written yet — see SETUP.md"; fi
	@for m in $(FROZEN); do \
	    echo "=== $$m (frozen) ==="; \
	    $(SAN_SELECT); \
	    for h in $(KATAS)/$$m/include/*.h; do \
	        [ -e "$$h" ] || continue; \
	        $(CC) $(CSTD) $(WARN) -I$(KATAS)/$$m/include -fsyntax-only -x c $$h || exit 1; \
	    done; \
	    for f in $(KATAS)/$$m/tests/*.c; do \
	        $(CC) $(CSTD) $(WARN) $$san -I$(KATAS)/$$m/include \
	            -c $$f -o /dev/null || exit 1; \
	    done; \
	done
	@echo "frozen contracts compile"

# The Python half. `make test` needs an implementation and src/ is gitignored, so — exactly
# as for C — the most CI can prove about a frozen Python suite is that it is valid and
# collectable. Without this a suite with a syntax error passed every check and shipped green,
# and you found out mid-rep with the clock running.
#
# --collect-only imports the module and enumerates its tests without running them, which is
# the closest analogue to compiling a C suite without linking it. A suite that collects zero
# tests is a suite that is not there.
FROZEN_PY := $(sort $(patsubst $(KATAS)/%/tests/,%,$(dir $(wildcard $(KATAS)/*/tests/*.py))))

check-frozen-py:
	@if [ -z "$(FROZEN_PY)" ]; then echo "no Python test suites yet — see SETUP.md"; fi
	@for m in $(FROZEN_PY); do \
	    echo "=== $$m (frozen, pytest) ==="; \
	    PYTHONPATH=$(KATAS)/$$m/src $(PY) -B -m pytest -q -p no:cacheprovider \
	        --collect-only $(KATAS)/$$m/tests > /dev/null || exit 1; \
	done
	@echo "frozen Python suites collect"

list:
	@echo "with an implementation: $(if $(ALL_MODULES),$(ALL_MODULES),none yet)"
	@echo "pytest modules:         $(if $(ALL_PY),$(ALL_PY),none yet)"
	@echo "scaffolded:             $(sort $(notdir $(patsubst %/,%,$(dir $(wildcard $(KATAS)/*/BRIEF.md)))))"

$(BUILD):
	@mkdir -p $(BUILD)

clean:
	@rm -rf $(BUILD)

.DEFAULT_GOAL := help
