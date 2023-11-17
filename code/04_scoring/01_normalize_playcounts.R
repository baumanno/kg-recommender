library(tidyverse)


# Setup -------------------------------------------------------------------

here::i_am("code/04_scoring/01_normalize_playcounts.R")


# Utility functions -------------------------------------------------------

scale_min_max <- function(x, mi, ma) {
  return(((x - min(x)) / (max(x) - min(x))) * (ma - mi) + mi)
}

# Load data ---------------------------------------------------------------

df <- read_csv(here::here("data/processed/user_sample_playcounts.csv"), col_types = "ccd")

# Glimpse data ------------------------------------------------------------

glimpse(df)

# Wrangle data ------------------------------------------------------------

df_scaled <- df |> 
  group_by(uid) |> 
  mutate(
    score = scale_min_max(count, 1, 1000)
  ) |> 
  ungroup()

df_scaled |> 
  group_by(uid) |> 
  summarise(
    across(score, list(min = min, median = median, mean = mean, max = max)),
    n = n()
  )

df_scaled |> 
  write_csv(here::here("data/processed/user_sample_normalized_playcounts.csv"))
