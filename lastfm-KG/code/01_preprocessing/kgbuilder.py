from collections import defaultdict
import csv
import os
import pathlib
import sys
from argparse import ArgumentParser

MO_CLASSES = {"track": "mo:Track", "artist": "mo:MusicArtist", "genre": "mo:Genre"}
MO_PROPS = {"genre": "mo:genre"}
FOAF_PROPS = {"name": "foaf:name", "maker": "foaf:maker"}
DC_PROPS = {"title": "dc:title"}

PREFIXES = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "lfmr": "http://last.fm/lfm-resource#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "mo": "http://purl.org/ontology/mo/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}


def run(input: pathlib.Path, output: pathlib.Path) -> int:
    artist_track = defaultdict(list)
    artist_id_name = dict()
    track_genres = defaultdict(list)
    track_id_name = dict()
    all_genres = set()

    with open(input, "r", newline="") as f:
        reader = csv.DictReader(f, fieldnames=next(f).strip().split(","))

        for r in reader:
            t_id = r["compound"].strip()
            t_name = r["track_name"].strip()
            a_id = r["artist_id"].strip()
            a_name = r["artist_name"].strip()
            genres = r["genres"].strip().split("|")

            artist_id_name[a_id] = a_name
            track_id_name[t_id] = t_name
            artist_track[a_id].append(t_id)
            track_genres[t_id] += genres
            all_genres.update(genres)

    with open(output, "w") as f:
        for alias, uri in PREFIXES.items():
            l = f"@prefix {alias}: <{uri}> .\n"
            f.write(l)

        f.write("\n")

        for genre in all_genres:
            genre = genre.strip()
            if len(genre) == 0:
                continue
            l = f"lfmr:{genre}\t\ta\t\t{MO_CLASSES['genre']}\t\t.\n"
            l += f"lfmr:{genre}\t\t{DC_PROPS['title']}\t\t\"{genre}\"\t\t.\n"
            f.write(l)

        for a_id, tracks in artist_track.items():
            a_name = artist_id_name[a_id].replace(r'"', r"\"")
            l = f"lfmr:{a_id}\t\ta\t\t{MO_CLASSES['artist']}\t\t.\n"
            l += f"lfmr:{a_id}\t\t{FOAF_PROPS['name']}\t\t\"{a_name}\"\t\t.\n"
            f.write(l)

            for t_id in tracks:
                t_name = track_id_name[t_id].strip().replace(r'"', r"\"")

                # prefix track-IDs to avoid collisions with artists that have same ID
                t_id_pref = f"t_{t_id}"

                l = f"lfmr:{t_id_pref}\t\ta\t\t{MO_CLASSES['track']}\t\t.\n"
                l += f"lfmr:{t_id_pref}\t\t{DC_PROPS['title']}\t\t\"{t_name}\"\t\t.\n"
                l += f"lfmr:{t_id_pref}\t\t{FOAF_PROPS['maker']}\t\tlfmr:{a_id}\t\t.\n"
                f.write(l)

                for genre in track_genres[t_id]:
                    genre = genre.strip()
                    if len(genre) == 0:
                        continue
                    l = f"lfmr:{t_id_pref}\t\t{MO_PROPS['genre']}\t\tlfmr:{genre}\t\t.\n"
                    f.write(l)

    return os.EX_OK


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--input", type=pathlib.Path, help="CSV-file to turn into the LastFM-KG"
    )
    parser.add_argument(
        "--output", type=pathlib.Path, help="Destination to write RDF triples to"
    )
    args = parser.parse_args()

    sys.exit(run(args.input, args.output))
