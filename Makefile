SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# alias the python- and pip-executables to the ones in the virtual environment
py = $$(if [ -d $(CURDIR)/'.venv' ]; then echo $(CURDIR)/".venv/bin/python3"; else echo "python3"; fi)
pip = $(py) -m pip

RAWDIR = ./data/raw/
PROCESSEDDIR = ./data/processed/
# Raw and processed research data
DATA := $(addprefix $(RAWDIR), acoustic_features_lfm_id.tsv.xz artist_track_genres.txt.xz) \
				$(addprefix $(PROCESSEDDIR), artist_track_genres.csv.xz kg_artist_track_genres.graphml.xz tracks_with_features.csv.xz)
DATA_UNCOMP := $(foreach f, $(DATA), $(basename $(f) .xz))

# The compression tool used; make sure this is installed on your system!
XZ := $(shell command -v xz 2>/dev/null)
ifndef XZ
$(error "xz command not found. Please install")
endif

.DEFAULT_GOAL := help

# Display help for targets when calling `make` or `make help`.
# To add help-tags to new targets, place them after the target-name (and
# dependencies) following a `##`. See the targets in this file for examples.
.PHONY: help
help: ## Display this help section
	@awk 'BEGIN {FS = ":.*?## "} /^[.a-zA-Z\$$/]+.*:.*?##\s/ {printf "\033[36m%-38s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: all
all: .venv ## Run all targets

.venv: requirements.txt ## Set up Python virtualenv
	$(py) -m venv .venv
	$(pip) install -U pip setuptools wheel build
	$(pip) install -U -r requirements.txt
	touch .venv
	@echo "Done! Don't forget to execute \`source .venv/bin/activate\`"

.PHONY: uncompress
uncompress: ## Uncompress research data
	$(XZ) --decompress --keep --verbose $(DATA)
	sha256sum -c ./data/SHASUMS

.PHONY: compress
compress: ## Compress research data
	echo $(DATA_UNCOMP)
	sha256sum $(DATA_UNCOMP) > ./data/SHASUMS
	-$(XZ) --compress --keep --verbose -9 --extreme --threads=0 $(DATA_UNCOMP)

.PHONY: clean
clean: ## Run cleanup routines
	$(error Not implemented)

.PHONY: test
test: ## Run tests
	$(error Not implemented)
