#!/bin/bash
# Author:zy3425@ic.ac.uk
# Script: csvtospace.sh
# Description:
# Converts a CSV file to a space-separated file


echo "Please enter  file names: "

read file

if [[ $file != *.csv ]]; then
    echo "Error: Input file is not a .csv file"
    exit 1
fi

# Define outputpath
outputPath="../results/$(basename "$file" .csv)_space_separated_version.txt"
echo "Creating space-separated version of $file as $outputPath ..."

# Convert commas to spaces
tr ',' ' ' <"$file" >"$outputPath"
echo "Done,Output saved to path:$outputPath"
