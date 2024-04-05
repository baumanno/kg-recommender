from argparse import ArgumentParser
from rdflib import Graph, URIRef
from rdflib.namespace import RDF
from sys import argv

from config import Config

def loadKG(filename):
    print(f'Loading {filename} as an RDFLib graph ...')

    graph = Graph()
    graph.parse(filename, format="turtle")

    return graph

def getPossibleRecommendables(catalog, profile, recommendableType):
    recommendables = catalog.subjects(predicate=RDF.type, object=recommendableType)
    profile_recommendables = profile.subjects(predicate=RDF.type, object=recommendableType)

    non_recommendables = [n for n in profile_recommendables]

    return [r for r in recommendables if not r in non_recommendables]

def getRecommendables(catalog, profile, start, recommendableType):
    print(f'Getting recommendables for {start} ...')

    recommendables = getPossibleRecommendables(catalog, profile, recommendableType)

    subjects = catalog.subjects(predicate=None, object=start)
    subjects = [s for s in subjects if s in recommendables]

    objects = catalog.objects(subject=start, predicate=None)
    objects = [o for o in objects if o in recommendables]

    return list(set(subjects) | set(objects))


def main(args):
    arg_p = ArgumentParser('python get_recommendables.py', description='Gets recommendables, not in the user-profile, from the catalog KG, starting from a given node.')
    arg_p.add_argument('Catalog', metavar='catalog', type=str, default=None, help='catalog KG file (*.ttl)')
    arg_p.add_argument('Profile', metavar='profile', type=str, default=None, help='user-profile KG file (*.ttl)')
    arg_p.add_argument('-n', '--node', type=str, default='http://www.netflix.com/nf-resource#Andrea_Libman', help='starting node')

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

    startingNode = URIRef(args.node)

    cfg = Config()
    recommendableType = URIRef(cfg.getRecommendableType())
    
    recommendables = getRecommendables(catalogKG, userProfileKG, startingNode, recommendableType)
    print(recommendables)
    print(len(recommendables))

if __name__ == '__main__':
    exit(main(argv))

