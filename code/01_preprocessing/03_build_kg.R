library(tidyverse)

# Setup ------------------------------------------------------------------------

here::i_am("code/01_preprocessing/03_build_kg.R")

# Utility functions -------------------------------------------------------

# Load data ---------------------------------------------------------------

df <- vroom::vroom(here::here("data/processed/tracks_with_features.csv"))

# Glimpse data ------------------------------------------------------------

glimpse(df)

message("Collisions between artist- and track-ID:")
df |>
  filter(a_id == compound)

message("Collisions between artist- and track-name:")
df |>
  filter(a_name == t_name)

# Observations:
# - some IDs collide between artist and track,
# - some names of artists match the titles of tracks
#
# Because the name-collisions are more and more difficult to avoid, we
# decide to resolve ID collisions instead by simply prefixing the track-ID with
# the prefix "t_" (see next section).


# Build edgelist ----------------------------------------------------------

# prefix the track-ID to avoid collisions with artist-ID
df <- df |>
  mutate(compound = sprintf("t_%s", compound))

# Build an edgelist for artist -> track relations.
# These edges carry a "relation"-attribute with the value "artist".
edgelist_tracks_artists <- df |>
  select(source = a_id, target = compound) |>
  distinct(source, target) |>
  mutate(relation = "artist")

# Build an edgelist for track -> genre relations.
# These edges carry a "relation"-attribute with the value "genre".
edgelist_tracks_genres <- df |>
  select(source = compound, target = genres) |>
  separate_longer_delim(target, "|") |>
  distinct(source, target) |>
  mutate(relation = "genre")

edgelist <- bind_rows(edgelist_tracks_artists, edgelist_tracks_genres)


# Build vertex-attributes -------------------------------------------------

# Note: this dataframe contains three columns:
# - "name" MUST match the names given in the edgelist,
# - "human_name" is the name of the thing, i.e., NOT the ID, but the artist- or
#   track-name,
# - "type" indicates the type of the vertex: artist, track, or genre

artist_v_attr <- df |>
  select(a_id, human_name = a_name) |>
  rename(name = a_id) |>
  distinct(name, .keep_all = TRUE) |>
  mutate(type = "artist")

track_v_attr <- df |>
  select(compound, human_name = t_name) |>
  rename(name = compound) |>
  distinct(name, .keep_all = TRUE) |>
  mutate(type = "track")

# For genres, the "graph-name" and the human-readable name are identical.
# To conform to the interface of the attribute-dataframe, we simply duplicate
# the respective column.
genre_v_attr <- df |>
  select(genres) |>
  separate_longer_delim(genres, "|") |>
  distinct(genres, .keep_all = TRUE) |>
  mutate(
    name = genres,
    human_name = genres,
    type = "genre",
    .keep = "none"
  )

vertex_attr <- bind_rows(artist_v_attr, track_v_attr, genre_v_attr)

# Build graph -------------------------------------------------------------
g <- make_empty_graph()
for (i in 1:10) {
  row <- edgelist[i, ]
  print(c(row$source, row$target))
  g <- add_edges(g, c(row$source, row$target))  
}

# Write data --------------------------------------------------------------

write_graph(g, here::here("data/processed/kg_artist_track_genres.gml"), format = "gml")

