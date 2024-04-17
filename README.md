# Companion repository for "How to Surprisingly Consider Recommendations? A KG-based Approach Relying on Complex Network Metrics"

This repository provides code and data to accompany the publication.
The two subtrees `lastfm-KG` and `netflix-KG` contain code for generating recommendations through the proposed framework, and the experimental evaluation.

## Setup

A recent Python environment is assumed (>= 3.11).

Set up a virtual environment in the project root and install the required dependencies:

``` bash
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
# or use the provided make target:
$ # make .venv
```

Some parts of the data analysis, as well as plotting require a recent version of R.
This project uses [renv](https://rstudio.github.io/renv/index.html) for managing dependencies on R-packages.
The [docs](https://rstudio.github.io/renv/articles/renv.html#collaboration) explain how the workflow goes; if you load up the project in RStudio, everything should work out of the box, and you should be prompted to pull in all dependencies.

If you use R standalone, just fire up R in the project root; renv should bootstrap itself and call `renv::restore()` automatically.

### Versions used for publication

``` bash
$ python --version
Python 3.11.8
$ R --version
R version 4.3.3 (2024-02-29) -- "Angel Food Cake"
```


## Data

This repository provides intermediate data collected during the experiments as xz-compressed files.
Run the following make target to extract all data:

```bash
$ make uncompress
```

