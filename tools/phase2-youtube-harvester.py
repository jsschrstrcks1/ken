#!/usr/bin/env python3
"""
Phase 2: YouTube Carson Sermon Harvesting

Extracts captions/transcripts from YouTube videos featuring D.A. Carson.
Target: 100+ sermons, 500,000+ words.

Uses YouTube's native caption system (no API key needed for captions).
"""

import urllib.request
import urllib.parse
import json
import re
import time
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

class YouTubeCarsonHarvester:
    def __init__(self):
        self.output_dir = Path("/Volumes/1TB External/openclaw/workspace-main/carson-harvest/video-transcripts")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.harvest_log = {
            "started": datetime.now().isoformat(),
            "source": "YouTube",
            "videos_found": 0,
            "transcripts_extracted": 0,
            "total_words": 0,
            "videos": []
        }
        
        self.session_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def search_youtube(self, query):
        """Search YouTube for Carson videos."""
        print(f"Searching YouTube for: {query}")
        
        # YouTube search URL
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        
        try:
            req = urllib.request.Request(search_url, headers=self.session_headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8', errors='ignore')
            
            # Extract video IDs from HTML (YouTube embeds them in JSON)
            # Look for videoId in the page
            video_ids = re.findall(r'"videoId":"([^"]{11})"', html)
            unique_ids = list(set(video_ids))[:20]  # First 20 unique
            
            print(f"  Found {len(unique_ids)} video IDs")
            return unique_ids
        
        except Exception as e:
            print(f"  Error: {e}")
            return []
    
    def extract_video_title(self, video_id):
        """Extract video title from YouTube page."""
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            req = urllib.request.Request(url, headers=self.session_headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8', errors='ignore')
            
            # Extract title from meta tag
            match = re.search(r'<meta name="title" content="([^"]+)"', html)
            if match:
                return match.group(1)
            
            # Fallback: extract from h1 or og:title
            match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
            if match:
                return match.group(1)
            
            return f"Video_{video_id}"
        
        except:
            return f"Video_{video_id}"
    
    def get_caption_tracks(self, video_id):
        """Get available caption tracks for a video."""
        try:
            # Fetch video info
            url = f"https://www.youtube.com/watch?v={video_id}"
            req = urllib.request.Request(url, headers=self.session_headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8', errors='ignore')
            
            # Extract caption URL from player response
            # YouTube stores caption data in JavaScript
            match = re.search(r'"captions":\{"playerCaptionsTracklistRenderer":', html)
            if not match:
                return None
            
            # This is complex; YouTube uses dynamically loaded caption data
            # For now, return None (we'll use a simpler approach)
            return None
        
        except:
            return None
    
    def extract_transcript_simple(self, video_id):
        """
        Try to extract transcript via YouTube transcript endpoint.
        Falls back to empty if not available.
        """
        try:
            # YouTube transcript API endpoint (unofficial)
            url = f"https://www.youtube.com/api/timedtext?v={video_id}&lang=en"
            req = urllib.request.Request(url, headers=self.session_headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                xml_data = response.read().decode('utf-8', errors='ignore')
            
            # Parse XML captions
            root = ET.fromstring(xml_data)
            
            # Extract text from caption blocks
            transcript = []
            for text_elem in root.findall('.//text'):
                if text_elem.text:
                    transcript.append(text_elem.text)
            
            return ' '.join(transcript) if transcript else None
        
        except:
            return None
    
    def save_transcript(self, video_id, title, transcript, index):
        """Save transcript to markdown file."""
        if not transcript or len(transcript) < 100:
            return False
        
        # Clean title
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' 
                            for c in title).rstrip()[:70]
        safe_title = safe_title.replace(' ', '-').lower()
        
        filename = f"youtube-{index:04d}-{safe_title}.md"
        filepath = self.output_dir / filename
        
        word_count = len(transcript.split())
        
        markdown = f"""---
source: "YouTube"
video_id: "{video_id}"
title: "{title}"
url: "https://www.youtube.com/watch?v={video_id}"
word_count: {word_count}
extracted: "{datetime.now().isoformat()}"
extraction_method: "YouTube caption API"
---

# {title}

**Source:** [YouTube](https://www.youtube.com/watch?v={video_id})

---

{transcript}

---

_Transcript extracted from YouTube captions_
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown)
            return True
        except:
            return False
    
    def harvest(self):
        """Execute YouTube harvest."""
        print("\n" + "="*80)
        print("PHASE 2: YOUTUBE CARSON SERMON HARVESTING")
        print("="*80 + "\n")
        
        # Search queries
        queries = [
            "D.A. Carson sermon",
            "Donald Carson sermon",
            "D.A. Carson teaching",
            "Carson biblical preaching",
        ]
        
        all_video_ids = set()
        
        # Search for videos
        for query in queries:
            video_ids = self.search_youtube(query)
            all_video_ids.update(video_ids)
            time.sleep(1)
        
        print(f"\nTotal unique videos found: {len(all_video_ids)}\n")
        self.harvest_log["videos_found"] = len(all_video_ids)
        
        if not all_video_ids:
            print("No videos found. Exiting.\n")
            return
        
        # Extract transcripts
        print(f"Extracting transcripts from {len(all_video_ids)} videos...\n")
        
        for i, video_id in enumerate(sorted(all_video_ids), 1):
            print(f"[{i}/{len(all_video_ids)}] {video_id}")
            
            try:
                # Get title
                title = self.extract_video_title(video_id)
                print(f"  Title: {title[:60]}")
                
                # Extract transcript
                transcript = self.extract_transcript_simple(video_id)
                
                if transcript:
                    if self.save_transcript(video_id, title, transcript, i):
                        word_count = len(transcript.split())
                        self.harvest_log["transcripts_extracted"] += 1
                        self.harvest_log["total_words"] += word_count
                        self.harvest_log["videos"].append({
                            "index": i,
                            "video_id": video_id,
                            "title": title,
                            "word_count": word_count,
                        })
                        print(f"  ✓ Saved ({word_count} words)")
                    else:
                        print(f"  ✗ Save failed")
                else:
                    print(f"  ✗ No transcript available")
            
            except Exception as e:
                print(f"  ✗ Error: {e}")
            
            time.sleep(1)
        
        # Save log
        log_file = self.output_dir / "YOUTUBE_HARVEST_LOG.json"
        with open(log_file, 'w') as f:
            json.dump(self.harvest_log, f, indent=2)
        
        # Summary
        print("\n" + "="*80)
        print("PHASE 2 COMPLETE")
        print("="*80)
        print(f"\nResults:")
        print(f"  Videos searched: {self.harvest_log['videos_found']}")
        print(f"  Transcripts extracted: {self.harvest_log['transcripts_extracted']}")
        print(f"  Total words: {self.harvest_log['total_words']:,}")
        if self.harvest_log['transcripts_extracted'] > 0:
            avg = self.harvest_log['total_words'] // self.harvest_log['transcripts_extracted']
            print(f"  Average words/video: {avg:,}")
        print(f"  Output: {self.output_dir}")
        print(f"  Log: {log_file}\n")

if __name__ == "__main__":
    harvester = YouTubeCarsonHarvester()
    harvester.harvest()
