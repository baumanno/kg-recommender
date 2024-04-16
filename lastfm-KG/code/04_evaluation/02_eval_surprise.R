library(ggplot2)
library(tidyverse)

# Setup -------------------------------------------------------------------

here::i_am("lastfm-KG/code/04_evaluation/02_eval_surprise.R")

data_path <- here::here("lastfm-KG/data/processed")
out_path <- here::here("lastfm-KG/viz")

# Diversity: Wrangle data -------------------------------------------------

diversity <- read_csv(here::here(data_path, "diversity.csv"), col_types = "cccd")

diversity <- diversity |>
  group_by(metric) |>
  summarise(mean = mean(value)) |>
  separate_wider_regex(metric, c(metric = ".*", "_", order = ".*"), too_few = "align_start")

# ugly hack to duplicate the rows for base and profile, so they show up in both asc/desc panels
diversity_fixed_for_base_and_profile <- diversity |>
  filter(is.na(order)) |>
  slice(rep(1:2, times = 2)) |>
  mutate(order = c(rep("asc", 2), rep("desc", 2))) |>
  bind_rows(diversity) |>
  drop_na(order) |>
  distinct() |>
  mutate(color = case_when(
    metric == "base" | metric == "profile" ~ "#ff0000",
    T ~ NA
  )) |>
  arrange(mean) |>
  mutate(o = row_number())

# Diversity: Plotting -----------------------------------------------------

p <- diversity_fixed_for_base_and_profile |> 
  ggplot() +
  geom_col(aes(y = tidytext::reorder_within(metric, o, order), x = mean, fill = color)) +
  tidytext::scale_y_reordered() +
  scale_fill_discrete(guide="none") +
  facet_wrap(~order, scales = "free_y") +
  labs(title = "Diversity") +
  ylab("metric")

ggsave(filename = here::here(out_path, "diversity.pdf"), plot = p, dpi = 300, width = 6, height = 4)

# Unexpectedness: Wrangle data --------------------------------------------

unexpectedness <- read_csv(here::here(data_path, "unexpectedness.csv"), col_types = "cccd")

unexpectedness <- unexpectedness |>
  group_by(metric) |>
  summarise(mean = median(value)) |>
  separate_wider_regex(metric, c(metric = ".*", "_", order = ".*"), too_few = "align_start")

# ugly hack, see above
unexpectedness_fixed_for_base <- unexpectedness |>
  filter(is.na(order)) |>
  slice(rep(1, times = 2)) |>
  mutate(order = c(rep("asc", 1), rep("desc", 1))) |>
  bind_rows(unexpectedness) |>
  drop_na(order) |>
  distinct() |>
  mutate(color = case_when(
    metric == "base" | metric == "profile" ~ "#ff0000",
    T ~ NA
  )) |>
  arrange(mean) |>
  mutate(o = row_number())

# Unexpectedness: Plotting ------------------------------------------------

p <- unexpectedness_fixed_for_base |> 
  ggplot() +
  geom_col(aes(y = tidytext::reorder_within(metric, o, order), x = mean, fill = color)) +
  tidytext::scale_y_reordered() +
  scale_fill_discrete(guide="none") +
  facet_wrap(~order, scales = "free_y") +
  labs(title = "Unexpectedness") +
  ylab("metric")

ggsave(filename = here::here(out_path, "unexpectedness.pdf"), plot = p, dpi = 300, width = 6, height = 4)
