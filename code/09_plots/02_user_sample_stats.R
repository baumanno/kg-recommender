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

features <- read_csv(here::here("data/processed/tracks_with_features.csv"))

df_sampled <- read_csv(here::here("data/processed/user_sample_playcounts.csv"), col_types = "ccd")

feats <- df_sampled |> 
  group_by(uid) |> 
  nest(data = compound:count) |> 
  ungroup() |> 
  slice_sample(n = 3) |>
  unnest(data) |> 
  left_join(features, by = join_by(compound)) |> 
  pivot_longer(danceability:tempo, names_to = "feature") |> 
  ggplot() +
  geom_boxplot(aes(x = feature, y = value, fill = uid), outlier.alpha = .2, alpha = .6, colour = "#666666") +
  coord_flip() +
  scale_fill_brewer(type = "qual", palette = "Dark2") +
  ylab("feature name") +
  plot_annotation(
    title = "Feature distribution for sample of users",
    caption = "All values normalized to [0,1]"
  )

ggsave(filename = here::here("viz/users/03_subsampled_feature_comparison.pdf"), feats, height = 4, width = 6, dpi = 300)
