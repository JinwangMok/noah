#!/bin/bash

output="./llm_proxy/model_size.yaml"

echo "models:" > $output

find ./models -type f \( -iname "*.gguf" -o -iname "*.ggml" \) | while read file; do
    size=$(stat -c %s "$file")
    echo "  - path: $file" >> $output  
    echo "    size: $size" >> $output
done

echo "$output is now updated."
