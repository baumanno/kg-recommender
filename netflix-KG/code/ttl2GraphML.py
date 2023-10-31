import os
import networkx as nx

from argparse import ArgumentParser
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
from rdflib import Graph
from sys import argv

def convert(filename):
    print(f'Loading {filename} as an RDFLib graph...')
    graph = Graph()
    graph.parse(filename, format="turtle")

    print('Converting RDFLib graph to NetworkX multidigraph...')
    kg = rdflib_to_networkx_multidigraph(graph)

    output_filename_wo_extension = os.path.splitext(filename)[0]
    output_filename = f'{output_filename_wo_extension}.graphml'
    
    print('Converting multidigraph to GraphML...') 
    nx.write_graphml(kg, output_filename)

    print(f'Stored it as {output_filename}')

def main(args):
    arg_p = ArgumentParser('python ttl2GraphML.py', description='Converts a Turtle KG to GraphML.')
    arg_p.add_argument('Filename', metavar='filename', type=str, default=None, help='TTL input file')

    args = arg_p.parse_args(args[1:])
    filename = args.Filename

    if filename is None:
        print('No input file provided.')
        exit(1)

    convert(filename)

if __name__ == '__main__':
    exit(main(argv))

