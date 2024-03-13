#!/bin/bash
MIN_DEGREE_IN=2
MIN_DEGREE_OUT=2
TRAIN_SPLIT=.9
SOURCE_DIR="../data/processed/"
SOURCE_FILENAME="netflix_titles.ttl"
SCRIPT_DIR="../data/res/"
SCRIPT_FILENAME_KG="ttl2KG.awk"
SCRIPT_FILENAME_USER="user2model.awk"

DESTINATION_DIR="../data/model/"

source=$SOURCE_DIR
source+=$SOURCE_FILENAME

scriptkg=$SCRIPT_DIR
scriptkg+=$SCRIPT_FILENAME_KG
scriptuser=$SCRIPT_DIR
scriptuser+=$SCRIPT_FILENAME_USER

echo "(re-)creating destination dir '$DESTINATION_DIR'"
[ -e "$DESTINATION_DIR" ] && rm -r "$DESTINATION_DIR"
mkdir -p $DESTINATION_DIR

echo "generating model files from '$source'"
awk -v OFS=' ' \
    -v outdir="$DESTINATION_DIR" \
    -v min_degree_in=$MIN_DEGREE_IN \
    -v min_degree_out=$MIN_DEGREE_OUT \
    -f $scriptkg \
    "$SCRIPT_DIR/filter_predicates" "$SCRIPT_DIR/filter_relations" $source $source

echo "generating train & test"
find $SOURCE_DIR -type f -name userprofile*.csv -print | sort | xargs -i awk -v OFS=' ' \
                                                                                         -v trainsplit=$TRAIN_SPLIT \
                                                                                         -v trainfile="$DESTINATION_DIR/train.txt" \
                                                                                         -v testfile="$DESTINATION_DIR/test.txt" \
                                                                                         -f $scriptuser \
                                                                                         -F'[, ]' \
                                                                                         "$DESTINATION_DIR/items_id.txt" \
                                                                                         "{}"


echo "Done!"

