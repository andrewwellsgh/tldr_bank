#!/usr/bin/env bash

OUTPUT="bundle.txt"
> "$OUTPUT"

while IFS= read -r file; do
    echo "===== FILE: $file =====" >> "$OUTPUT"
    cat "$file" >> "$OUTPUT"
    echo -e "\n\n" >> "$OUTPUT"
done < <(
    find . -type f \
        ! -path "*/.git/*" \
        ! -path "*/__pycache__/*" \
        ! -path "*/.venv/*" \
        ! -path "*/venv/*" \
        ! -path "*/node_modules/*" \
        ! -path "*/csv_store/*" \
        ! -name "$OUTPUT"
)

echo "Bundle written to $OUTPUT"