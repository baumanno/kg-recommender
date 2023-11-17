########################################################################
# DISCLAIMER                                                           #
#                                                                      #
# This Makefile is untested. It was written using shell history and    #
# a decent sprinkle of intuition. I never tested it, as it would run   #
# longer than I have any more patience for.                            #
# -- baumanno, 2023-11-15 20:07
########################################################################

SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

.DEFAULT_GOAL := help

# Display help for targets when calling `make` or `make help`.
# To add help-tags to new targets, place them after the target-name (and
# dependencies) following a `##`. See the targets in this file for examples.
.PHONY: help
help: ## Display this help section
	@awk 'BEGIN {FS = ":.*?## "} /^[.a-zA-Z\$$/]+.*:.*?##\s/ {printf "\033[36m%-38s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: all
all: tabulate ## Run all targets

DATADIR:=../../../data

$(DATADIR)/tmp/trackids_with_features.csv: ## Create the mapping of single-ID to compound
	Rscript ./01_write_track_ids.R

$(DATADIR)/processed/les_tracks_with_features.csv: $(DATADIR)/tmp/trackids_with_features.csv ## Keep all listening events on tracks for which features exist
	./02_filter_les.sh \
		$(DATADIR)/raw/LFM_1b_LEs.txt.xz \
		$(DATADIR)/tmp/trackids_with_features.csv \
		$(DATADIR)/processed/les_tracks_with_features.csv

$(DATADIR)/tmp/per_user_counts/: $(DATADIR)/tmp/trackids_with_features.csv $(DATADIR)/processed/les_tracks_with_features.csv ## Extract profiles with only the tracks for which features exist
	mkdir -p $(DATADIR)/tmp/per_user_counts
	./03_tracks_per_user.sh \
		$(DATADIR)/tmp/trackids_with_features.csv \
		$(DATADIR)/processed/les_tracks_with_features.csv \
		$(DATADIR)/tmp/per_user_counts

.PHONY: tabulate
tabulate: $(DATADIR)/tmp/per_user_counts/ ## Aggregate per-user totals and per-user per-track playcounts
	./04_tabulate_counts.sh \
		$(DATADIR)/tmp/per_user_counts \
		$(DATADIR)/processed/total_tracks_per_user.csv

.PHONY: clean
clean: ## Run cleanup routines
	$(error Not implemented)

.PHONY: test
test: ## Run tests
	$(error Not implemented)
