library(tidyverse)
library(patchwork)

# Setup -------------------------------------------------------------------

here::i_am("code/09_plots/02_user_sample_stats.R")

# Utility functions -------------------------------------------------------

geom_boxplot_pretty <- purrr::partial(geom_boxplot, colour = "#999999", alpha = .8, fill = "lightblue")
geom_hist_pretty <- purrr::partial(geom_histogram, colour = "white", alpha = .8, fill = "lightblue")

# Load data ---------------------------------------------------------------

df_sampled <- read_csv(here::here("data/processed/user_sample.csv"))

hs <- df_sampled |>
  ggplot() +
  geom_hist_pretty(aes(x = count), binwidth = 500) +
  scale_x_continuous(labels = scales::label_number_auto()) +
  scale_y_log10(labels = scales::label_log(), limits = c(1, 1e2)) +
  xlab("# unique tracks") +
  ylab("n") +
  theme_minimal()

bs <- df_sampled |>
  ggplot() +
  geom_boxplot_pretty(aes(y = count)) +
  scale_y_log10(labels = scales::label_log(), limits = c(1, 1e4)) +
  scale_x_continuous(labels = NULL) +
  theme_minimal() +
  ylab("# unique tracks")

ps <- hs + bs + plot_annotation(
  title = "Distribution of user-sample",
  caption = "y-axes log-scaled",
  tag_levels = "a",
  tag_prefix = "(",
  tag_suffix = ")"
)

ggsave(filename = here::here("viz/users/02_user_sample_stats.pdf"), ps, height = 4, width = 6)