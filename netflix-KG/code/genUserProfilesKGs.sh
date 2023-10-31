#!/bin/bash
SOURCE_DIR="../data/processed/"
SOURCE_FILENAME_BASE="userprofile_"

count=$( find $SOURCE_DIR -maxdepth 1 -type f -name "$SOURCE_FILENAME_BASE*.csv" | wc -l)

for i in $(seq 1 $count); do

if [ "$i" -lt 10 ]
then
    j="0$i"
else
    j="$i"
fi

source=$SOURCE_DIR
source+="$SOURCE_FILENAME_BASE$j.csv"

echo "Generating KG in Turtle (*.tll) format for user profile $j ..."
python3 parseCSV.py $source

filenamebase=$( echo $source | rev | cut -f 2- -d '.' | rev )
ttlfilename="$filenamebase.ttl"
echo "Converting $ttlfilename to GraphML format ..."

python3 ttl2GraphML.py $ttlfilename

done

echo "Done!"

