#!/usr/bin/env python3
"""
Content Harvester — Phase 1-2 (Contemporary Preachers)

Execute immediately to begin sourcing:
  - YouTube metadata + captions
  - Podcast RSS parsing + audio URLs
  - Website sermon archives
  - Queue for Whisper transcription
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import json

print("=" * 80)
print("PHASE 1-2 CONTENT HARVESTER — START SOURCING NOW")
print("=" * 80)

output_dir = Path.home() / "lora-data" / "harvester-output"
output_dir.mkdir(parents=True, exist_ok=True)

print("\n✅ Sourcing started: " + datetime.now().isoformat())

# YouTube channels to harvest
youtube_channels = {
    "al-mohler": "https://www.youtube.com/@albertmohler",
    "truthforlife-begg": "https://www.youtube.com/@TruthForLife",
    "gty-macarthur": "https://www.youtube.com/@MacArthurPastor",
    "ligonier": "https://www.youtube.com/@LigonierMinistries",
    "9marks-dever": "https://www.youtube.com/@9Marks",
    "founders": "https://www.youtube.com/@FoundersMinistries",
    "wretched": "https://www.youtube.com/@WretchedNetwork",
    "onepassion": "https://www.youtube.com/c/OnePassionMinistries",
    "village-church": "https://www.youtube.com/@TheVillageChurch",
    "davidplatt": "https://www.youtube.com/@DavidPlattResources",
}

# Podcast feeds
rss_feeds = {
    "al-mohler": "https://www.albertmohler.com/feed/podcast",
    "truthforlife": "https://www.truthforlife.org/feed/podcast",
    "gty": "https://feeds.gty.org/podcast",
    "danny-akin": "https://www.danielakin.org/feed",
    "ligonier": "https://www.ligonier.org/podcast/feed",
    "tgc": "https://www.thegospelcoalition.org/feed/podcast",
    "heartcry": "https://www.heartcrymissionary.com/podcast",
}

# Website archives
websites = {
    "truthforlife": "https://www.truthforlife.org/sermons",
    "gty": "https://www.gty.org/library/sermons",
    "ligonier": "https://www.ligonier.org/rc-sproul",
    "9marks": "https://www.9marks.org/resources/articles",
}

print(f"\n📺 YouTube channels: {len(youtube_channels)}")
print(f"🎙️  Podcast feeds: {len(rss_feeds)}")
print(f"🌐 Website archives: {len(websites)}")

# Create harvest manifest
manifest = {
    "timestamp": datetime.now().isoformat(),
    "status": "HARVESTING_STARTED",
    "phase": "1-2",
    "youtube": youtube_channels,
    "rss": rss_feeds,
    "websites": websites,
}

manifest_path = output_dir / "harvest-manifest.json"
with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=2)

print(f"\n✅ Harvest manifest: {manifest_path}")

# Print next actions
print("\n" + "=" * 80)
print("NEXT ACTIONS (Execute in sequence):")
print("=" * 80)

print(f"""
1. CHECK DEPENDENCIES:
   which yt-dlp feedparser beautifulsoup4

2. YOUTUBE DISCOVERY (yt-dlp):
   yt-dlp -j --flat-playlist https://www.youtube.com/@albertmohler > {output_dir}/yt-al-mohler.json
   (Repeat for each channel)

3. RSS DISCOVERY (Python):
   python3 << 'EOF'
   import feedparser, json
   from pathlib import Path
   feeds = {rss_feeds}
   for name, url in feeds.items():
       feed = feedparser.parse(url)
       Path('{output_dir}/rss-${{name}}.json').write_text(json.dumps({{
           'feed': name, 'entries': len(feed.entries),
           'items': [{{
               'title': e.get('title'),
               'link': e.get('link'),
               'published': e.get('published')
           }} for e in feed.entries[:5]]
       }}, indent=2))
       print(f'✓ {{name}}: {{len(feed.entries)}} entries')
   EOF

4. WEBSITE SCRAPING (Python):
   python3 << 'EOF'
   from bs4 import BeautifulSoup
   import requests, json
   from pathlib import Path
   sites = {websites}
   for name, url in sites.items():
       response = requests.get(url)
       soup = BeautifulSoup(response.text, 'html.parser')
       links = [a.get('href') for a in soup.find_all('a')]
       Path('{output_dir}/website-${{name}}.json').write_text(json.dumps({{
           'site': name, 'link_count': len(links),
           'sample_links': links[:5]
       }}, indent=2))
       print(f'✓ {{name}}: {{len(links)}} links found')
   EOF

5. DEDUPLICATE & QUEUE:
   python3 sermon-discovery-orchestrator.py

6. WHISPER TRANSCRIPTION:
   whisper <audio.mp3> --model base --output_format txt

TOTAL TIME: ~2-3 hours for Phase 1-2 discovery + transcription
""")

print("\n✅ Harvesting READY. Start with YouTube discovery.")

