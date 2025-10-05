#!/bin/bash

if [ $# -eq 0 ]; then # Check if any arguments are provided
    echo "Error: No input provided"
    exit 1
fi

echo "Merging $1 and $2 into $3 ..."

cat $1 > $3
cat $2 >> $3
echo "Merged File is"
cat $3