
library(ggplot2)

# Setup -------------------------------------------------------------------

here::i_am("netflix-KG/code/evaluation/01_eval_ndcg.R")

data_path <- here::here("netflix-KG/data/tmp/")
out_path <- here::here("netflix-KG/viz/")

files <- dir(data_path, pattern = "*.ndcg.result$")

# Wrangle data ------------------------------------------------------------

df <-
  dplyr::tibble(filename = files) |>
  dplyr::mutate(contents = purrr::map(filename, ~ readr::read_table(file.path(data_path, .), col_names = c("cut", "what", "ndcg"), col_types = "ccd"))) |>
  tidyr::unnest(contents) |>
  tidyr::separate_wider_delim(filename, delim = ".", names = c("metric"), too_many = "drop") |>
  tidyr::separate_wider_regex(metric, c(metric = ".*", "_", order = ".*")) |>
  dplyr::group_by(order) |>
  dplyr::arrange(ndcg, .by_group = TRUE) |>
  dplyr::mutate(o = dplyr::row_number())

# Plotting ----------------------------------------------------------------

for (cutlevel in unique(df$cut)) {
  p <- df |>
    dplyr::filter(cut == cutlevel) |>
    ggplot() +
    geom_col(aes(x = tidytext::reorder_within(metric, o, order), y = ndcg)) +
    facet_wrap(~order, scales = "free_x") +
    tidytext::scale_x_reordered() +
    xlab("metric") +
    theme(axis.text.x = element_text(angle = 90, hjust = 1, vjust = .5))
  
  ggsave(filename = paste0(out_path, "netflix_", cutlevel, ".pdf"), plot = p, dpi = 300, width = 6, height = 4)
}
