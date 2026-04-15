#!/usr/bin/env bash
#
# InTheWake → Cloudflare R2 image sync
#
# Run from the InTheWake repository root after rclone is configured with
# an `r2` remote pointing at the `inthewake-media` bucket.
#
# --copy-links is set because some directories (notably assets/ships)
# contain symlinks that need to be resolved to their target content
# before upload. R2 (and S3 generally) doesn't store symlinks — the
# content has to be inlined as a normal object under the symlink's name.
#
# Usage:
#   bash "$KEN_DIR/admin/inthewake/r2-migration/rclone-sync.sh" [--dry-run]
#
# Soli Deo Gloria.

set -uo pipefail

DRY_RUN=""
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN="--dry-run"
  echo ">>> DRY RUN — no files will be uploaded <<<"
fi

REMOTE="r2:inthewake-media"

SOURCES=(
  "assets/ships"
  "ports/img"
  "assets/social"
  "assets/images"
  "assets/venues"
  "assets/articles"
  "assets/brand"
  "assets/icons"
  "assets/img"
  "authors/img"
  "authors/ico"
  "authors/tinas-images"
  "solo/images"
  "images"
)

FAILED_SOURCES=()

for src in "${SOURCES[@]}"; do
  if [[ ! -d "$src" ]]; then
    echo "[SKIP] $src (not present)"
    continue
  fi

  count=$(find "$src" -type f | wc -l)
  size=$(du -sh "$src" | cut -f1)
  echo "[SYNC] $src ($count files, $size) → $REMOTE/$src"

  # Allow individual directory failures (e.g. broken symlinks in one tree)
  # without aborting the rest of the sync. rclone already retries 3 times
  # internally and prints its own error summary.
  if ! rclone sync $DRY_RUN \
    --progress \
    --copy-links \
    --transfers 16 \
    --checkers 32 \
    "$src/" \
    "$REMOTE/$src/"; then
    echo "[WARN] $src reported errors — continuing with remaining sources"
    FAILED_SOURCES+=("$src")
  fi
done

echo
if [[ ${#FAILED_SOURCES[@]} -eq 0 ]]; then
  echo "Sync complete — no errors."
else
  echo "Sync complete with errors in ${#FAILED_SOURCES[@]} source(s):"
  for src in "${FAILED_SOURCES[@]}"; do
    echo "  - $src"
  done
fi
echo "Verify total with: rclone size $REMOTE"
