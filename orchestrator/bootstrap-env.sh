#!/bin/bash
# bootstrap-env.sh — Ensures orchestrator API keys are available.
#
# Strategy:
#   1. If orchestrator/.env exists, copy it to ~/.orchestrator.env (backup)
#   2. If orchestrator/.env is missing but ~/.orchestrator.env exists, restore it
#   3. If neither exists, warn (keys must be manually configured)
#
# Usage:  bash bootstrap-env.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_ENV="$SCRIPT_DIR/.env"
HOME_ENV="$HOME/.orchestrator.env"

# Case 1: local .env exists — ensure home backup is current
if [ -f "$LOCAL_ENV" ]; then
    cp -f "$LOCAL_ENV" "$HOME_ENV" 2>/dev/null
    exit 0
fi

# Case 2: local .env missing but home backup exists — restore
if [ -f "$HOME_ENV" ]; then
    cp -f "$HOME_ENV" "$LOCAL_ENV" 2>/dev/null
    exit 0
fi

# Case 3: neither exists
echo "[bootstrap] WARNING: No .env found. Create $LOCAL_ENV or $HOME_ENV with API keys." >&2
echo "[bootstrap] See $SCRIPT_DIR/.env.example for required keys." >&2
exit 0
