#!/bin/bash
# SAFEGUARD: Prevent claims of file changes without evidence
# Usage: verify-file-change.sh <file_path> <expected_line_count> <expected_hash_sample>
# 
# This script MUST run and PASS before claiming any file modification is complete.
# Failure to run this = immediate halt, no commit, no push.

set -e

FILE="$1"
EXPECTED_LINES="$2"
EXPECTED_SAMPLE="$3"

if [ -z "$FILE" ] || [ -z "$EXPECTED_LINES" ]; then
    echo "ERROR: Usage: verify-file-change.sh <file> <expected_line_count> <optional_sample_text>"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "ERROR: File does not exist: $FILE"
    exit 1
fi

# Get actual line count
ACTUAL_LINES=$(wc -l < "$FILE")

echo "==============================================="
echo "FILE VERIFICATION SAFEGUARD"
echo "==============================================="
echo "File: $FILE"
echo "Expected lines: $EXPECTED_LINES"
echo "Actual lines: $ACTUAL_LINES"
echo ""

# Check line count
if [ "$ACTUAL_LINES" != "$EXPECTED_LINES" ]; then
    echo "❌ FAILURE: Line count mismatch!"
    echo "   Expected: $EXPECTED_LINES"
    echo "   Got: $ACTUAL_LINES"
    exit 1
else
    echo "✅ Line count verified: $ACTUAL_LINES lines"
fi

# If sample text provided, verify it's NOT in the file (for deletions)
if [ -n "$EXPECTED_SAMPLE" ]; then
    if grep -q "$EXPECTED_SAMPLE" "$FILE"; then
        echo "❌ FAILURE: Deletion not verified!"
        echo "   Text still present: $EXPECTED_SAMPLE"
        exit 1
    else
        echo "✅ Deletion verified: Sample text not found (as expected)"
    fi
fi

echo ""
echo "✅ ALL VERIFICATIONS PASSED"
echo "File change is REAL and VERIFIED."
echo "Safe to commit and push."
exit 0
