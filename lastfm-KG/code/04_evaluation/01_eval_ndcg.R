library(tidyverse)
library(tidytext)

here::i_am("lastfm-KG/code/04_evaluation/01_eval_ndcg.R")

data_path <- here::here("lastfm-KG/data/processed/eval/")

files <- dir(data_path, pattern = "*.ndcg.result$")

df <-
  tibble(filename = files) |>
  mutate(contents = purrr::map(filename, ~ read_table(file.path(data_path, .), col_names = c("cut", "what", "ndcg"), col_types = "ccd"))) |>
  unnest(contents) |>
  separate_wider_delim(filename, delim = ".", names = c("metric"), too_many = "drop") |>
  separate_wider_regex(metric, c(metric = ".*", "_", order = ".*")) |>
  group_by(order) |>
  arrange(ndcg, .by_group = TRUE) |>
  mutate(o = row_number())

for (cutlevel in unique(df$cut)) {
  p <- df |>
    filter(cut == cutlevel) |>
    ggplot() +
    geom_col(aes(x = reorder_within(metric, o, order), y = ndcg)) +
    facet_wrap(~order, scales = "free_x") +
    scale_x_reordered() +
    xlab("metric") +
    theme(axis.text.x = element_text(angle = 90, hjust = 1, vjust = .5))
  ggsave(filename = paste0(here::here("lastfm-KG/data/res/"), cutlevel, ".pdf"), plot = p, dpi = 300, width = 6, height = 4)
}
