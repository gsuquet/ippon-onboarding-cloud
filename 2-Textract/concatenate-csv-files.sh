#!/bin/bash

# Create the ./data/suspects/ directory if it doesn't exist
mkdir -p ./data/suspects/

# Check if there are CSV files in the ./data/textract/ directory
if ls ./data/textract/*.csv 1> /dev/null 2>&1; then
    # Sort the files based on the number in the filename and concatenate them into ./data/suspects/suspects.csv
    for file in $(ls ./data/textract/*.csv | perl -ne 'print if s/^.*?(\d+).*$/$1/' | sort -n); do
        cat "./data/textract/liste_suspects_${file}.png-results.csv" >> ./data/suspects/suspects.csv
    done
    # Remove empty lines from suspects.csv
    sed -i '/^$/d' ./data/suspects/suspects.csv
else
    echo "No CSV files found in ./data/textract/ directory."
fi
