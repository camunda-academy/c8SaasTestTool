#!/bin/bash

# Check if input file is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 input_file . A file called envVars.txt will be generated." 
    exit 1
fi

input_file="$1"
output_file="envVars.txt"

# Convert the Linux env file to Windows format
{
    while IFS='=' read -r key value; do
        # Remove 'export ' and quotes
        key=${key#export }
        key=${key//\'/}
        key=${key//\"/}
        value=${value//\'/}
        value=${value//\"/}
        
        # Write to output file
        echo "$key=$value"
    done < "$input_file"
} > "$output_file"

#echo "Converted file saved as: $output_file"
