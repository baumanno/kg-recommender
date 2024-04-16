##
# Evaluate recos
#
# @file
# @version 0.1

SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

PROJECT_ROOT ?= ../..
DATADIR ?= $(PROJECT_ROOT)/data
PROCESSED := $(DATADIR)/processed
TMP := $(DATADIR)/tmp

.DEFAULT_GOAL := help

# Display help for targets when calling `make` or `make help`.
# To add help-tags to new targets, place them after the target-name (and
# dependencies) following a `##`. See the targets in this file for examples.
.PHONY: help
help: ## Display this help section
	@awk 'BEGIN {FS = ":.*?## "} /^[.a-zA-Z\$$/]+.*:.*?##\s/ {printf "\033[36m%-38s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

ALL_BASE := $(shell find $(PROCESSED)/recos/eval -type f -name "*.eval" -exec basename {} \;)
ALL_BASE := $(subst .eval,, $(ALL_BASE))

NDCG_RESULTS := $(addsuffix .ndcg.result,$(ALL_BASE))
NDCG_RESULTS := $(addprefix $(TMP)/,$(NDCG_RESULTS))

PLOT_DIR := $(PROJECT_ROOT)/viz
PLOT_NAMES := $(PLOT_DIR)/netflix_ndcg_cut_%.pdf

.PHONY: all
all: $(NDCG_RESULTS) $(PLOT_NAMES)

$(PROCESSED)/recos/eval/%.eval:
	@:

$(NDCG_RESULTS): $(TMP)/%.ndcg.result: $(PROCESSED)/recos/eval/%.eval
	tail -n 11 $< > $@

$(PLOT_NAMES): $(NDCG_RESULTS)
	Rscript -e 'renv::run("./01_eval_ndcg.R")'

# end
