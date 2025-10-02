#!/bin/bash
# Author:zy3425@ic.ac.uk
# Script: csvtospace.sh
# Description:
# Converts a CSV file to a space-separated file


# Check if input file is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: need a csv_file as input"
    exit 1
else
    # when correct
    echo "proceeding..."

fi

# Check if file exists
test -f "$1" || { echo "File $1 not found!"; exit 1; }

# Define outputpath
outputPath="../data/$(basename "$1" .csv)_space_separated_version.txt"
echo "Creating space-separated version of $1 as $outputPath ..."

# Convert commas to spaces
tr ',' ' ' <$1> "$outputPath"
echo "Done,Output saved to path:$outputPath"
