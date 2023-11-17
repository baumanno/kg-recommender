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

# Plot `count` distributions ----------------------------------------------

h <- df_totals |>
  ggplot() +
  geom_hist_pretty(aes(x = count), binwidth = 500) +
  scale_x_continuous(labels = scales::label_number_auto()) +
  scale_y_log10(labels = scales::label_log()) +
  xlab("# unique tracks") +
  ylab("n") +
  theme_minimal()

b <- df_totals |>
  ggplot() +
  geom_boxplot_pretty(aes(y = count)) +
  scale_y_log10(labels = scales::label_log()) +
  scale_x_continuous(labels = NULL) +
  theme_minimal() +
  ylab("# unique tracks")

p <- h + b + plot_annotation(
  title = "Distribution of unique tracks per user",
  caption = "y-axes log-scaled",
  tag_levels = "a",
  tag_prefix = "(",
  tag_suffix = ")"
)

ggsave(filename = here::here("viz/users/01_user_track_distribution.pdf"), p, height = 4, width = 6)
