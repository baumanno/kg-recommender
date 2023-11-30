##
# LastFM KG
#
# @file
# @version 0.1

SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
.DEFAULT_GOAL := help

DATADIR := ./data
PROCESSEDDIR := $(DATADIR)/processed

NAMES := catalog-kg.ttl user_ratings.csv global_playcounts.csv user_ratings.csv user_sample.csv les-filtered.csv tracks_with_features.csv
PROCESSED_DATA := $(addprefix $(PROCESSEDDIR)/,$(NAMES))
PROCESSED_COMP := $(addsuffix '.xz',$(PROCESSED_DATA))

# The compression tool used; make sure this is installed on your system!
XZ := $(shell command -v xz 2>/dev/null)
ifndef XZ
$(error "xz command not found. Please install")
endif

# Display help for targets when calling `make` or `make help`.
# To add help-tags to new targets, place them after the target-name (and
# dependencies) following a `##`. See the targets in this file for examples.
.PHONY: help
help: ## Display this help section
	@awk 'BEGIN {FS = ":.*?## "} /^[.a-zA-Z\$$/]+.*:.*?##\s/ {printf "\033[36m%-38s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: uncompress
uncompress: ## Uncompress research data
	$(XZ) --decompress --keep --verbose $(PROCESSED_COMP)
	tar xJf $(PROCESSEDDIR)/recos.tar.xz
	tar xJf $(PROCESSEDDIR)/subkgs.tar.xz

.PHONY: compress
compress: ## Compress research data
	-$(XZ) --compress --keep --verbose -9 --extreme --threads=0 $(PROCESSED_DATA)
	tar cJf $(PROCESSEDDIR)/recos.tar.xz $(PROCESSEDDIR)/recos
	tar cJf $(PROCESSEDDIR)/subkgs.tar.xz $(PROCESSEDDIR)/subkgs

# end
