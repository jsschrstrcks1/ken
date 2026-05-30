#!/bin/bash
# sync-docs.sh — Verify CLAUDE.md ↔ AGENTS.md parity on shared topics

set -e

CLAUDE_MD="/Volumes/1TB External/openclaw/workspace-main/CLAUDE.md"
AGENTS_MD="/Volumes/1TB External/openclaw/workspace-main/AGENTS.md"

echo "🔍 Checking CLAUDE.md ↔ AGENTS.md Parity (Shared Topics)"
echo "========================================================="
echo

# These sections must exist in BOTH files (shared topics requiring parity)
SHARED_TOPICS=(
  "Memory"
  "Skills"
  "Protected Areas"
  "Cognitive Memory"
  "Anthropic ToS"
)

echo "📋 Validating shared topics exist in both files..."
echo

DIVERGENT=0

for topic in "${SHARED_TOPICS[@]}"; do
  if grep -q "$topic" "$CLAUDE_MD"; then
    echo "✅ CLAUDE.md: $topic"
  else
    echo "❌ CLAUDE.md: MISSING $topic"
    DIVERGENT=$((DIVERGENT + 1))
  fi
  
  if grep -q "$topic" "$AGENTS_MD"; then
    echo "✅ AGENTS.md:  $topic"
  else
    echo "❌ AGENTS.md: MISSING $topic"
    DIVERGENT=$((DIVERGENT + 1))
  fi
  echo
done

if [ $DIVERGENT -gt 0 ]; then
  echo "⚠️  $DIVERGENT DIVERGENCES DETECTED"
  echo
  echo "Fix by ensuring these shared topics exist in BOTH files:"
  echo "  - Memory system (encoding, tiers, recall)"
  echo "  - Skills catalog and activation"
  echo "  - Protected areas (.gitignore)"
  echo "  - Cognitive Memory mechanics"
  echo "  - Anthropic ToS requirements"
  echo
  exit 1
else
  echo "✅ Parity check PASSED — all shared topics present in both files"
  echo
  echo "📌 Sync rules:"
  echo "   - Shared topics: edit BOTH files, commit together"
  echo "   - Topic-specific: edit only the relevant file"
  echo "   - Run this script after major edits to verify"
fi
