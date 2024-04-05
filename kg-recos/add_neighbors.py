from argparse import ArgumentParser
from rdflib import Graph, URIRef
from sys import argv

from config import Config

def loadKG(filename):
    print(f'Loading {filename} as an RDFLib graph ...')

    graph = Graph()
    graph.parse(filename, format="turtle")

    return graph

def addExtraMetadata(kg, catalog, extraMetadata):
    extraTriples = Graph()
    for extra in extraMetadata:
        extraTriples += catalog.triples((None, extra, None))

    for s, p, o in kg.triples((None, None, None)):
         kg += extraTriples.triples((s, None, None))
         kg += extraTriples.triples((p, None, None))
         kg += extraTriples.triples((o, None, None))
            

def getNeighbors(catalog, recommendable, extraMetadata):
    print(f'Gathering {recommendable} neighbors ...')

    neighborsKG = Graph()
    neighborsKG += catalog.triples((recommendable, None, None)) # subjects
    neighborsKG += catalog.triples((None, None, recommendable)) # objects

    addExtraMetadata(neighborsKG, catalog, extraMetadata)

    return neighborsKG

def addNeighbors(catalogKG, userProfileKG, recommendable, extraMetadata, saveFile=False):
    neighborsKG = getNeighbors(catalogKG, recommendable, extraMetadata)
    
    resultKG = Graph()
    resultKG = userProfileKG + neighborsKG

    if saveFile:
        resultKG.serialize(format="ttl", destination="neighbors.ttl")

    return resultKG

def main(args):
    arg_p = ArgumentParser('python include_neighbors.py', description='Includes all catalog neighbors of a recommendable, not already in the user-profile.')
    arg_p.add_argument('Catalog', metavar='catalog', type=str, default=None, help='catalog KG file (*.ttl)')
    arg_p.add_argument('Profile', metavar='profile', type=str, default=None, help='user-profile KG file (*.ttl)')
    arg_p.add_argument('-r', '--recommendable', type=str, default='http://www.netflix.com/nf-schema#s8103', help='recommendable item')

    args = arg_p.parse_args(args[1:])
    catalog = args.Catalog

    if catalog is None:
        print('No catalog KG provided.')
        exit(1)

    profile = args.Profile

    if profile is None:
        print('No user-profile KG provided.')
        exit(1)

    catalogKG = loadKG(catalog)
    userProfileKG = loadKG(profile)

    cfg = Config()
    extraMetadata = cfg.getExtraMetadataTypes()
    print(extraMetadata)

    addNeighbors(catalogKG, userProfileKG, URIRef(args.recommendable), extraMetadata, saveFile=True)

if __name__ == '__main__':
    exit(main(argv))

