import csv

PATH = "../data/external/artist_track_genres.txt"
DEST = "../data/processed/artist_track_genres.csv"

row_dict = {
  'compound': '',
  'track': '',
  'artist_id': 0,
  'artist': '',
  'genres': ''
}

with open(PATH, 'r') as f:
  with open(DEST, 'w', newline='') as w:
    next(f) # skip header
    
    writer = csv.DictWriter(w, fieldnames = list(row_dict.keys()))
    writer.writeheader()
    
    for line in f:
      line = line.strip()
      if len(line) <= 0:
        continue
      
      # column 5 contains LFM2b playcount, which we don't need and hence drop
      # columns 6+ contain (genre, weight) tuples separated by tabs, which we aggregate in a list and clean later
      row_dict['compound'], row_dict['track'], row_dict['artist_id'], row_dict['artist'], _, *genres = line.split('\t')
      
      # genre names are at odd indices, weights at even indices; only keep the odds
      genres = [g.strip() for g in genres[0::2]]
      row_dict['genres'] = '|'.join(genres)
      
      writer.writerow(row_dict)
