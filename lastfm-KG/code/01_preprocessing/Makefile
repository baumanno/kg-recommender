##
# Data pre-processing for KG recos
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

filtereddata = tracks_with_features.csv les-filtered.csv
filtereddata = $(addprefix $(PROCESSED)/,filtereddata)

NAMES = tracks_with_features.csv les-filtered.csv global_playcounts.csv user_ratings.csv catalog-kg.ttl
FILES = $(addprefix $(PROCESSED)/,$(NAMES))

.PHONY: all
all: $(FILES) .user-subkgs.sentinel

$(filtereddata) &:
	$(py) merge.py \
		--genres=../../data/raw/artist_track_genres.txt \
		--features=../../data/raw/acoustic_features_lfm_id.tsv \
		--lfm=../../data/raw/LFM_1b_LEs.txt.xz \
		--features-out=$(PROCESSED)tracks_with_features.csv \
		--lfm-out=$(PROCESSED)/les-filtered.csv
	# above command doesn't re-write les-filtered.csv if it exists, because it's huge.
	# Thus, we update it's timestamp to indicate the above command ran, to ensure pre-requisites of
	# other targets are recoginzed.
	@touch $(PROCESSED)/les-filtered.csv

$(TMP)/%.hist.csv: $(PROCESSED)/les-filtered.csv
	./split.sh \
		$(PROCESSED)/les-filtered.csv \
		$(TMP)

$(PROCESSED)/global_playcounts.csv: $(TMP)/*.hist.csv
	-rm $@ # Remove the file to prevent duplicates
	./aggregate.sh \
		$(TMP) \
		$@

$(PROCESSED)/user_ratings.csv $(TMP)/*.features.csv &: $(PROCESSED)/global_playcounts.csv $(PROCESSED)/tracks_with_features.csv
	$(py) users.py \
		--user-counts=$< \
		--num-users=1000 \
		--sample-out=$(PROCESSED)/user_sample.csv \
		--tmpdir=$(TMP) \
		--features=$(filter-out $<,$^) \
		--scaled-out=$@

$(PROCESSED)/catalog-kg.ttl: $(PROCESSED)/tracks_with_features.csv
	$(py) kgbuilder.py \
		--input=$< \
		--output=$@

.user-subkgs.sentinel: $(TMP)/*.features.csv
	-mkdir $(TMP)/subkgs
	find $(TMP) -type f -name "*.features.csv" \
		| xargs -n1 basename \
		| awk -F. '{print $$1}' \
		| xargs -I{} $(py) kgbuilder.py --input=$(TMP)/{}.features.csv --output=$(TMP)/subkgs/{}.subkg.ttl
	@touch $@

# end
