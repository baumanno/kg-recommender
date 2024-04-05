import os

from argparse import ArgumentParser
from pathlib import Path
from rdflib import URIRef
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
from sys import argv

from add_neighbors import addNeighbors
from config import Config
from get_recommendables import loadKG, getRecommendables

def getApplicableNodes(kg, predicateTypes):
    print('Getting all user-profile nodes ...')

    subjects = set()
    objects = set()
    for p in predicateTypes:
        for s, o in kg.subject_objects(predicate=URIRef(p)):
            subjects.add(s)
            objects.add(o)

    return list(subjects.union(objects))

def extractMetric(kg, node, metric):
    nx_kg = rdflib_to_networkx_multidigraph(kg)
    return nx_kg.number_of_nodes()
         
def main(args):
    arg_p = ArgumentParser('python recommend.py', description='Gets recommendations for an user-profile KG, based on a catalog KG, and a given metric')
    arg_p.add_argument('Catalog', metavar='catalog', type=str, default=None, help='catalog KG file (*.ttl)')
    arg_p.add_argument('Profile', metavar='profile', type=str, default=None, help='user-profile KG file (*.ttl)')
    arg_p.add_argument('-m', '--metric', type=str, default='numnodes', help='Metric for KG-based recommendation')
    
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
    predicateTypes = cfg.getPredicateTypes()
    recommendableType = URIRef(cfg.getRecommendableType())
    extraMetadata = cfg.getExtraMetadataTypes()

    nodes = getApplicableNodes(userProfileKG, predicateTypes)
    processed_recommendables = dict()
    for n in nodes:
        recommendables = getRecommendables(catalogKG, userProfileKG, n, recommendableType)
        for r in recommendables:
            if r in processed_recommendables:
                print(f'Skipping already-processed {r}')
                continue

            updatedUserProfileKG = addNeighbors(catalogKG, userProfileKG, r, extraMetadata)
            processed_recommendables[r] = extractMetric(updatedUserProfileKG, r, args.metric)

    # Sort: More relevant first
    recos = dict(sorted(processed_recommendables.items(), key=lambda item: item[1], reverse=True))

    # Save to file
    profile_dir = os.path.dirname(profile)
    output_dir = os.path.join(profile_dir, 'recos')
    Path(output_dir).mkdir(parents=True, exist_ok=True) # Create if not exists

    output_filename = os.path.join(output_dir, f'{args.metric}.txt')
    open(output_filename, 'w').close() # Clean if exists

    with open(output_filename, 'a') as output_file:
        for k, v in recos.items():
            output_file.write(f'{k}\t{v}\n')

    print(f'Stored it as {output_filename}')

if __name__ == '__main__':
    exit(main(argv))
    
