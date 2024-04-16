import csv
import logging
import os
import pathlib
import sys
from argparse import ArgumentParser
from collections import defaultdict
from typing import NamedTuple

import numpy as np
import numpy.typing as npt
import pandas as pd
from sklearn.metrics.pairwise import cosine_distances


def diversity(items: npt.NDArray[np.float64]):
    sum = np.sum(cosine_distances(items))
    # correct for counting each reco twice
    factor = len(items) * (len(items) - 1)
    return (1 / factor) * sum


def unexpectedness(
    profile_vectors: npt.NDArray[np.float64], reco_vectors: npt.NDArray[np.float64]
):
    sum = np.sum(cosine_distances(profile_vectors, reco_vectors))

    return (1 / (len(profile_vectors) * len(reco_vectors))) * sum


def run(
    user_profile_dir: pathlib.Path,
    reranked_reco_files: list[pathlib.Path],
    base_reco_dir: pathlib.Path,
    track_features_file: pathlib.Path,
) -> int:

    logger = logging.getLogger(__name__)

    logger.info(f"Indexing features from {track_features_file}")

    feature_names = [
        "danceability",
        "energy",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
    ]

    df = pd.read_csv(track_features_file)
    df["feature_vectors"] = df[feature_names].to_numpy().tolist()
    features_index: dict[str, npt.NDArray[np.float64]] = pd.Series(
        df["feature_vectors"].values, index=df["compound"]
    ).to_dict()

    metric_recos_index: defaultdict[str, defaultdict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )

    users: set[str] = set()

    logger.info(f"Processing {len(reranked_reco_files)} reranked recos")

    for file in reranked_reco_files:
        metric = file.stem
        logger.info(f"Processing {file}")

        with open(file, "r") as f:
            reader = csv.DictReader(
                f, fieldnames=["user_id", "track_id", "metric", "value"]
            )

            # build up a nested defaultdict of the reranked recos of this user
            # { metric: {user: [recos]} }
            for record in reader:
                metric_recos_index[metric][record["user_id"]].append(record["track_id"])
                users.add(record["user_id"])

    logger.info(f"Loading profiles and recos for {len(users)} users")

    users_base_recos_index: defaultdict[str, list[str]] = defaultdict(list)
    users_profile_index: defaultdict[str, list[str]] = defaultdict(list)

    for user in users:
        with open(user_profile_dir / f"{user}.features.csv", "r", newline="") as f:
            reader = csv.DictReader(f, fieldnames=next(f).strip().split(","))

            # build up profile index containing the feature-vectors of tracks from the user's profile
            for record in reader:
                users_profile_index[user].append(record["compound"])

        with open(base_reco_dir / f"{user}.csv", "r") as f:
            reader = csv.DictReader(f, fieldnames=next(f).strip().split(","))

            # build up reco index for the base recos
            for record in reader:
                users_base_recos_index[user].append(record["track_id"])

    logger.info("Collecting feature vectors")

    profile_features = {
        user: np.array([features_index[track] for track in tracks])
        for user, tracks in users_profile_index.items()
    }
    base_features = {
        user: np.array([features_index[reco] for reco in recos[:10]])
        for user, recos in users_base_recos_index.items()
    }
    reranked_features = {
        metric: {
            user: np.array([features_index[reco] for reco in recos[:10]])
            for user, recos in user_recos.items()
        }
        for metric, user_recos in metric_recos_index.items()
    }

    measures_diversity: list[str] = []
    measures_unexpectedness: list[str] = []

    logger.info("Computing measures for base recos")

    for user, vectors in base_features.items():
        div = diversity(vectors)
        measures_diversity += f"diversity,base,{user},{div}\n"

        unexp = unexpectedness(profile_features[user], vectors)
        measures_unexpectedness += f"unexpectedness,base,{user},{unexp}\n"

    logger.info("Computing measures for reranked recos")

    for metric, user_vectors in reranked_features.items():
        for user, vectors in user_vectors.items():
            div = diversity(vectors)
            measures_diversity += f"diversity,{metric},{user},{div}\n"

            unexp = unexpectedness(profile_features[user], vectors)
            measures_unexpectedness += f"unexpectedness,{metric},{user},{unexp}\n"

    logger.info("Computing measures for profiles")

    for user, vectors in profile_features.items():
        div = diversity(vectors)
        measures_diversity += f"diversity,profile,{user},{div}\n"

    logger.info("Writing output files")

    with open("diversity.csv", "w") as f:
        f.write("measure,metric,user_id,value\n")
        f.writelines(measures_diversity)

    with open("unexpectedness.csv", "w") as f:
        f.write("measure,metric,user_id,value\n")
        f.writelines(measures_unexpectedness)

    return os.EX_OK


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s",
        level=logging.INFO,
    )

    parser = ArgumentParser()
    parser.add_argument("--user-profile-dir", type=pathlib.Path)
    parser.add_argument("--reranked-recos", type=pathlib.Path, nargs="+")
    parser.add_argument("--base-reco-dir", type=pathlib.Path)
    parser.add_argument("--track-features", type=pathlib.Path)

    args = parser.parse_args()

    sys.exit(
        run(
            args.user_profile_dir,
            args.reranked_recos,
            args.base_reco_dir,
            args.track_features,
        )
    )
