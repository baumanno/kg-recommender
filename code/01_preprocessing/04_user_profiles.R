library(tidyverse)

# Setup -------------------------------------------------------------------

here::i_am("code/01_preprocessing/04_user_profiles.R")

# Utility functions -------------------------------------------------------

# Load data ---------------------------------------------------------------

tracks_features <- read_csv(here::here("data/processed/tracks_with_features.csv"))

les <- read_tsv(
  here::here("data/raw/LFM_1b_LEs.txt.xz"),
  n_max = 1E6,
  col_names = c("userid", "aid", "albid", "tid", "timestamp"),
  col_types = "ccccc",
  col_select = c(-albid)
)

# Glimpse data ------------------------------------------------------------

glimpse(tracks_features)
glimpse(les)

# Wrangle data ------------------------------------------------------------

tracks <- tracks_features |>
  mutate(grouper = compound) |>
  separate_longer_delim(compound, "_") |>
  rename(track_id = compound) |>
  select(grouper, track_id)

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


