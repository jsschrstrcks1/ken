#!/bin/bash
# davey-coordinator.sh
# Coordinates three parallel harvester pipelines for Stephen Davey sermons
# Run: bash davey-coordinator.sh

set -e

WORKSPACE="/Volumes/1TB External/openclaw/workspace-main"
TOOLS_DIR="$WORKSPACE/tools"

echo "════════════════════════════════════════════════════════════════"
echo "  STEPHEN DAVEY SERMON HARVESTER — 3-Path Parallel Pipeline"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Verify Python environment
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 not found"
    exit 1
fi

echo "[✓] Environment check passed"
echo ""

# Verify scripts exist
for script in davey-path1-subsplash.py davey-path2-youtube.py davey-path3-podcast.py; do
    if [[ ! -f "$TOOLS_DIR/$script" ]]; then
        echo "[ERROR] Missing: $script"
        exit 1
    fi
done

echo "[✓] All harvester scripts present"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "LAUNCHING PARALLEL PIPELINES"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Path 1: Subsplash (this machine, 25 sermons, 3-min throttle)
echo "[1/3] Path 1: Subsplash Harvester (this machine)"
echo "      • Target: Wisdom International (Subsplash)"
echo "      • Rate: 25 sermons with 3-min separation"
echo "      • Duration: ~2 hours"
echo ""
python3 "$TOOLS_DIR/davey-path1-subsplash.py" &
PID_1=$!
echo "      → Started (PID: $PID_1)"
echo ""

# Path 2: YouTube (m3pro, batch download)
echo "[2/3] Path 2: YouTube Extractor (m3pro — kens-macbook-pro)"
echo "      • Target: YouTube 'Wisdom for the Heart' channel"
echo "      • Method: yt-dlp (no API key)"
echo "      • Command to run on m3pro:"
echo "        ssh kenbaker@kens-macbook-pro.local 'python3 ~/openclaw/tools/davey-path2-youtube.py'"
echo ""

# Path 3: Podcast RSS (m4max, batch harvest)
echo "[3/3] Path 3: Podcast RSS Harvester (m4max)"
echo "      • Target: Wisdom for the Heart podcast feed"
echo "      • Method: RSS parsing + HTML extraction"
echo "      • Command to run on m4max:"
echo "        ssh kenbaker@100.120.40.114 'python3 ~/openclaw/tools/davey-path3-podcast.py'"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "MONITORING PATH 1"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Wait for Path 1 to complete
wait $PID_1
EXIT_1=$?

if [[ $EXIT_1 -eq 0 ]]; then
    echo "[✓] Path 1 complete"
else
    echo "[!] Path 1 exited with code $EXIT_1"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "STATUS: Path 1 Complete"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Session logs:"
echo "  • /Volumes/1TB External/Projects/Romans/stephen-davey-transcripts/path1-session.json"
echo "  • (Check m3pro and m4max for path2-session.json and path3-session.json)"
echo ""
echo "Next steps:"
echo "  1. Deploy Path 2 on m3pro: ssh user@kens-macbook-pro.local"
echo "  2. Deploy Path 3 on m4max: ssh user@100.120.40.114"
echo "  3. Monitor transcripts directory for incoming files"
echo "  4. Run: git add && git commit once all harvests complete"
echo ""
