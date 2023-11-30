import argparse
import csv
import lzma
import logging
import os
import pathlib
import sys
import typing

import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class Record(typing.NamedTuple):
    compound: str
    track_id: str
    track_name: str
    artist_id: str
    artist_name: str
    genres: str


class ListeningEvent(typing.NamedTuple):
    user_id: str
    artist_id: str
    album_id: str
    track_id: str
    timestamp: str


def read_genres(genres_path: pathlib.Path) -> pd.DataFrame:
    data = []
    with open(genres_path, "r") as f:
        next(f)
        # format: track_id TAB track TAB artist_id TAB artist TAB LFM-2b_playcount TAB genre
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue

            # column 1
            #   - track-IDs joined by `_`; all IDs that refer to the same track
            # column 5
            #   - LFM2b playcount, which we don't need and hence drop
            # columns 6+
            #   - (genre, weight) tuples separated by tabs; aggregate in a list and clean later
            track_id, track_name, artist_id, artist_name, _, *genres = line.split("\t")

            # genre names are at odd indices, weights at even indices; only keep the odds
            genres = {g.strip() for g in genres[0::2]}
            genres = "|".join(genres)

            for single in track_id.split("_"):
                data.append(
                    Record(
                        track_id, single, track_name, artist_id, artist_name, genres
                    )._asdict()
                )
    df = pd.DataFrame(data)
    df["track_id"] = df["track_id"].astype("int64")

    return df


def run(
    genres_path: pathlib.Path,
    features_path: pathlib.Path,
    lfm_path: pathlib.Path,
    features_out: pathlib.Path,
    lfm_out: pathlib.Path,
) -> int:
    logger = logging.getLogger(__name__)

    if lfm_path.suffix != ".xz":
        logger.critical(
            f"Expected xz-compressed LFM file, got {lfm_path.suffix}. Aborting"
        )
        return os.EX_DATAERR

    logger.info("Reading genre-data...")
    genres = read_genres(genres_path)
    logger.info("done!")

    logger.info("Reading feature-data...")
    features = pd.read_csv(features_path, sep="\t").dropna()
    logger.info("done!")

    logger.info("Joining data...")
    df = pd.merge(genres, features, on="track_id")
    logger.info("done!")

    logger.info("Normalizing BPM...")

    df["tempo"] = MinMaxScaler(feature_range=(0, 1)).fit_transform(
        df["tempo"].values.reshape(-1, 1).astype(float)
    )

    logger.info("done!")

    logger.info(f"Writing feature data to {features_out}")
    df.to_csv(features_out, index=False)
    logger.info("done!")

    # Writing this file is costly, so if it exists, just exit early with success
    if lfm_out.exists():
        logger.warning(f"{lfm_out} exists. Early exit")
        return os.EX_OK

    logger.info("Building track-compound index...")
    track_id_to_compound = dict(zip(df["track_id"].astype(str), df["compound"]))
    logger.info("done!")

    logger.info("Filtering listening events to featureset...")
    n_records = 0
    with lzma.open(lfm_path, "rt") as fin:

        with open(lfm_out, "w") as fout:
            writer = csv.DictWriter(fout, fieldnames=ListeningEvent._fields)
            writer.writeheader()

            for line in fin:
                if n_records % 1_000_000 == 0:
                    logger.info(f"wrote {n_records} records so far")
                line = line.strip()
                if len(line) == 0:
                    continue
                record = ListeningEvent._make(line.split("\t"))

                try:
                    record = record._replace(
                        track_id=track_id_to_compound[record.track_id]
                    )
                except KeyError:
                    continue

                writer.writerow(record._asdict())
                n_records += 1

    logger.info(f"Done. Wrote {n_records} lines to {lfm_out}")

    return os.EX_OK


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s",
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--genres", type=pathlib.Path, required=True)
    parser.add_argument("--features", type=pathlib.Path, required=True)
    parser.add_argument("--lfm", type=pathlib.Path, required=True)
    parser.add_argument("--features-out", type=pathlib.Path, required=True)
    parser.add_argument("--lfm-out", type=pathlib.Path, required=True)
    args = parser.parse_args()

    sys.exit(run(args.genres, args.features, args.lfm, args.features_out, args.lfm_out))
