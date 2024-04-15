import csv
import logging
import os
import pathlib
import sys
from argparse import ArgumentParser
from typing import NamedTuple

# magic number: number of recos per user; tuned via ../02_recos/02_dump_recos.py
NUM_RECOS_IN_LIST: int = 100


class QrelLine(NamedTuple):
    query_id: str
    document_id: str
    relevance: int


def run(reco_dir: pathlib.Path, out: pathlib.Path) -> int:
    logger = logging.getLogger(__name__)

    logger.info(f"Reading reference-recos from {reco_dir}")

    data: list[QrelLine] = []
    for user_recos in reco_dir.glob("*.csv"):

        with open(user_recos, "r", newline="") as f:
            reader = csv.DictReader(f, fieldnames=next(f).strip().split(","))

            rel = NUM_RECOS_IN_LIST
            for r in reader:
                q = QrelLine(
                    query_id=r["user_id"], document_id=r["track_id"], relevance=rel
                )
                rel -= 1
                data.append(q)

    lines_to_write: list[str] = []
    for q in data:
        lines_to_write += f"{q.query_id} Q0 {q.document_id} {q.relevance}\n"

    with open(out, "w") as f:
        logger.info(f"Writing {len(lines_to_write)} to {out}")
        f.writelines(lines_to_write)

    return os.EX_OK


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)-15s %(name)-15s %(levelname)-15s %(message)s",
        level=logging.INFO,
    )

    parser = ArgumentParser()
    parser.add_argument("--reco-dir", type=pathlib.Path, help="Path to the user-recos")
    parser.add_argument("--out", type=pathlib.Path, help="Path to the final file")

    args = parser.parse_args()

    sys.exit(run(args.reco_dir, args.out))
