library(tidyverse)
library(tidytext)

here::i_am("lastfm-KG/code/04_evaluation/02_eval_surprise.R")

df_div <- read_csv("./lastfm-KG/code/04_evaluation/diversity.csv", col_types = "cccd")

df_div <- df_div |>
  group_by(metric) |>
  summarise(mean = mean(value)) |>
  separate_wider_regex(metric, c(metric = ".*", "_", order = ".*"), too_few = "align_start")
p <- df_div |>
  filter(is.na(order)) |>
  slice(rep(1:2, times = 2)) |>
  mutate(order = c(rep("asc", 2), rep("desc", 2))) |>
  bind_rows(df_div) |>
  drop_na(order) |>
  distinct() |>
  mutate(color = case_when(
    metric == "base" | metric == "profile" ~ "#ff0000",
    T ~ NA
  )) |>
  arrange(mean) |>
  mutate(o = row_number()) |>
  ggplot() +
  geom_col(aes(y = reorder_within(metric, o, order), x = mean, fill = color)) +
  scale_y_reordered() +
  facet_wrap(~order, scales = "free_y") +
  labs(title = "Diversity") +
  ylab("metric")
ggsave(filename = paste0(here::here("lastfm-KG/data/res/"), "diversity.pdf"), plot = p, dpi = 300, width = 6, height = 4)


df_unexp <- read_csv("./lastfm-KG/code/04_evaluation/unexpectedness.csv", col_types = "cccd")

df_unexp <- df_unexp |>
  group_by(metric) |>
  summarise(mean = median(value)) |>
  arrange(-mean) |>
  separate_wider_regex(metric, c(metric = ".*", "_", order = ".*"), too_few = "align_start")
p <- df_unexp |>
  filter(is.na(order)) |>
  slice(rep(1, times = 2)) |>
  mutate(order = c(rep("asc", 1), rep("desc", 1))) |>
  bind_rows(df_unexp) |>
  drop_na(order) |>
  distinct() |>
  mutate(color = case_when(
    metric == "base" | metric == "profile" ~ "#ff0000",
    T ~ NA
  )) |>
  arrange(mean) |>
  mutate(o = row_number()) |>
  ggplot() +
  geom_col(aes(y = reorder_within(metric, o, order), x = mean, fill = color)) +
  scale_y_reordered() +
  facet_wrap(~order, scales = "free_y") +
  labs(title = "Unexpectedness") +
  ylab("metric")
ggsave(filename = paste0(here::here("lastfm-KG/data/res/"), "unexpectedness.pdf"), plot = p, dpi = 300, width = 6, height = 4)
