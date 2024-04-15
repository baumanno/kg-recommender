import csv
import logging
import os
import pathlib
import sys
from argparse import ArgumentParser
from typing import NamedTuple

# magic number: number of recos per user; tuned via ../02_recos/02_dump_recos.py
NUM_RECOS_IN_LIST: int = 100


class ResultsLine(NamedTuple):
    query_id: str
    document_id: str
    rank: int
    score: int
    standard: str


def run(input_list: list[pathlib.Path], output_dir: pathlib.Path) -> int:
    logger = logging.getLogger(__name__)

    for input in input_list:
        logger.info(f"Reading {input}")

        data: list[ResultsLine] = []
        metric_name = input.stem

        with open(input, "r", newline="") as f:
            reader = csv.DictReader(
                f, fieldnames=["user_id", "track_id", "metric", "value"]
            )

            score = NUM_RECOS_IN_LIST
            rank = 1
            cur_user = ""

            for line in reader:
                # if we're seeing a new user, reset score and rank
                if cur_user != line["user_id"]:
                    cur_user = line["user_id"]
                    score = NUM_RECOS_IN_LIST
                    rank = 1

                r = ResultsLine(
                    query_id=cur_user,
                    document_id=line["track_id"],
                    rank=rank,
                    score=score,
                    standard=metric_name.upper(),
                )
                data.append(r)

                score -= 1
                rank += 1

        lines_to_write: list[str] = []
        for r in data:
            lines_to_write += (
                f"{r.query_id} Q0 {r.document_id} {r.rank} {r.score} {r.standard}\n"
            )

        out_name = output_dir / (metric_name + ".results.test")
        logger.info(f"Writing {out_name}")

        with open(out_name, "w") as f:
            f.writelines(lines_to_write)

    return os.EX_OK


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s",
        level=logging.INFO,
    )

    parser = ArgumentParser()
    parser.add_argument(
        "--input",
        type=pathlib.Path,
        nargs="+",
        help="The file to re-write to results-format",
    )
    parser.add_argument("--output-dir", type=pathlib.Path, help="The destination file")
    args = parser.parse_args()

    sys.exit(run(args.input, args.output_dir))
