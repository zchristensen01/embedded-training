# embedded-training — the command interface.
#
# Practice commands are at the top; the build rules for the katas are below them.
# `make help` lists everything.
PY := python3

.PHONY: help today calendar newkata drill lap done status review stats prompt \
        rehearse report card progress test debug analyze valgrind list log \
        check-log check-frozen check-calendar check-coverage clean

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
	@echo "  occasional"
	@echo "    make prompt   draw a 'how would you test X' design prompt"
	@echo "    make rehearse draw a behavioural story, time the take, log it"
	@echo "    make report   the progress measurements"
	@echo "    make progress score the 78 capabilities, write logs/PROGRESS.md"
	@echo "    make newkata  NAME=x  scaffold a new kata module"
	@echo "    make calendar regenerate plan/CALENDAR.md with real dates"
	@echo ""
	@echo "  the build, and second opinions on it"
	@echo "    make test MODULE=ring_buffer   ... just one kata"
	@echo "    make test CC=clang             build with a second compiler"
	@echo "    make debug MODULE=fsm          -g -O0 for gdb (does not run it)"
	@echo "    make analyze                   gcc -fanalyzer, finds bugs without running"
	@echo "    make valgrind MODULE=fsm       second opinion on memory (no sanitizers)"
	@echo "    make list                      which katas have an implementation"
	@echo "    make check-frozen              the headers and suites still compile (CI runs this)"
	@echo "    make check-calendar            schedule and build plan agree (CI runs this)"
	@echo "    make check-coverage            every capability has a mechanism (CI runs this)"
	@echo "    make check-log                 validate logs/log.tsv (CI runs this)"
	@echo "    make clean                     remove build/"

# ---------------------------------------------------------------- practice ---

today:    ; @$(PY) tools/today.py
calendar: ; @$(PY) tools/schedule.py --write
newkata:  ; @$(PY) tools/newkata.py $(NAME)
drill:    ; @$(PY) tools/drill.py start $(KATA) $(VARIANT)
lap:      ; @$(PY) tools/drill.py lap $(P)
done:     ; @$(PY) tools/drill.py done
status:   ; @$(PY) tools/drill.py status
review:   ; @$(PY) tools/review.py $(N)
stats:    ; @$(PY) tools/review.py --stats
prompt:   ; @$(PY) tools/prompt.py
rehearse: ; @$(PY) tools/rehearse.py $(S)
report:   ; @$(PY) tools/report.py
card:     ; @$(PY) tools/card.py $(ARGS)
progress: ; @$(PY) tools/progress.py --write
log:      ; @$(PY) tools/check_log.py --summary
check-log:; @$(PY) tools/check_log.py
check-calendar: ; @$(PY) tools/schedule.py --check
check-coverage: ; @$(PY) tools/progress.py --check

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

# The Python kata is run by pytest, not compiled. MODULE= filters both lists rather
# than being trusted blindly, so `make test MODULE=test_harness_py` doesn't try to
# hand a directory full of .py files to the C compiler.
ALL_PY := $(sort $(patsubst $(KATAS)/%/tests/,%,$(dir $(wildcard $(KATAS)/*/tests/*.py))))

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
	    $(PY) -m pytest -q $(KATAS)/$$m/tests || exit 1; \
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

list:
	@echo "with an implementation: $(if $(ALL_MODULES),$(ALL_MODULES),none yet)"
	@echo "pytest modules:         $(if $(ALL_PY),$(ALL_PY),none yet)"
	@echo "scaffolded:             $(sort $(notdir $(patsubst %/,%,$(dir $(wildcard $(KATAS)/*/BRIEF.md)))))"

$(BUILD):
	@mkdir -p $(BUILD)

clean:
	@rm -rf $(BUILD)

.DEFAULT_GOAL := help
