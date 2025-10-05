#!/bin/bash


if [ $# -eq 0 ]; then # Check if any arguments are provided
    echo "Error: No input provided"
    exit 1
fi

NumLines=`wc -l < $1`
echo "The file $1 has $NumLines lines"
echols