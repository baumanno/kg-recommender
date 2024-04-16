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
DATADIR ?= ../../data
PROCESSED := $(DATADIR)/processed
TMP := $(DATADIR)/tmp

# alias the python- and pip-executables to the ones in the virtual environment
py = $$(if [ -d $(PROJECT_ROOT)/'.venv' ]; then echo $(PROJECT_ROOT)/".venv/bin/python3"; else echo "python3"; fi)
pip = $(py) -m pip

HAVE_TREC_EVAL := $(shell command -v trec_eval 2>/dev/null)
ifndef HAVE_TREC_EVAL
$(error trec_eval is missing, please install from https://github.com/usnistgov/trec_eval)
endif

.DEFAULT_GOAL := help

# Display help for targets when calling `make` or `make help`.
# To add help-tags to new targets, place them after the target-name (and
# dependencies) following a `##`. See the targets in this file for examples.
.PHONY: help
help: ## Display this help section
	@awk 'BEGIN {FS = ":.*?## "} /^[.a-zA-Z\$$/]+.*:.*?##\s/ {printf "\033[36m%-38s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)


ALL_BASE := $(shell find $(PROCESSED)/eval -type f -name "*.res" -exec basename {} \;)
RESULTS_FILES := $(addprefix $(PROCESSED)/eval/,$(ALL_BASE))
ALL_BASE := $(subst .res,, $(ALL_BASE))

ALL_RESULTS := $(addsuffix .results.test,$(ALL_BASE))
ALL_RESULTS := $(addprefix $(PROCESSED)/eval/,$(ALL_RESULTS))

NDCG_RESULTS := $(addsuffix .ndcg.result,$(ALL_BASE))
NDCG_RESULTS := $(addprefix $(PROCESSED)/eval/,$(NDCG_RESULTS))

PLOT_DIR := $(PROJECT_ROOT)/viz

TREC_LEVELS := 5 10 15 20 30 100 200 500 1000
NDCG_PLOTS := $(foreach level,$(TREC_LEVELS),$(subst LEVEL,$(level),$(PLOT_DIR)/lastfm_ndcg_cut_LEVEL.pdf))

SURPRISE_PLOTS := diversity.pdf unexpectedness.pdf
SURPRISE_PLOTS := $(addprefix $(PLOT_DIR)/,$(SURPRISE_PLOTS))

.PHONY: all
all: $(NDCG_RESULTS) $(NDCG_PLOTS) $(SURPRISE_PLOTS) $(PROCESSED)/diversity.csv $(PROCESSED)/unexpectedness.csv

$(PROCESSED)/eval/qrels.test: $(TMP)/recos
	$(py) gen_qrels.py \
		--reco-dir=$< \
		--out=$@

$(PROCESSED)/eval/%.results.test: $(PROCESSED)/eval/qrels.test $(PROCESSED)/eval/*.res
	$(py) gen_results.py \
		--input $(filter-out $<,$^) \
		--output-dir=$(PROCESSED)/eval/

$(NDCG_RESULTS): $(PROCESSED)/eval/%.ndcg.result: $(PROCESSED)/eval/%.results.test
	trec_eval \
		-q \
		-m ndcg_cut \
		$(PROCESSED)/eval/qrels.test \
		$< \
	| tail -n 9 > $@

$(NDCG_PLOTS) &: $(NDCG_RESULTS)
	Rscript -e 'renv::run("./01_eval_ndcg.R")'

$(PROCESSED)/diversity.csv $(PROCESSED)/unexpectedness.csv &: $(RESULTS_FILES)
	$(py) acoustic_features.py \
		--user-profile-dir=$(TMP) \
		--reranked-recos $(PROCESSED)/eval/*.res \
		--base-reco-dir=$(TMP)/recos \
		--track-features=$(PROCESSED)/tracks_with_features.csv \
		--out-dir=$(PROCESSED)

$(SURPRISE_PLOTS) &: $(PROCESSED)/diversity.csv $(PROCESSED)/unexpectedness.csv
	Rscript -e 'renv::run("./02_eval_surprise.R")'

# end
