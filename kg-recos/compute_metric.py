import networkx as nx
import numpy as np

from argparse import ArgumentParser
from concentrationMetrics import Index
from rdflib.extras.external_graph_libs import rdflib_to_networkx_digraph
from sys import argv

from get_recommendables import loadKG

def hhi(lst):
    return Index().hhi(np.array(lst))

def computeMetric(kg, metric):
    print(f'Computing {metric} ...')

    nx_kg = rdflib_to_networkx_digraph(kg)

    if 'density' == metric:
        return nx.density(nx_kg)
    if 'numedges' == metric:
        return nx_kg.number_of_edges()
    if 'numnodes' == metric:
        return nx_kg.number_of_nodes()
    if 'avg_degree' == metric:
        return nx_kg.number_of_edges() / nx_kg.number_of_nodes()

    if 'betweenness' == metric:
        computed = nx.betweenness_centrality(nx_kg)
        return hhi(list(computed.values()))
    if 'closeness' == metric:
        computed = nx.closeness_centrality(nx_kg)
        return hhi(list(computed.values()))
    if 'pagerank' == metric:
        computed = nx.pagerank(nx_kg)
        return hhi(list(computed.values()))
    if 'in_degree' == metric:
        computed = nx.in_degree_centrality(nx_kg)
        return hhi(list(computed.values()))
    if 'out_degree' == metric:
        computed = nx.out_degree_centrality(nx_kg)
        return hhi(list(computed.values()))
    if 'degree' == metric:
        computed = nx.degree_centrality(nx_kg)
        return hhi(list(computed.values()))

    raise ValueError('Unsupported metric!')

def main(args):
    arg_p = ArgumentParser('python compute_metric.py', description='Computes a given metric in a KG.')
    arg_p.add_argument('KnowledgeGraph', metavar='kg', type=str, default=None, help='KG file (*.ttl)')
    arg_p.add_argument('-m', '--metric', type=str, default='numnodes', help='Metric for KG-based recommendation')

    args = arg_p.parse_args(args[1:])
    knowledgeGraph = args.KnowledgeGraph

    if knowledgeGraph is None:
        print('No KG provided.')
        exit(1)

    kg = loadKG(knowledgeGraph)

    value = computeMetric(kg, args.metric)
    print(value)

if __name__ == '__main__':
    exit(main(argv))

