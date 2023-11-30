import csv
import heapq
import logging
import os
import pathlib
import sys
from argparse import ArgumentParser
from collections import defaultdict
from typing import DefaultDict, List, Tuple, Type

import pandas as pd
import surprise


def get_top_n(
    predictions: List[surprise.Prediction], n: int = 10
) -> DefaultDict[str, List[Tuple[str, float]]]:
    top = defaultdict(list)

    for uid, iid, _, est, _ in predictions:
        top[uid].append((iid, est))

    for uid, ratings in top.items():
        top[uid] = heapq.nlargest(n, ratings, key=lambda x: x[1])

    return top


def run(
    algo: Type[surprise.AlgoBase],
    train_path: pathlib.Path,
    save_dir: pathlib.Path,
    sample_size: int = 0,
    top_n: int = 100,
) -> int:
    logger = logging.getLogger(__name__)

    logger.info(f"Reading {train_path}")
    df_train = pd.read_csv(train_path)

    if sample_size > 0:
        logger.info(f"Downsampling to {sample_size} rows")
        df_train = df_train.sample(sample_size)

    reader = surprise.Reader(
        rating_scale=(1, 1000),
    )

    logger.info("Building dataset")

    data_train = surprise.Dataset.load_from_df(
        df_train[["user_id", "track_id", "rating"]], reader=reader
    )

    data_train = data_train.build_full_trainset()
    data_test = data_train.build_anti_testset()

    predictions = algo().fit(data_train).test(data_test)

    logger.info("Fetching top 100 recos...")
    top_recos = get_top_n(predictions, 100)

    logger.info(f"Writing individual recos to {save_dir}")
    for user, recos in top_recos.items():
        with open(save_dir / (str(user) + ".csv"), "wt") as f:
            writer = csv.DictWriter(f, fieldnames=["user_id", "track_id", "score"])
            writer.writeheader()

            data = []
            for track, score in recos:
                data.append({"user_id": user, "track_id": track, "score": score})
            writer.writerows(data)

    return os.EX_OK


if __name__ == "__main__":
    parser = ArgumentParser(prog="Generate Recommendations")
    parser.add_argument("--algo", type=str)
    parser.add_argument("trainfile", type=pathlib.Path)
    parser.add_argument(
        "--sample",
        type=int,
        default=0,
        help="If set to a value >0, downsample training data",
    )
    parser.add_argument("--save-dir", type=pathlib.Path, help="Write recos to this dir")
    parser.add_argument(
        "--top-n",
        type=int,
        default=100,
        help="Extract top N recommendations, sorted by score",
    )
    args = parser.parse_args()

    algo = getattr(surprise, args.algo, None)
    if algo is None:
        raise NameError(f"Algorithm {args.algo} not found!")

    logging.basicConfig(
        format="%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s",
        level=logging.DEBUG,
    )

    sys.exit(run(algo, args.trainfile, args.save_dir, args.sample, args.top_n))
