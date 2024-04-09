import os

from argparse import ArgumentParser
from pathlib import Path
from rdflib import URIRef
from sys import argv

from add_neighbors import addNeighbors
from compute_metric import computeMetric
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
         
def main(args):
    arg_p = ArgumentParser('python recommend.py', description='Gets recommendations for user-profile KGs, based on a catalog KG, and a given metric')
    arg_p.add_argument('-m', '--metrics', type=str, default=None, help='Comma-separated metric list (e.g. \'degree,eigenvector,betweenness\').')
    arg_p.add_argument('-r', '--recommendables', type=str, default=None, help='[OPTIONAL] File with a list of recommendable items. If not provided, we will build our own list, according to the catalog and the user-profile.')
    arg_p.add_argument('Catalog', metavar='catalog', type=str, default=None, help='catalog KG file (*.ttl)')
    arg_p.add_argument('Profiles', metavar='profiles', type=str, default=[], nargs='+', help='Space-separated user-profile KG files (*.ttl)')

    args = arg_p.parse_args(args[1:])

    catalog = args.Catalog
    if catalog is None:
        print('No catalog KG provided.')
        exit(1)

    profiles = args.Profiles
    if profiles is None:
        print('No user-profile KG provided.')
        exit(1)

    metrics = args.metrics
    if metrics is None:
        print('No metric provided.')
        exit(1)

    metrics = metrics.split(',')

    recommendablesFile = args.recommendables
    externalRecommendables = None
    if recommendablesFile is None:
        print('No recommendables list provided. Will build our own.')
    else:
        print('Parsing external recommendables list ...')
        externalRecommendables = dict()
        with open(recommendablesFile, 'r') as recsFile:
            for line in recsFile:
                contents = line.strip().split(' ')
                if contents[0] in externalRecommendables:
                    lst = externalRecommendables[contents[0]]
                    lst.append(URIRef(contents[1]))
                    externalRecommendables[contents[0]] = lst
                else:
                    externalRecommendables[contents[0]] = [URIRef(contents[1])]

    cfg = Config()
    predicateTypes = cfg.getPredicateTypes()
    recommendableType = URIRef(cfg.getRecommendableType())
    extraMetadata = cfg.getExtraMetadataTypes()

    catalogKG = loadKG(catalog)

    for profile in profiles:
        userProfileKG = loadKG(profile)

        processed_recommendables = dict()

        if externalRecommendables is None: # find our own recommendables
            nodes = getApplicableNodes(userProfileKG, predicateTypes)
            for n in nodes:
                recommendables = getRecommendables(catalogKG, userProfileKG, n, recommendableType)

                for r in recommendables:
                    if r in processed_recommendables:
                        print(f'Skipping already-processed {r}')
                        continue

                    updatedUserProfileKG = addNeighbors(catalogKG, userProfileKG, r, extraMetadata)
                    metrics_for_recommendable = dict()
                    for m in metrics:
                        metrics_for_recommendable[m] = computeMetric(updatedUserProfileKG, m)
                    processed_recommendables[r] = metrics_for_recommendable

        else: # use external recommendables
            for r in externalRecommendables[Path(profile).stem]:
                if (r, None, None) in userProfileKG or (None, None, r) in userProfileKG:
                    print(f'Skipping already-existing node {r}')
                    continue

                updatedUserProfileKG = addNeighbors(catalogKG, userProfileKG, r, extraMetadata)
                metrics_for_recommendable = dict()
                for m in metrics:
                    metrics_for_recommendable[m] = computeMetric(updatedUserProfileKG, m)
                processed_recommendables[r] = metrics_for_recommendable

        for m in metrics:
            # Sort: More relevant first
            recos = dict(sorted(processed_recommendables.items(), key=lambda item: item[1][m], reverse=True))

            # Save to file
            profile_dir = os.path.dirname(profile)
            profile_filename = Path(profile).stem # Remove path and extension
            output_dir = os.path.join(profile_dir, f'recos_{profile_filename}')
            Path(output_dir).mkdir(parents=True, exist_ok=True) # Create if not exists

            output_filename = os.path.join(output_dir, f'{m}.txt')
            open(output_filename, 'w').close() # Clean if exists

            with open(output_filename, 'a') as output_file:
                for k, v in recos.items():
                    output_file.write(f'{k}\t{v[m]}\n')

            print(f'Stored it as {output_filename}')

if __name__ == '__main__':
    exit(main(argv))
    
