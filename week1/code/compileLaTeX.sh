#!/bin/bash
# Compile LaTeX document

if [ $# -eq 0 ]; then # Check if any arguments are provided
    echo "Error: No input provided"
    exit 1
fi

if [[ $file != *.tex ]]; then
    echo "Error: Input file is not a .tex file"
    exit 1
fi


if [[ $1 == *.tex ]]; then
    filename=${1%.tex} # Remove file extension
else
    filename=$1 # Use the provided name
fi

pdflatex $filename.tex
bibtex $filename
pdflatex $filename.tex
pdflatex $filename.tex
evince $filename.pdf &

## Cleanup
rm *.aux
rm *.log
rm *.bbl
rm *.blg