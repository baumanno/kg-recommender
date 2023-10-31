#!/bin/bash
SOURCE="../data/raw/netflix_titles.csv"

DESTINATION_DIR="../data/processed/"

USERS=$1
LOWER=$2
UPPER=$3

watchcountsfilename=users_with_watchcounts.csv
echo "user_id,show_id,num_watches" > $watchcountsfilename

for i in $(seq 1 $USERS); do

R=$(($(($RANDOM%(($UPPER-$LOWER+1))))+$LOWER))

echo "Generating a random profile for user $i with $R entries..."

if [ "$i" -lt 10 ]
then
    j="0$i"
else
    j="$i"
fi
filename=userprofile_"$j".csv
( head -n 1 $SOURCE ; tail -n +1 $SOURCE | shuf -n $R ) > $filename

while IFS="," read -r show_id
do
  W=$(($(($RANDOM%((10-1+1))))+1)) # 1 time watched min; 10 times max
  echo "$j,$show_id,$W" >> $watchcountsfilename
  echo "user_id: $j"
  echo "show_id: $show_id"
  echo "num_watches: $W"
  echo ""
done < <( cut -d "," -f1,1 $filename | tail -n +2 ) # while

echo "Moving the $filename KGs to $DESTINATION_DIR ..."
mv $filename $DESTINATION_DIR

done # for

echo "Moving the $watchcountsfilename KGs to $DESTINATION_DIR ..."
mv $watchcountsfilename $DESTINATION_DIR

echo "Done!"

