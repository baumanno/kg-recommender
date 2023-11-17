library(tidyverse)
library(patchwork)

# Setup -------------------------------------------------------------------

here::i_am("code/02_exploration/02_user_stats.R")

# Utility functions -------------------------------------------------------

geom_boxplot_pretty <- purrr::partial(geom_boxplot, colour = "#999999", alpha = .8, fill = "lightblue")
geom_hist_pretty <- purrr::partial(geom_histogram, colour = "white", alpha = .8, fill = "lightblue")

# Read data ---------------------------------------------------------------

df_totals <- read_csv(
  here::here("data/processed/total_tracks_per_user.csv"),
  col_names = c("uid", "count"),
  col_types = "cd"
)

# Glimpse data ------------------------------------------------------------

summary(df_totals$count)
n_distinct(df_totals$uid)
