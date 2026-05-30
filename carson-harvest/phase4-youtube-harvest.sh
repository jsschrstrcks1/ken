#!/bin/bash
# YouTube Video Transcript Extraction

OUTDIR="/Volumes/1TB External/openclaw/workspace-main/carson-harvest/video-transcripts"
mkdir -p "$OUTDIR"

echo "Harvesting YouTube video transcripts..."

cat > "$OUTDIR/YOUTUBE_HARVESTING_INSTRUCTIONS.txt" << 'EOF'
YouTube Video Transcript Harvesting

Search on YouTube:
1. "D.A. Carson sermon"
2. "D.A. Carson interview"
3. "D.A. Carson teaching"
4. "D.A. Carson conference"

For each video:
a. Check if "Show Transcript" button available (YouTube's auto-captions)
b. Click "Show Transcript" → Copy full transcript
c. Save to video-transcripts/youtube-[video-id].md
d. Include video URL and metadata

Tools:
- youtube-dl: Download video metadata
- youtube-transcript-api (Python): Extract transcripts automatically

Python one-liner:
  pip install youtube-transcript-api
  python3 -c "from youtube_transcript_api import YouTubeTranscriptApi;     print(YouTubeTranscriptApi.get_transcript('VIDEO_ID'))"

Bash loop to find and download Carson videos:
  youtube-dl --skip-download --write-auto-sub --sub-lang en     "https://www.youtube.com/results?search_query=D.A.+Carson+sermon"

Estimated yield: 500,000+ words from 100+ videos × 5000 words/transcript

Save format: video-transcripts/youtube-[title].md

Front matter:
---
source: "YouTube"
video_title: "[Title]"
video_url: "[URL]"
video_duration: "[Duration]"
speaker: "D.A. Carson"
transcript_source: "[youtube-auto|manual|api]"
---

[transcript]
EOF

echo "YouTube harvesting plan created."
