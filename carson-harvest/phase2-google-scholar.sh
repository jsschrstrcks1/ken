#!/bin/bash
# Google Scholar Carson Paper Search

OUTDIR="/Volumes/1TB External/openclaw/workspace-main/carson-harvest/academic-papers"
mkdir -p "$OUTDIR"

echo "Searching Google Scholar for D.A. Carson papers..."

cat > "$OUTDIR/GOOGLE_SCHOLAR_INSTRUCTIONS.txt" << 'EOF'
Google Scholar Carson Paper Harvesting

1. Go to https://scholar.google.com/
2. Search: "D.A. Carson" OR "Donald Carson"
3. Filter by: Recent (sort by date)

For each paper:
a. Check if PDF link available (often free preprint)
b. Try ResearchGate profile: https://www.researchgate.net/profile/Donald-Carson
c. Check author's university profile
d. Use Google Books for book chapters
e. Extract text and save as academic-papers/[title].txt

Estimated: 50+ papers × 4000-8000 words = 200,000-400,000 words

Tools:
- pdftotext: Extract text from PDF papers
- curl: Download PDFs from links
- grep: Search for Carson in abstracts

Bash one-liner to check for free PDFs:
  curl -s "https://scholar.google.com/scholar?q=Carson" | grep -o 'http[^"]*\.pdf' | head -20
EOF

echo "Google Scholar harvesting plan created."
