#!/bin/bash
# Auto-transcribe Discord audio and reply with transcript
# Run via: bash /path/to/auto-transcribe.sh
# Or add to crontab: */2 * * * * bash /Volumes/1TB\ External/openclaw/workspace-main/tools/auto-transcribe.sh

set -e

AUDIO_DIR="$HOME/.openclaw/audio-inbox"
TRANSCRIPT_DIR="$HOME/.openclaw/transcripts"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure directories exist
mkdir -p "$AUDIO_DIR" "$TRANSCRIPT_DIR"

# Run the Python transcriber
python3 "$SCRIPT_DIR/transcribe-discord-audio.py"

# Check for new transcripts and announce them
TRANSCRIPTS_FILE="$TRANSCRIPT_DIR/.last-announced"
[ -f "$TRANSCRIPTS_FILE" ] || touch "$TRANSCRIPTS_FILE"

for transcript_file in "$TRANSCRIPT_DIR"/*.txt; do
    if [ -f "$transcript_file" ]; then
        basename=$(basename "$transcript_file")
        if ! grep -q "$basename" "$TRANSCRIPTS_FILE"; then
            # New transcript — read and announce
            transcript_text=$(cat "$transcript_file")
            echo "✓ New transcript: $basename"
            echo "$transcript_text"
            
            # Log as announced
            echo "$basename" >> "$TRANSCRIPTS_FILE"
        fi
    fi
done
