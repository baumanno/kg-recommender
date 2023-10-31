import csv
import os
import unidecode

from argparse import ArgumentParser
from datetime import datetime
from sys import argv

def escape_literals(literal):
    literal = literal.strip()
    if literal == "":
        return literal

    # escape inner quotes (e.g. nicknames). Also, no line breaks allowed on literals
    return literal.replace("\"", "\\\"").replace("\n", "").replace("\r", "") 

def format_uri(uri):
    uri = uri.strip()
    if uri == "":
        return uri

    uri = "".join(i for i in uri if i not in r'\/:*?!"<>|.()$&’“”\'') # Remove invalid chars
    uri = unidecode.unidecode(uri) # Remove accents
    return uri.replace(" ", "_") # Replace spaces by underlines

def get_multiple_values(entities, property, id, klass, reverse=False):
    classes = set()
    relations = set()

    relationships = set()

    for entity in entities.split(","):
        entity = escape_literals(entity)
        if entity == "":
            continue

        classes.add(klass)

        entity_uri = format_uri(entity)
        entity_uri = f'nfr:{entity_uri}'

        relations.add((entity_uri, 'rdf:type', klass))
        relations.add((entity_uri, 'rdfs:label', f'\"{entity}\"^^xsd:string'))

        if reverse:
            relationships.add((entity_uri, property, id))
        else:
            relationships.add((id, property, entity_uri))

    return classes, relations, relationships

def parse_date(dateStr):
    dateStr = dateStr.strip()
    if dateStr == "":
        return None

    result = datetime.strptime(dateStr,"%B %d, %Y").isoformat()

    return f'\"{result}\"^^xsd:dateTime'

def parse_year(yearStr):
    yearStr = yearStr.strip()
    if yearStr == "":
        return None

    return f'\"{yearStr}\"^^xsd:nonNegativeInteger'

def parse_duration(durStr):
    durStr = durStr.strip()
    if durStr == "":
        return None

    #return f'\"{durStr}\"^^xsd:duration' # Would need further parsing for 'PTXXM' format
    return f'\"{durStr}\"^^xsd:string' # Either 'XX Minutes" or 'YY Seasons' (breaks xsd:duration syntax)

def parse(filename):
    prefixes = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
                'nfs': 'http://www.netflix.com/nf-schema#',
                'nfr': 'http://www.netflix.com/nf-resource#',
                'xsd': 'http://www.w3.org/2001/XMLSchema#'}
    classes = set()
    properties = []
    relations = set()
    relationships = set()

    with open(filename, 'r') as file:
        reader = csv.reader(file, delimiter=',')
        line_id = 0
        for line in reader:
            line_id += 1
            if line_id == 1: # First line has the properties
                for prop in line:
                   if prop == 'director':
                       properties.append('nfs:directed')
                   elif prop == 'cast':
                       properties.append('nfs:acted_in')
                   elif prop == 'country':
                       properties.append('nfs:produced_in')
                   elif prop == 'rating':
                       properties.append('nfs:rated')
                   else:
                       properties.append(f'nfs:{prop}')
                classes.add('rdf:Property') # for TBox completenness
            else: # Instances
                # 0: ID
                id = f'nfs:{line[0]}'
                classes.add('nfs:Entry')
                relations.add((id, 'rdf:type', 'nfs:Entry'))

                # 1: type
                c, r, rl = get_multiple_values(line[1], 'rdf:type', id, 'nfs:Format')
                classes.update(c)
                relations.update(r)
                relationships.update(rl)

                # 2: title
                title = escape_literals(line[2])
                if not title == "":
                    relationships.add((id, properties[2], f'\"{title}\"^^xsd:string'))

                # 3: director
                c, r, rl = get_multiple_values(line[3], properties[3], id, 'nfs:Director', reverse=True)
                classes.update(c)
                relations.update(r)
                relationships.update(rl)

                # 4: cast
                c, r, rl = get_multiple_values(line[4], properties[4], id, 'nfs:Actor', reverse=True)
                classes.update(c)
                relations.update(r)
                relationships.update(rl)

                # 5: country
                c, r, rl = get_multiple_values(line[5], properties[5], id, 'nfs:Country')
                classes.update(c)
                relations.update(r)
                relationships.update(rl)
                
                # 6: date_added
                date_added = parse_date(line[6])
                if not date_added is None:
                    relationships.add((id, properties[6], date_added))

                # 7: release_year
                release_year = parse_year(line[7])
                if not release_year is None:
                    relationships.add((id, properties[7], release_year))

                # 8: rating
                c, r, rl = get_multiple_values(line[8], properties[8], id, 'nfs:Rating')
                classes.update(c)
                relations.update(r)
                relationships.update(rl)

                # 9: duration
                duration = parse_duration(line[9])
                if not duration is None:
                    relationships.add((id, properties[9], duration))

                # 10: listed_in
                c, r, rl = get_multiple_values(line[10], properties[10], id, 'nfs:Collection')
                classes.update(c)
                relations.update(r)
                relationships.update(rl)

                # 11: description
                description = escape_literals(line[11])
                if not description == "":
                    relationships.add((id, properties[11], f'\"{description}\"^^xsd:string'))

    return prefixes, classes, relations, properties, relationships

def generate_ttl(filename, prefixes, classes, relations, properties, relationships):
    output_filename_wo_extension = os.path.splitext(filename)[0]
    output_filename = f'{output_filename_wo_extension}.ttl'
    open(output_filename, 'w').close() # Clean the file in case it exists

    with open(output_filename, 'a') as output_file:
        for key in prefixes.keys():
            output_file.write('@prefix\t{}:\t<{}>\t.\n'.format(key, prefixes[key]))
        output_file.write('\n\n')

        # TBox
        for klass in sorted(classes):
            output_file.write(f'{klass}\ta\trdf:Class\t.\n')
        output_file.write('\n\n')

        for prop in sorted(properties):
            output_file.write(f'{prop}\ta\trdf:Property\t.\n')
        output_file.write('\n\n')

        for relation in sorted(relations, key=lambda tup: (tup[0], tup[1])):
            if relation[1] == 'rdf:type':
                output_file.write(f'{relation[0]}\ta\t{relation[2]}\t.\n')
            else:
                output_file.write(f'{relation[0]}\t{relation[1]}\t{relation[2]}\t.\n')
        output_file.write('\n\n')

        # ABox
        for relationship in sorted(relationships, key=lambda tup: (tup[0], tup[1])):
            if relationship[1] == 'rdf:type':
                output_file.write(f'{relationship[0]}\ta\t{relationship[2]}\t.\n')
            else:
                output_file.write(f'{relationship[0]}\t{relationship[1]}\t{relationship[2]}\t.\n')

    print(f'Stored it as {output_filename}')

def main(args):
    arg_p = ArgumentParser('python parseCSV.py', description='Generates a KG from netflix CSV file.')
    arg_p.add_argument('Filename', metavar='filename', type=str, default=None, help='CSV input file')

    args = arg_p.parse_args(args[1:])
    filename = args.Filename

    if filename is None:
        print('No input file provided.')
        exit(1)

    prefixes, classes, relations, properties, relationships = parse(filename)
    
    generate_ttl(filename, prefixes, classes, relations, properties, relationships)

if __name__ == '__main__':
    exit(main(argv))

