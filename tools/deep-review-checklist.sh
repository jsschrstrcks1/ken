#!/bin/bash
# deep-review-checklist.sh
# Run this against any HTML file before claiming work is done.
# The orchestra catches what Claude misses. This checklist approximates that depth.

FILE="$1"

if [ -z "$FILE" ]; then
  echo "Usage: $0 <path-to-html-file>"
  exit 1
fi

if [ ! -f "$FILE" ]; then
  echo "ERROR: File not found: $FILE"
  exit 1
fi

ERRORS=0
WARNINGS=0

echo "=== DEEP REVIEW CHECKLIST: $FILE ==="
echo ""

# 1. STALE COMMENTS — check ALL occurrences, not just the first
echo "--- [1] Stale version comments (ALL occurrences) ---"
grep -n "ICP-Lite\|ICP-1\|ICP-2\|ICP-3" "$FILE" | while read -r line; do
  echo "  $line"
done
ICOUNT=$(grep -c "ICP-Lite" "$FILE" 2>/dev/null || echo 0)
if [ "$ICOUNT" -gt 0 ]; then
  echo "  ❌ Found $ICOUNT stale ICP-Lite reference(s) — update ALL occurrences"
  ERRORS=$((ERRORS + 1))
else
  echo "  ✅ No stale ICP-Lite references"
fi
echo ""

# 2. BOOLEAN GUARD LOGIC — look for inverted conditions
echo "--- [2] Swiper guard logic ---"
grep -n "if(window\.__swiperReady\|if(!window\.__swiperReady" "$FILE"
GUARD=$(grep -c "if(window\.__swiperReady)" "$FILE" 2>/dev/null || echo 0)
if [ "$GUARD" -gt 0 ]; then
  echo "  ❌ Found $GUARD possibly INVERTED guard(s): if(window.__swiperReady) should be if(!window.__swiperReady)"
  ERRORS=$((ERRORS + 1))
else
  echo "  ✅ No inverted Swiper guards detected"
fi
echo ""

# 3. DUPLICATE FETCH CALLS — same URL fetched more than once
echo "--- [3] Duplicate fetch() calls ---"
grep -n "fetch(" "$FILE" | sed "s/.*fetch(//" | sed "s/).*//" | sort | uniq -d | while read -r url; do
  echo "  ❌ DUPLICATE fetch: $url"
  ERRORS=$((ERRORS + 1))
done
FETCHCOUNT=$(grep -c "fetch(" "$FILE" 2>/dev/null || echo 0)
echo "  Total fetch() calls: $FETCHCOUNT"
echo ""

# 4. DUPLICATE SCRIPT LOADS — same src loaded more than once
echo "--- [4] Duplicate script loads ---"
grep -n '<script.*src=' "$FILE" | sed 's/.*src=["'"'"']//' | sed 's/["'"'"'].*//' | sort | uniq -d | while read -r src; do
  echo "  ❌ DUPLICATE script src: $src"
  ERRORS=$((ERRORS + 1))
done
echo ""

# 5. DUPLICATE SWIPER INITS — multiple new Swiper() targeting same element
echo "--- [5] Swiper initialization count ---"
grep -n "new Swiper(" "$FILE"
SWIPERCOUNT=$(grep -c "new Swiper(" "$FILE" 2>/dev/null || echo 0)
echo "  Total new Swiper() calls: $SWIPERCOUNT"
if [ "$SWIPERCOUNT" -gt 4 ]; then
  echo "  ⚠️  More than 4 Swiper inits — verify no duplicates"
  WARNINGS=$((WARNINGS + 1))
fi
echo ""

# 6. ID UNIQUENESS — duplicate IDs cause silent failures
echo "--- [6] Duplicate HTML IDs ---"
grep -o 'id="[^"]*"' "$FILE" | sort | uniq -d | while read -r id; do
  echo "  ❌ DUPLICATE ID: $id"
  ERRORS=$((ERRORS + 1))
done
echo ""

# 7. STALE COMMENTS IN BODY (not just head)
echo "--- [7] Version comments in body (must match head) ---"
HEAD_ICP=$(grep -m1 "ICP-" "$FILE" | grep -o "ICP-[^ >\"']*" | head -1)
ALL_ICP=$(grep -o "ICP-[0-9A-Za-z.]*" "$FILE" | sort -u)
echo "  First ICP reference: $HEAD_ICP"
echo "  All ICP references: $ALL_ICP"
UNIQUE_ICP=$(echo "$ALL_ICP" | wc -l | tr -d ' ')
if [ "$UNIQUE_ICP" -gt 1 ]; then
  echo "  ❌ INCONSISTENT ICP versions — must all match"
  ERRORS=$((ERRORS + 1))
else
  echo "  ✅ ICP version consistent"
fi
echo ""

# 8. MISSING STRUCTURED DATA
echo "--- [8] Structured data (JSON-LD) ---"
JSONLD=$(grep -c "application/ld+json" "$FILE" 2>/dev/null || echo 0)
if [ "$JSONLD" -eq 0 ]; then
  echo "  ⚠️  No JSON-LD structured data found"
  WARNINGS=$((WARNINGS + 1))
else
  echo "  ✅ JSON-LD present ($JSONLD block(s))"
fi
echo ""

# FINAL SUMMARY
echo "=== SUMMARY ==="
echo "  Errors:   $ERRORS"
echo "  Warnings: $WARNINGS"
echo ""
if [ "$ERRORS" -gt 0 ]; then
  echo "  ❌ FAILED — fix errors before claiming done"
  exit 1
else
  echo "  ✅ PASSED — ready for orchestra review"
  exit 0
fi
