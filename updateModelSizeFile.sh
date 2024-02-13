#!/bin/bash

output="./data/model_sizes.yaml"

echo "models:" > $output

find ./models -type f \( -iname "*.gguf" -o -iname "*.ggml" \) | while read file; do
    size=$(stat -c %s "$file")
    filename=$(basename "$file")
    echo "  - name: $filename" >> $output
    echo "    size: $size" >> $output
done

echo "$output is now updated."
