import logging
import os
import pathlib
import sys
from argparse import ArgumentParser
from collections import defaultdict
from typing import List

import numpy as np
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from surprise import (
    NMF,
    BaselineOnly,
    Dataset,
    KNNBaseline,
    KNNBasic,
    KNNWithMeans,
    KNNWithZScore,
    Prediction,
    Reader,
)
from surprise.model_selection import KFold


def run(
    train_path: pathlib.Path,
    sample_size: int = 0,
    table_path: None | pathlib.Path = None,
) -> int:
    logger = logging.getLogger(__name__)

    logger.info(f"Reading {train_path}")
    df_train = pd.read_csv(train_path)

    if sample_size > 0:
        logger.info(f"Downsampling to {sample_size} rows")
        df_train = df_train.sample(sample_size)

    reader = Reader(
        rating_scale=(1, 1000),
    )

    logger.info("Building dataset")

    data_train = Dataset.load_from_df(
        df_train[["user_id", "track_id", "rating"]], reader=reader
    )

    splits = KFold(n_splits=5)

    errs = defaultdict(list)

    for i, (train, test) in enumerate(splits.split(data_train)):
        print("---------------")
        print(f" Fold {i}    NMF")
        print("---------------")
        preds: List[Prediction] = NMF().fit(train).test(test)
        mae = np.mean([abs(p.r_ui - p.est) for p in preds])
        print(f"MAE: {mae}")
        errs["NMF"].append(mae)
        print("--------------------------")

        print("----------------------------------")
        print(f" Fold {i}    Mean Baseline Estimate")
        print("----------------------------------")
        preds = BaselineOnly().fit(train).test(test)
        mae = np.mean([abs(p.r_ui - p.est) for p in preds])
        print(f"MAE: {mae}")
        errs["BaselineOnly"].append(mae)
        print("--------------------------")

        print("-----------------------")
        print(f" Fold {i}    UserItemkNN")
        print("-----------------------")
        preds = KNNBasic(n=40, sim_options={"name": "cosine"}).fit(train).test(test)
        mae = np.mean([abs(p.r_ui - p.est) for p in preds])
        print(f"MAE: {mae}")
        errs["KNNBasic"].append(mae)
        print("--------------------------")

        print("------------------------------")
        print(f" Fold {i}    UserItemkNNBaseline")
        print("------------------------------")
        preds = KNNBaseline(n=40, sim_options={"name": "cosine"}).fit(train).test(test)
        mae = np.mean([abs(p.r_ui - p.est) for p in preds])
        print(f"MAE: {mae}")
        errs["KNNBaseline"].append(mae)
        print("--------------------------")

        print("--------------------------")
        print(f" Fold {i}    UserItemkNNAvg")
        print("--------------------------")
        preds = KNNWithMeans(n=40, sim_options={"name": "cosine"}).fit(train).test(test)
        mae = np.mean([abs(p.r_ui - p.est) for p in preds])
        print(f"MAE: {mae}")
        errs["KNNWithMeans"].append(mae)
        print("--------------------------")

        print("-----------------------------")
        print(f" Fold {i}    UserItemkNNZscore")
        print("-----------------------------")
        preds = (
            KNNWithZScore(n=40, sim_options={"name": "cosine"}).fit(train).test(test)
        )
        mae = np.mean([abs(p.r_ui - p.est) for p in preds])
        print(f"MAE: {mae}")
        errs["KNNWithZScore"].append(mae)
        print("--------------------------")

    mmeans = {k: np.mean(m) for k, m in errs.items()}
    minim = min(mmeans.items(), key=lambda x: x[1])
    with open("./algo.out", "w") as f:
        f.write(minim[0])

    env = Environment(
        loader=FileSystemLoader("templates"), trim_blocks=True, lstrip_blocks=True
    )
    template = env.get_template("table.tex.j2")
    tab = template.render(data=mmeans, minim=minim[0])

    print(tab)

    if table_path is not None:
        logger.info(f"Writing table to {table_path}")
        with open(table_path, "w") as f:
            f.write(tab)

    return os.EX_OK


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s",
        level=logging.DEBUG,
    )

    parser = ArgumentParser(prog="Generate Recommendations")
    parser.add_argument("trainfile", type=pathlib.Path)
    parser.add_argument(
        "--sample",
        type=int,
        default=0,
        help="If set to a value >0, downsample training data",
    )
    parser.add_argument(
        "--write-table",
        type=pathlib.Path,
        default=None,
        help="If provided, render table-template to this file.",
    )
    args = parser.parse_args()

    sys.exit(run(args.trainfile, args.sample, args.write_table))
