#!/bin/bash
# The Gospel Coalition Carson Article Harvesting

OUTDIR="/Volumes/1TB External/openclaw/workspace-main/carson-harvest/blog-writings"
mkdir -p "$OUTDIR"

echo "Harvesting The Gospel Coalition for Carson articles..."

# TGC search for Carson
# Note: This requires parsing TGC's site or API
# For now, document manual approach:

cat > "$OUTDIR/TGC_HARVESTING_INSTRUCTIONS.txt" << 'EOF'
The Gospel Coalition Carson Article Harvesting Instructions

1. Go to https://www.thegospelcoalition.org/
2. Search for "D.A. Carson"
3. Results should show 100+ articles
4. For each article:
   a. Open article URL
   b. Copy article text
   c. Save as blog-writings/tgc-[title].md
   d. Include front matter: source, date, URL, author

Estimated: 150 articles × 1000-3000 words = 150,000-450,000 words

TGC has open access; no copy restrictions. Can use web scraper if needed.

Alternative: Use curl + grep to extract article links:
  curl -s "https://www.thegospelcoalition.org/?s=Carson" | grep -o 'href="[^"]*"' > links.txt

Then batch process with wget or curl to download full articles.
EOF

echo "TGC harvesting plan created: $OUTDIR/TGC_HARVESTING_INSTRUCTIONS.txt"
