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

set -euo pipefail

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

for src in "${SOURCES[@]}"; do
  if [[ ! -d "$src" ]]; then
    echo "[SKIP] $src (not present)"
    continue
  fi

  count=$(find "$src" -type f | wc -l)
  size=$(du -sh "$src" | cut -f1)
  echo "[SYNC] $src ($count files, $size) → $REMOTE/$src"

  rclone sync $DRY_RUN \
    --progress \
    --copy-links \
    --transfers 16 \
    --checkers 32 \
    "$src/" \
    "$REMOTE/$src/"
done

echo
echo "Sync complete."
echo "Verify with: rclone size $REMOTE"
