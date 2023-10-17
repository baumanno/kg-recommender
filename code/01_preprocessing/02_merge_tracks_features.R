library(tidyverse)

# Setup ------------------------------------------------------------------------

here::i_am("code/01_preprocessing/02_merge_tracks_features.R")

# Utility functions -------------------------------------------------------

scale_min_max <- function(x, a, b) {
  stopifnot(
    is.numeric(x),
    is.numeric(a),
    is.numeric(b),
    b > a
  )

  x_std <- (x - min(x)) / (max(x) - min(x))
  return(x_std * (b - a) + a)
}

# Load data ---------------------------------------------------------------

tracks <- vroom::vroom(
  here::here("data/processed/artist_track_genres.csv"),
  skip = 1,
  col_names = c("compound", "t_name", "a_id", "a_name", "genres"),
  col_types = "ccccc"
)

acoustic_features <- vroom::vroom(
  here::here("data/raw/acoustic_features_lfm_id.tsv"),
  col_types = "cddddddddddd"
) |>
  rename(t_id = "track_id")


# Glimpse data ------------------------------------------------------------

glimpse(tracks)
glimpse(acoustic_features)

# Wrangle data ------------------------------------------------------------

# Remove acoustic features we won't need, and re-scale tempo from BPM into [0,1]
acoustic_features <- acoustic_features |>
  select(-key, -mode, -loudness) |>
  mutate(tempo = scale_min_max(tempo, 0, 1))

# Join the features with the tracks to get artist (name, id), track (name, id),
# genres, and features.
# Then select all distinct tracks by compound ID.
tracks_with_features <- tracks |>
  drop_na() |>
  mutate(grouper = compound) |>
  separate_longer_delim(compound, "_") |>
  inner_join(acoustic_features, by = join_by(compound == t_id)) |>
  select(-compound) |>
  rename(compound = grouper) |>
  distinct(compound, .keep_all = TRUE)

# Write data --------------------------------------------------------------

write_csv(
  tracks_with_features,
  here::here("data/processed/tracks_with_features.csv")
)
