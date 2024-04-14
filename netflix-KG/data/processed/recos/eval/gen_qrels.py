from rdflib import Graph, URIRef

output_filename = 'qrels.test'
open(output_filename, 'w').close() # Clean if exists

with open('../external_recos.txt', 'r') as f:
    with open(output_filename, 'a') as out:

        current_kg_file = None
        kg = None
        rank = 8808 # num. of nodes in the catalog
        for line in f:
            raw_line = line.strip().split()
            queryid = raw_line[0]
            documentid = raw_line[1]

            if queryid != current_kg_file:
                current_kg_file = queryid
                kg = Graph()
                kg.parse(f'../../{current_kg_file}.ttl', format="turtle")
                rank = 8808

            uri = URIRef(documentid)
            if (uri, None, None) in kg or (None, None, uri) in kg:
                out_line = f'{queryid} Q0 {documentid} 0' # already-existing documentids are non-relevant
                out.write(f'{out_line}\n')
                print(out_line)
                continue

            rank -= 1
            out_line = f'{queryid} Q0 {documentid} {rank}'
            out.write(f'{out_line}\n')
            print(out_line)

