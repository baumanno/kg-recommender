import csv
import logging
import os
import pathlib
import sys
from argparse import ArgumentParser
from multiprocessing import Pool
from typing import NamedTuple

import networkx as nx
import numpy as np
from concentrationMetrics import Index
from rdflib.extras.external_graph_libs import rdflib_to_networkx_digraph
from rdflib.graph import Graph


def hhi(lst):
    return Index().hhi(np.array(lst))


def computeMetric(kg: Graph, metric: str):

    nx_kg = rdflib_to_networkx_digraph(kg)

    if "density" == metric:
        return nx.density(nx_kg)
    if "numedges" == metric:
        return nx_kg.number_of_edges()
    if "numnodes" == metric:
        return nx_kg.number_of_nodes()
    if "avg_degree" == metric:
        return nx_kg.number_of_edges() / nx_kg.number_of_nodes()

    if "betweenness" == metric:
        computed = nx.betweenness_centrality(nx_kg)
        return hhi(list(computed.values()))
    if "closeness" == metric:
        computed = nx.closeness_centrality(nx_kg)
        return hhi(list(computed.values()))
    if "pagerank" == metric:
        computed = nx.pagerank(nx_kg)
        return hhi(list(computed.values()))
    if "in_degree" == metric:
        computed = nx.in_degree_centrality(nx_kg)
        return hhi(list(computed.values()))
    if "out_degree" == metric:
        computed = nx.out_degree_centrality(nx_kg)
        return hhi(list(computed.values()))
    if "degree" == metric:
        computed = nx.degree_centrality(nx_kg)
        return hhi(list(computed.values()))

    raise ValueError("Unsupported metric!")


class MetricLine(NamedTuple):
    user_id: str
    track_id: str
    metric_name: str
    metric_val: float


def f(
    user_subgraph: pathlib.Path, updated_subgraphs: pathlib.Path, out_dir: pathlib.Path
):
    # This worker is executed separately per user, i.e. one worker only
    # ever sees one user

    logger = logging.getLogger(__name__)

    metrics = [
        "density",
        "numedges",
        "numnodes",
        "avg_degree",
        "betweenness",
        "closeness",
        "pagerank",
        "in_degree",
        "out_degree",
        "degree",
    ]

    user = user_subgraph.name.removesuffix(".subkg.ttl")
    logger.info(f"Processing user {user}")

    data: list[MetricLine] = []

    # Read the subgraphs that resulted from incorporating each recommendation
    for subgraph in updated_subgraphs.glob("*.ttl"):
        track_id = subgraph.stem

        # Compute each metric on each subgraph
        for metric in metrics:
            g = Graph()
            g.parse(subgraph)
            m = computeMetric(g, metric)
            line = MetricLine(
                user_id=user, track_id=track_id, metric_name=metric, metric_val=float(m)
            )
            data.append(line)

    user_out_dir = pathlib.Path(out_dir / user)
    user_out_dir.mkdir(exist_ok=True)

    logger.info(f"Done for user {user}, writing results to {user_out_dir}")
    with open(user_out_dir / "results.csv", "w") as f:
        writer = csv.DictWriter(
            f, fieldnames=["user_id", "track_id", "metric_name", "metric_val"]
        )
        writer.writeheader()
        writer.writerows(map(lambda x: x._asdict(), data))

    return user


def run(
    updated_kg_dir: pathlib.Path,
    base_subgraph_dir: pathlib.Path,
    metrics_out_dir: pathlib.Path,
    nproc: int = 1,
) -> int:
    logger = logging.getLogger(__name__)

    logger.info(f"Collecting base subgraphs from {base_subgraph_dir}")
    subgraphs = list(base_subgraph_dir.glob("*.subkg.ttl"))
    updated_subgraph_dirs = list(updated_kg_dir.glob("*"))
    inputs = zip(
        sorted(subgraphs),
        sorted(updated_subgraph_dirs),
        [metrics_out_dir] * len(subgraphs),
    )

    logger.info(f"Initializing pool with {nproc} workers")
    with Pool(nproc) as p:
        ps_completed = p.starmap(f, inputs)
        print(list(ps_completed))

    return os.EX_OK


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)-15s %(name)-15s %(process)-3d %(levelname)-15s %(message)s",
        level=logging.INFO,
    )

    parser = ArgumentParser()
    parser.add_argument(
        "--updated-kg-dir",
        type=pathlib.Path,
        help="Path to user-kgs that have been updated with recos",
    )
    parser.add_argument(
        "--base-subgraph-dir",
        type=pathlib.Path,
        help="Path to the original recommendations",
    )
    parser.add_argument(
        "--metrics-out-dir", type=pathlib.Path, help="Path to write the metrics to"
    )
    parser.add_argument(
        "--nproc",
        type=int,
        help="Number of workers to spawn",
    )

    args = parser.parse_args()

    sys.exit(
        run(
            args.updated_kg_dir,
            args.base_subgraph_dir,
            args.metrics_out_dir,
            args.nproc,
        )
    )
