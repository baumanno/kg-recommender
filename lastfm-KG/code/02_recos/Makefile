##
# Recommendations for LastFM users
#
# @file
# @version 0.1

SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

PROJECT_ROOT ?= ../../..
DATADIR ?= ../../data
PROCESSED := $(DATADIR)/processed
TMP := $(DATADIR)/tmp
RES := $(DATADIR)/res

# alias the python- and pip-executables to the ones in the virtual environment
py = $$(if [ -d $(PROJECT_ROOT)/'.venv' ]; then echo $(PROJECT_ROOT)/".venv/bin/python3"; else echo "python3"; fi)
pip = $(py) -m pip

.DEFAULT_GOAL := help

# Display help for targets when calling `make` or `make help`.
# To add help-tags to new targets, place them after the target-name (and
# dependencies) following a `##`. See the targets in this file for examples.
.PHONY: help
help: ## Display this help section
	@awk 'BEGIN {FS = ":.*?## "} /^[.a-zA-Z\$$/]+.*:.*?##\s/ {printf "\033[36m%-38s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: all
all: algo.out .user-recos.sentinel

algo.out: $(PROCESSED)/user_ratings.csv
	$(py) 01_reco_eval.py \
		$< \
		--write-table=$(RES)/tab-reco-eval.tex

.user-recos.sentinel: $(PROCESSED)/user_ratings.csv algo.out
	$(eval ALGO := $(shell cat algo.out))
	$(py) 02_dump_recos.py \
		$< \
		--algo=$(ALGO) \
		--top-n=100 \
		--save-dir=$(TMP)/recos/
	@touch .user-recos.sentinel

.PHONY: clean
clean:
	-rm $(TMP)/recos/*.csv
	-rm algo.out
# end
