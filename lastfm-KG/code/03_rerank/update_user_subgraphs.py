import csv
import logging
import os
import pathlib
import sys
from argparse import ArgumentParser
from multiprocessing import Pool

import rdflib
from rdflib.namespace import FOAF, DC


def getNeighbors(catalog_kg: rdflib.Graph, reco_item: rdflib.URIRef):
    logger = logging.getLogger(__name__)

    neighborsKG = rdflib.Graph()
    neighborsKG += catalog_kg.triples((reco_item, None, None))  # subjects
    neighborsKG += catalog_kg.triples((None, None, reco_item))  # objects

    for s, _, _ in neighborsKG:
        neighborsKG += catalog_kg.triples((s, FOAF.name, None))
        neighborsKG += catalog_kg.triples((s, DC.title, None))

    return neighborsKG


def f(profile: pathlib.Path):
    logger = logging.getLogger(__name__)

    user = profile.stem.removesuffix(".subkg")
    # reco_dir is global; assigned to each worker through process initializier
    user_reco = reco_dir / (user + ".csv")

    if not user_reco.exists():
        logger.error(f"No recos for {user}")
        return

    logger.info(f"Reading profile {profile.name}")
    user_kg = rdflib.Graph()
    user_kg.parse(profile)

    logger.info(f"Reading recos for {user}")

    with open(user_reco) as f:
        reader = csv.DictReader(f, fieldnames=next(f).strip().split(","))
        user_out_dir = out_dir / str(user)
        pathlib.Path(user_out_dir).mkdir(exist_ok=True)

        for record in reader:
            reco_item = rdflib.URIRef(
                f"http://last.fm/lfm-resource#t_{record['track_id']}"
            )
            neigh_kg = getNeighbors(catalog_kg, reco_item)

            merged_kg = user_kg + neigh_kg
            logger.info(
                f"merged KG contains additional {len(merged_kg)-len(user_kg)} nodes"
            )

            outfile = user_out_dir / str(f"{record['track_id']}.ttl")
            logger.info(f"writing merged KG to {outfile}")
            merged_kg.serialize(
                format="ttl",
                destination=outfile,
            )
    return profile


def run(
    catalog_kg_file: pathlib.Path,
    user_kg_dir: pathlib.Path,
    reco_dir: pathlib.Path,
    out_dir: pathlib.Path,
    num_profiles: int = -1,
    nproc: int = 1,
) -> int:
    logger = logging.getLogger(__name__)

    logger.info(f"Reading catalog KG from {catalog_kg_file}")
    catalog_kg = rdflib.Graph()
    catalog_kg.parse(catalog_kg_file)

    logger.info("Collecting profiles to read")

    profiles_to_read = list(user_kg_dir.glob("*"))

    # if not all profiles are required, slice from the head of the list
    if num_profiles != -1:
        profiles_to_read = profiles_to_read[:num_profiles]
        num_profiles = len(profiles_to_read)

    logger.info(f"Reading {num_profiles} from {user_kg_dir}")

    def init_worker(rdir, catalog, odir):
        global reco_dir
        global catalog_kg
        global out_dir
        reco_dir = dir
        catalog_kg = catalog
        out_dir = odir

    logger.info(f"Initializing pool with {nproc} workers")
    with Pool(
        nproc, initializer=init_worker, initargs=(reco_dir, catalog_kg, out_dir)
    ) as p:
        ps_completed = p.imap_unordered(f, profiles_to_read)
        print(list(ps_completed))

    return os.EX_OK


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)-15s %(name)-15s %(process)-3d %(levelname)-15s %(message)s",
        level=logging.INFO,
    )

    parser = ArgumentParser()
    parser.add_argument(
        "--catalog-kg", type=pathlib.Path, help="Path to the catalog KG"
    )
    parser.add_argument(
        "--user-kg-dir",
        type=pathlib.Path,
        help="Directory containing profile sub-KGs",
    )
    parser.add_argument(
        "--reco-dir", type=pathlib.Path, help="Directory containing the reco-files"
    )
    parser.add_argument(
        "--out-dir", type=pathlib.Path, help="Directory to write the final stats to"
    )
    parser.add_argument(
        "--num-profiles",
        type=int,
        help="Read this many profiles; -1 (default) reads all",
    )
    parser.add_argument(
        "--nproc",
        type=int,
        help="Number of workers to spawn",
    )

    args = parser.parse_args()

    sys.exit(
        run(
            args.catalog_kg,
            args.user_kg_dir,
            args.reco_dir,
            args.out_dir,
            args.num_profiles,
            args.nproc,
        )
    )
