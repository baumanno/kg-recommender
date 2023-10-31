#!/bin/bash
SOURCE_DIR="../data/raw/"
SOURCE_FILENAME="netflix_titles.csv"

DESTINATION_DIR="../data/processed/"

source=$SOURCE_DIR
source+=$SOURCE_FILENAME
echo "Generating KG in Turtle (*.tll) format ..."
python3 parseCSV.py $source

filenamebase=$( echo $source | rev | cut -f 2- -d '.' | rev )
ttlfilename="$filenamebase.ttl"
echo "Converting $ttlfilename to GraphML format ..."

python3 ttl2GraphML.py $ttlfilename

echo "Moving the generated KGs to $DESTINATION_DIR ..."
mv $ttlfilename $DESTINATION_DIR
mv "$filenamebase.graphml" $DESTINATION_DIR

echo "Done!"

