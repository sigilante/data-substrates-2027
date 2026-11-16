# Rebuild everything the paper's numbers come from.
# Python 3 and matplotlib suffice for `all`; `board` and `traces` also need a
# full clone of urbit/urbit (history plus the develop branch), set with URBIT.
URBIT ?= ../urbit

all: tables figures reliability

tables:
	python3 data/build_steps.py
	python3 review/apply_decisions.py review/export

figures:
	cd figures && python3 figs.py && python3 fig_kinds.py && python3 tbl_regimes.py

reliability:
	python3 data/reliability.py data/second-coder-full.csv

board:
	python3 review/build_review_data.py $(URBIT)
	python3 review/assemble_board.py

traces:
	python3 data/protocol_bumps.py $(URBIT)
	python3 data/versions.py $(URBIT) pkg/arvo/sys/vane/gall.hoon /tmp/gall-versions.json --first-parent

# Rebuild, then fail if any tracked output changed.
check: tables figures
	git diff --exit-code -- data figures/*.tex

.PHONY: all tables figures reliability board traces check
