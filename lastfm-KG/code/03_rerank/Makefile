##
# Rerank recos according to metrics
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
all: .update_subgraphs.sentinel .metric_eval.sentinel

.update_subgraphs.sentinel:
	-mkdir $(TMP)/updated-kgs
	$(py) update_user_subgraphs.py \
		--user-kg-dir=$(TMP)/updated-kgs/ \
		--num-profiles=-1 \
		--reco-dir=$(TMP)/recos \
		--catalog-kg=$(PROCESSED)/catalog-kg.ttl \
		--outdir=$(TMP)/updated-kgs \
		--nproc=78
	@touch $@

.metric_eval.sentinel: .update_subgraphs.sentinel
	-mkdir $(TMP)/metrics
	$(py) metric_eval.py \
		--updated-kg-dir=$(TMP)/updated-kgs \
		--base-subgraph-dir=$(TMP)/subkgs \
		--metrics-out-dir=$(TMP)/metrics \
		--nproc=78
	@touch $@

# end
