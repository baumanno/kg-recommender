library(tidyverse)
library(itertools)
library(foreach)
library(doParallel)

# Setup -------------------------------------------------------------------

here::i_am("code/01_preprocessing/04_user_profiles.R")

# Utility functions -------------------------------------------------------

# Load data ---------------------------------------------------------------

tracks_features <- read_csv(here::here("data/processed/tracks_with_features.csv"))

# Glimpse data ------------------------------------------------------------

glimpse(tracks_features)

# Wrangle data ------------------------------------------------------------

tracks <- tracks_features |>
  mutate(grouper = compound) |>
  separate_longer_delim(compound, "_") |>
  rename(track_id = compound) |>
  select(grouper, track_id)
tracks |> write_csv(here::here("data/tmp/trackids_with_features.csv"))
track_ids <- pull(tracks, "track_id")
chunksize <- 1e5

f <- file(here::here("data/raw/LFM_1b_LEs.txt"), open = "rt")
it <- enumerate(ichunk(f, chunkSize = chunksize))
# purrr::map(it, \(x) joiner(x, tracks = track_ids))
# the_df <- lapply(it, \(x) joiner(x, tracks = track_ids))
filepath <- here::here("data/tmp/les/")

foreach::foreach(
  thing = it,
  .packages = c("dplyr", "readr"),
  .inorder = FALSE,
  .noexport = c("tid", "albid"),
  .export = c("track_ids", "filepath"),
  .combine = c,
  .multicombine = TRUE
  ) %do% {
  # joiner(thing$index, thing$value, tracks = track_ids, path = filepath)
  # print("hello")
  cat("test", file = "/tmp/test")
  
  filename <- paste0(filepath,"les_", thing$index, ".csv")
  # 
  thing$value |>
    paste(collapse = "\n") |>
    readr::read_tsv(
      col_names = c("userid", "aid", "albid", "tid", "timestamp"),
      col_types = "ccccc",
      col_select = c(-albid)
    ) |>
    dplyr::filter(tid %in% track_ids) |>
    readr::write_csv(file = filename)

  return(NULL)
  # print("done")
  # flush.console()
}
close(f); rm(f); rm(it); gc()

les <- vroom::vroom(here::here("data/raw/LFM_1b_LEs.txt.xz"), n_max = 1e5,       col_names = c("userid", "aid", "albid", "tid", "timestamp"),
                    col_types = "ccccc",
                    col_select = c(-albid))

les <- les |>
  distinct()

les_on_known_tracks <- les[les$tid %in% tracks$track_id, ]

les_with_compound <- les_on_known_tracks |>
  inner_join(
    tracks,
    by = join_by(tid == track_id),
    relationship = "many-to-many"
  ) |>
  select(-tid) |>
  rename(compound = grouper)

les_with_playcounts <- les_with_compound |>
  group_by(userid) |>
  add_count(compound, name = "num_listens")

les_with_num_tracks <- les_with_compound |>
  distinct(userid, compound) |>
  add_count(userid, name = "num_tracks_listened")

# Write data --------------------------------------------------------------

write_csv(les_with_playcounts, here::here("data/processed/les_with_playcounts.csv"))
write_csv(les_with_num_tracks, here::here("data/processed/les_with_num_tracks_listened.csv"))


