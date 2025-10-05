#!/bin/bash

if [ $# -eq 0 ]; then # Check if any arguments are provided
    echo "Error: No input provided"
    exit 1
fi

for f in *.tif; 
    do  
        echo "Converting $f"; 
        convert "$f"  "$(basename "$f" .tif).png"; 
    done