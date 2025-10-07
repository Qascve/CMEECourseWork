#!/bin/bash

echo "Usage: bash concatenateTwoFiles.sh File1 File2 Outputfile"

echo -n "Please enter three file names (file1 file2 outputfile): "

read file1 file2 outputfile

if [ $# -eq 0 ]; then # Check if any arguments are provided
    echo "Error: No input provided"
    exit 1
fi

if [ ! -f "$file1" ] || [ ! -f "$file2" ]; then
    echo "Error: Input file does not exist"
    exit 1
fi
echo "Merging $file1 and $file2 into $outputfile ..."

cat $file1 > $outputfile
cat $file2 >> $outputfile
echo "Merged File is"
cat $outputfile