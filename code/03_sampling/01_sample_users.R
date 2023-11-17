library(tidyverse)

# Setup -------------------------------------------------------------------

here::i_am("code/03_sampling/01_sample_users.R")


# Load data ---------------------------------------------------------------

df_totals <- read_csv(
  here::here("data/processed/total_tracks_per_user.csv"),
  col_names = c("uid", "count"),
  col_types = "cd"
)

# Sample users ------------------------------------------------------------

# Assign a group-label to each observation, indicating which quartile it resides in.
# There are three groups:
#   1: 0 to first quartile (25% of data),
#   2: first to third quartile (50% of data),
#   3: third to fourth quartile (25% of data)
#
df_quantile_groups <- df_totals |>
  mutate(
    grp = (findInterval(count, quantile(count, c(0, .25, .75, 1)), rightmost.closed = TRUE)),
  )

# Assign a new variable indicating how many rows to sample from each group.
# Currently, this samples 150 rows: 50 from the outer quartiles, 100 from the middle.
#
df_sampled <- df_quantile_groups |>
  mutate(
    n = case_match(grp, 1 ~ 25, 2 ~ 100, 3 ~ 25)
  ) |>
  group_by(grp) |>
  nest(data = c(uid, count)) |>
  mutate(smpl = map2(data, n, \(x, y) { set.seed(1234); slice_sample(x, n = y) })) |>
  select(-data) |> 
  unnest(smpl) |> 
  ungroup()
  

df_sampled |> 
  select(uid, count) |> 
  write_csv(here::here("data/processed/user_sample.csv"))
