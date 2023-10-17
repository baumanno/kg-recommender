import argparse
import logging
import os
import sys
from pprint import pprint as pp

import igraph
import numpy as np

logger = logging.getLogger("main")


def load_graph(path: str) -> igraph.Graph:
    logger.info("Loading file " + path)

    return igraph.load(path)


def print_graph_stats(g: igraph.Graph) -> None:
    print("# Graph stats ---------------")
    print(f" Number of vertices:\t{g.vcount()}")
    print(f" Number of edges:\t{g.ecount()}")
    print(" Maximum degree:"
          f"  {g.vs.select(_degree=g.maxdegree())[0]['human_name']}"
          f"  ({g.maxdegree()})")
    betweenness: float = g.betweenness()
    max_between: float = np.max(betweenness)
    which_between = np.argmax(betweenness)
    print(f" Maximum betweenness: {g.vs[which_between]} ({max_between}))")
    print()


def print_vertex_query(g: igraph.Graph, name: str) -> None:
    print("# Vertex stats --------------")
    vs: igraph.Vertex = g.vs.select(human_name_eq=name)
    print(f' Number of vertices matching "{name}": {len(vs)}')

    for i, v in enumerate(vs):
        print()
        print(f"## Item {i} ----------------")
        print(f" Vertex: {name}")
        print(f" Type: {v['type']}")
        print(" Degree: {}".format(v.degree(mode="out")))

        if v["type"] == "artist":
            print("         ^--- this is the number of tracks for this artist")
        elif v["type"] == "track":
            print("         ^--- this is the number of genres for this track")
        print(f" Betweenness: {v.betweenness()}")
        print(f" Closeness: {v.closeness()}")
        print(f" Pagerank: {v.pagerank()}")
        print()
        print("### Vertex neighborhood ------")
        pp(v.neighbors(mode="all"))


def run(graph_path: str, vertex: str):
    try:
        g = load_graph(graph_path)
    except Exception as e:
        logger.error("Error loading graphml: " + str(e))
        sys.exit(os.EX_OSERR)

    print_graph_stats(g)
    print_vertex_query(g, vertex)

    sys.exit(os.EX_OK)


if __name__ == "__main__":
    levels = (
        logging.INFO,
        logging.DEBUG,
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--graphml",
                        help="path to the graphml-dump",
                        required=True)
    parser.add_argument(
        "--vertex",
        help=("vertex to query; uses the `human_name`-attribute. Example:"
              " 'Somebody That I Used to Know'"),
        default="Black Sabbath",
    )
    parser.add_argument("--verbose",
                        "-v",
                        help="verbose output",
                        action="count",
                        default=0)
    args = parser.parse_args(sys.argv[1:])

    logging.basicConfig(
        level=levels[min(args.verbose,
                         len(levels) - 1)],
        format="%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s",
    )
    run(args.graphml, args.vertex)
