library(tidyverse)

# Setup -------------------------------------------------------------------

here::i_am("code/01_preprocessing/04_user_profiles/01_write_track_ids.R")

# Wrangle data ------------------------------------------------------------

read_csv(here::here("data/processed/tracks_with_features.csv")) |>
  mutate(grouper = compound) |>
  separate_longer_delim(compound, "_") |>
  rename(track_id = compound) |>
  select(grouper, track_id) |>
  write_csv(here::here("data/tmp/trackids_with_features.csv"))
