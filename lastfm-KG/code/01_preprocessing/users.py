import argparse
import csv
import logging
import os
import pathlib
import sys

import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def run(
    user_counts_path: pathlib.Path,
    num_users: int,
    sample_out: pathlib.Path,
    tmpdir: pathlib.Path,
    scaled_out: pathlib.Path,
    features_path: pathlib.Path,
) -> int:
    logger = logging.getLogger(__name__)

    logger.info("Building sample")
    df = pd.read_csv(user_counts_path)

    old_len = len(df)
    print(f"number of users: {old_len}")

    df = df[df["n_uniq_tracks"] > 100]

    new_len = len(df)
    print(f"number of users with >100 uniq tracks: {new_len}")
    reduction = (old_len - new_len) / old_len
    print(f"reduction: {reduction*100}%")

    logger.info(f"Sampling {num_users} users")
    df = df.sample(n=num_users, random_state=666)
    logger.info(f"User sample contains {len(df)} users")

    logger.info(f"Writing sample to {sample_out}")
    df.to_csv(sample_out, index=False)

    logger.info("Building full frame of all users in sample")
    data: list[pd.DataFrame] = []
    for user in df["user_id"]:
        path = tmpdir / (str(user) + ".playcounts.csv")
        data.append(
            pd.read_csv(
                path,
                header=None,
                names=["user_id", "track_id", "count"],
                dtype={"user_id": "int64", "track_id": "string", "count": "uint16"},
            )
        )

    logger.info(f"Collected {len(data)} sub-dataframes")
    sample_playcounts = pd.concat(data)

    logger.info("Scaling implicit counts to ratings in (1,1000)")

    scaler = MinMaxScaler(feature_range=(1, 1000))

    def scaler_func(group):
        group["rating"] = scaler.fit_transform(group[["count"]])
        return group

    df_scaled = (
        sample_playcounts.groupby("user_id", sort=False)[
            ["user_id", "track_id", "count"]
        ]
        .apply(scaler_func)
        .reset_index(drop=True)
    )

    logger.info(f"Writing scaled data to {scaled_out}")
    df_scaled.to_csv(scaled_out, index=False)

    logging.info(f"Reading feature-file {features_path} into memory")
    feature_index: dict[str, dict] = dict()
    with open(features_path, "r", newline="") as fd:
        features_header = next(fd).strip().split(",")
        reader = csv.DictReader(fd, fieldnames=features_header)
        for record in reader:
            feature_index[record["compound"]] = record

    logging.info("Writing feature histories for users")
    writecounter = 0
    for user, group in sample_playcounts.groupby("user_id"):
        user_records = []
        for row in group.itertuples():
            user_records.append(feature_index[row.track_id])

        with open(tmpdir / (str(user) + ".features.csv"), "w") as fout:
            writer = csv.DictWriter(fout, fieldnames=features_header)
            writer.writeheader()
            writer.writerows(user_records)
            writecounter += 1

    logger.info(f"Wrote {writecounter} user-feature-files")

    return os.EX_OK


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s",
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--user-counts", type=pathlib.Path)
    parser.add_argument("--num-users", type=int)
    parser.add_argument("--sample-out", type=pathlib.Path)
    parser.add_argument("--tmpdir", type=pathlib.Path)
    parser.add_argument("--scaled-out", type=pathlib.Path)
    parser.add_argument("--features", type=pathlib.Path)
    args = parser.parse_args()

    sys.exit(
        run(
            args.user_counts,
            args.num_users,
            args.sample_out,
            args.tmpdir,
            args.scaled_out,
            args.features,
        )
    )
