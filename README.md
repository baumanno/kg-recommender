# KG-based Recommendations

## Getting started

The `Makefile` provides several useful targets, see them all by running `make`
without arguments in your terminal:

```bash
$ make
```

### Set up virtual environment and install dependencies

```bash
$ make .venv
$ source .venv/bin/activate
```

### Optional: set up renv (for R)

**Skip this if you do not require R**

This project uses [renv](https://rstudio.github.io/renv/index.html) for
managing dependencies on R-packages. The [docs](https://rstudio.github.io/renv/articles/renv.html#collaboration)
explain how the workflow goes; if you load up the project in RStudio,
everything should work out of the box, and you should be prompted to pull in
all dependencies.

If you use R standalone, just fire up R in the project root; renv should
bootstrap itself and call `renv::restore()` automatically.

### Uncompress data

The raw data is quite large, so this repo provides
[xz-compressed](https://en.wikipedia.org/wiki/XZ_Utils) files for all relevant
dumps. Uncompress them with:

```bash
$ make uncompress
```

### KG stats

A dump of the knowledge graph is contained in
`./data/processed/kg_artist_track_genres.graphml`.  To see how to handle this
graph in [igraph](https://python.igraph.org/en/stable/), check the script in
`./code/02_exploration/01_kg_overview.py`. Run the script to see some
descriptive stats:

```bash
$ source .venv/bin/activate   # activate the virtual environment, if not done already
$ python code/02_exploration/01_kg_overview.py --help
```
Example:
```bash
$ python code/02_exploration/01_kg_overview.py \
    --graphml ./data/processed/kg_artist_track_genres.graphml \
    --vertex "Somebody That I Used to Know"
```

## Documentation of datasets

### General note about track-IDs

It turns out that in the [original LFM-1b dataset](http://www.cp.jku.at/datasets/LFM-1b/),
several track-IDs were used to refer to the same "logical" song
(no, not [this one](https://www.youtube.com/watch?v=pP8iUyb9Gn8)).
Therefore, the authors of [EmoMTB](https://doi.org/10.1007/s13735-023-00275-8)
decided to accumulate all IDs referring to the same track, joined by an
underscore. We refer to this ID-string as the "compound ID".

Therefore, keep in mind that the relation "track-name -> track-ID" is
one-to-many. This has already been considered for preprocessing and
KG-building.

To avoid collisions between artist- and track-IDs, all compound track-IDs are
prefixed with `t_`.

### `data/raw/artist_track_genres.txt`

#### Provenance

Submitted to Baumann and Schoenfeld privately from Markus Schedl, one of the
authors of [EmoMTB](https://doi.org/10.1007/s13735-023-00275-8).

No known publicly accessible URI.

#### Description

Serves as input to `code/01_preprocessing/flatten_artist_track_genre.py`, which
turns it into a nicer CSV-file (see next section).

### `data/processed/artist_track_genre.csv`

#### Provenance

Processed version of `data/raw/artist_track_genres.txt` (see previous section).

#### Description

Contains tracks performed by artists, along with genre annotations.
One row per observation.

| Field       | Description                                                                  | Example                                      |
|-------------|------------------------------------------------------------------------------|----------------------------------------------|
| `compound`  | All LastFM-IDs referring to this single track                                | `11393952_7208083_21104_30530776`            |
| `track`     | The name of the track                                                        | `Somebody That I Used to Know`               |
| `artist_id` | The LastFM Artist-ID                                                         | `3085`                                       |
| `artist`    | The name of the artist                                                       | `Gotye`                                      |
| `genres`    | A pipe-delimeted string of all genres assigned to this track by LastFM users | `pop\|indiepop\|rock\|singersongwriter\|...` |

### `data/raw/acoustic_features_lfm_id.tsv`

#### Provenance

[Eva Zangerle 2019. Culture-Aware Music Recommendation Dataset. Zenodo.](https://doi.org/10.5281/zenodo.3477841)

#### Description

> This file contains the following columns (cf. Spotify Audio Feature Description for further description of acoustic features):
>
>   * track_id: LFM-1b's id for the track (int)
>   * danceability: how suitable the track is for dancing (float, [0,1])
>   * energy: perceptual measure of intensity and activity (float, [0,1])
>   * key: key of the track (int, pitch class notation)
>   * loudness: loudness in decibels (float)
>   * mode: major (1) or minor (0) (int)
>   * speechiness: presence of spoken words (float, [0,1])
>   * acousticness: confidence whether track is acoustic (float, [0,1])
>   * instrumentalness: likelihood that track contains no vocals (float, [0,1])
>   * liveness: presence of an audience in recording (float, [0,1])
>   * valence: musical positiveness conveyed (float, [0,1])
>   * tempo: tempo of track in beats per minute (float) Please note that the features for a single track may not be complete as the full information was not provided by Spotify's API.


### `data/processed/tracks_with_features.csv`

#### Provenance

Essentially, an inner join of `artist_track_genre.csv` and
`acoustic_features_lfm_id.tsv` on the field `track_id`.
Due to the join, only tracks with features and genres are retained.

#### Description

All tracks from `artist_track_genre.csv` for which acoustic features are
available in `acoustic_features_lfm_id.tsv`.
Hence, a subset of all tracks for which fine-grained musical features exist;
useful to compare similarity across tracks in terms of acoustic features, e.g.,
tempo, energy, etc.

**Note 1**: the fields `key`, `loudness`, and `mode` from the original dataset
were dropped, as they are not indicative of users' listening behaviour.

**Note 2:** `tempo` is a minmax-normalized value of the traditional BPM-measure, taken
across the entire `acoustic_features_lfm_id.tsv` dataset

**Note 3:** according to Spotify's
[terms of service, Section IV Restrictions, 2a](https://developer.spotify.com/terms#section-iv-restrictions),
it is not allowed "[to use] the Spotify Platform or any Spotify Content to
train a machine learning or AI model or otherwise ingesting Spotify Content
into a machine learning or AI model;"

We may have to check these restrictions if we decide that we are, in fact,
training an ML model using their data.


| Field               | Description                                                                                                                                           | Example                        |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| `t_name`            | The name of the track                                                                                                                                 | `Somebody That I Used to Know` |
| `a_id`              | The LastFM-artist-ID; a unique identifier for artists                                                                                                 | `3085`                         |
| `a_name`            | The name of the artist                                                                                                                                | `Gotye`                        |
| `genres`            | A pipe-separated list of genres assigned to this track                                                                                                | `pop\|indiepop\|rock\|...`     |
| `compound`          | (see above)                                                                                                                                           | (see above)                    |
| 8 acoustic features | Numeric indicators of musical features of the track, see [the docs](https://developer.spotify.com/documentation/web-api/reference/get-audio-features) | 0.374                          |

### `data/processed/kg_artist_track_genres.graphml`

#### Provenance

Built from the existing data using `code/01_preprocessing/03_build_kg.R`.

#### Description

A knowledge graph of artists, tracks, and genres.

| Name         | What   | Description                                                                                                                     | Example                                            |
|--------------|--------|---------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| `relation`   | Edge   | Type of the relation; values: `[artist|genre]`                                                                                  | `artist`                                           |
| `name`       | Vertex | The ID of the thing; artist-IDs for artists, compound-ID for tracks; name of the genre for genres                               | `3085`, `t_11393952_7208083_21104_30530776`, `pop` |
| `human_name` | Vertex | A human-readable name for the thing; artist-names, track-titles, and genres (for genres, `name` and `human_name` are identical) | `Gotye`, `Somebody That I Used to Know`, `pop`     |
| `type`       | Vertex | Type of the vertex; values: `[artist|track|genre]`                                                                              | --                                                 |
| `id`         | Vertex | A generic ID assigned by igraph during export to graphml; carries no domain-information.                                        | `n24237`                                           |

### User profiles

TODO: fill this section with better description of user profiles.