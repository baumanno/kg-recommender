from argparse import ArgumentParser
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS
from sys import argv

def loadKG(filename):
    print(f'Loading {filename} as an RDFLib graph ...')

    graph = Graph()
    graph.parse(filename, format="turtle")

    return graph

def addExtraMetadata(kg, catalog):
    extraTriples = Graph()
    extraTriples += catalog.triples((None, RDF.type, None))
    extraTriples += catalog.triples((None, RDFS.label, None))

    for s, p, o in kg.triples((None, None, None)):
         kg += extraTriples.triples((s, None, None))
         kg += extraTriples.triples((p, None, None))
         kg += extraTriples.triples((o, None, None))
            

def getNeighbors(catalog, recommendable):
    print(f'Gathering {recommendable} neighbors ...')

    neighborsKG = Graph()
    neighborsKG += catalog.triples((recommendable, None, None)) # subjects
    neighborsKG += catalog.triples((None, None, recommendable)) # objects

    addExtraMetadata(neighborsKG, catalog)

    return neighborsKG

def addNeighbors(catalogKG, userProfileKG, recommendable, saveFile=False):
    neighborsKG = getNeighbors(catalogKG, recommendable)
    
    resultKG = Graph()
    resultKG = userProfileKG + neighborsKG

    if saveFile:
        resultKG.serialize(format="ttl", destination="out.ttl")

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

    addNeighbors(catalogKG, userProfileKG, URIRef(args.recommendable), saveFile=True)

if __name__ == '__main__':
    exit(main(argv))

