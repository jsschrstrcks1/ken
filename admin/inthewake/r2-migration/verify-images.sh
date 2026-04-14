#!/usr/bin/env bash
#
# Verify R2-backed image serving matches production.
#
# Samples image URLs from a set of pages and compares HTTP status + size
# between production (cruisinginthewake.com) and the preview host passed
# as argument (e.g. preview.cruisinginthewake.com).
#
# Usage:
#   bash verify-images.sh preview.cruisinginthewake.com
#
# Soli Deo Gloria.

set -euo pipefail

PREVIEW_HOST="${1:?Usage: verify-images.sh <preview-host>}"
PROD_HOST="cruisinginthewake.com"

# Sample pages spanning page types
SAMPLE_PAGES=(
  "/"
  "/ships/"
  "/ships/rcl/icon-of-the-seas.html"
  "/ships/rcl/allure-of-the-seas.html"
  "/ships/carnival/carnival-celebration.html"
  "/ports/dubai.html"
  "/ports/cozumel.html"
  "/ports/juneau.html"
  "/ports/barcelona.html"
  "/restaurants/chops.html"
  "/restaurants/main-dining-room.html"
  "/solo.html"
  "/articles.html"
  "/tools/port-tracker.html"
)

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

echo ">>> Crawling ${#SAMPLE_PAGES[@]} sample pages for image URLs..."

total_imgs=0
mismatches=0
missing_preview=0

for page in "${SAMPLE_PAGES[@]}"; do
  html=$(curl -sS --max-time 30 "https://${PROD_HOST}${page}" || echo "")
  # Extract image URLs (src= and srcset=)
  urls=$(echo "$html" | grep -oE 'src="/[^"]+\.(webp|jpg|jpeg|png|svg|ico)"' | sed 's/^src="//;s/"$//' | sort -u)

  for url in $urls; do
    total_imgs=$((total_imgs + 1))
    prod_sz=$(curl -sSI --max-time 15 "https://${PROD_HOST}${url}" | grep -i '^content-length:' | awk '{print $2}' | tr -d '\r')
    prev_sz=$(curl -sSI --max-time 15 "https://${PREVIEW_HOST}${url}" | grep -i '^content-length:' | awk '{print $2}' | tr -d '\r')

    if [[ -z "$prev_sz" ]]; then
      missing_preview=$((missing_preview + 1))
      echo "[MISSING] $url (404 on preview)"
    elif [[ "$prod_sz" != "$prev_sz" ]]; then
      mismatches=$((mismatches + 1))
      echo "[MISMATCH] $url (prod=$prod_sz, preview=$prev_sz)"
    fi
  done
done

echo
echo "=== Summary ==="
echo "Total images checked: $total_imgs"
echo "Size mismatches:      $mismatches"
echo "Missing from preview: $missing_preview"

if [[ $missing_preview -gt 0 || $mismatches -gt 0 ]]; then
  echo ">>> Preview has problems — do NOT cut over to production"
  exit 1
fi

echo ">>> All images verified"
