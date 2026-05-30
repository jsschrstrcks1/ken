#!/bin/bash
# Podcast Interview Transcripting

OUTDIR="/Volumes/1TB External/openclaw/workspace-main/carson-harvest/podcast-transcripts"
mkdir -p "$OUTDIR"

echo "Harvesting podcast interview transcripts..."

cat > "$OUTDIR/PODCAST_HARVESTING_INSTRUCTIONS.txt" << 'EOF'
Podcast Interview Transcripting

Primary podcasts featuring D.A. Carson:
1. The Briefing (Al Mohler)
2. Gospel Coalition Podcast
3. Ask Pastor John (John Piper)
4. Renewing Your Mind (Ligonier/Sproul)

For each podcast:
a. Go to podcast platform (Apple Podcasts, Spotify, etc.)
b. Search for Carson episodes
c. Check if transcript provided
d. If not, use podcast platform's transcript feature or Whisper API

Apple Podcasts/Spotify often have episode transcripts. Check:
- thebriefing.org (Al Mohler's site)
- gospelcoalition.org/podcast
- desiringGod.org (Piper's ministry)
- ligonier.org/podcast

For episodes without transcripts, use:
  ffmpeg -i episode.mp3 -ac 1 -ar 16000 -f wav - | whisper - --model base --task transcribe

Estimated yield: 400,000+ words from all podcasts

Save format: podcast-transcripts/[podcast]-[episode-number]-[title].md

Front matter:
---
source: "Podcast: [Name]"
podcast_title: "[Episode Title]"
guest: "D.A. Carson"
date: "[Episode Date]"
duration_minutes: [minutes]
transcript_source: "[manual|official|whisper-api]"
---

[transcript text]
EOF

echo "Podcast harvesting plan created."
