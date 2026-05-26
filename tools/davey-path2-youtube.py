#!/usr/bin/env python3
"""
Path 2: YouTube Transcript Extractor
- Target: YouTube channel "Wisdom for the Heart" (Stephen Davey sermons)
- Method: yt-dlp + local subtitle extraction (no API key needed)
- Output: /Volumes/1TB External/Projects/Romans/stephen-davey-transcripts/
- Deployment: m3pro (kens-macbook-pro)
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
import time

# Configuration
OUTPUT_DIR = Path("/Volumes/1TB External/Projects/Romans/stephen-davey-transcripts")
SESSION_LOG = OUTPUT_DIR / "path2-session.json"

# YouTube playlist URLs for Stephen Davey
PLAYLISTS = {
    "romans": "https://www.youtube.com/playlist?list=PLH0Szn1yYNeez0Y8xECtpjY3LwS5L1bVe",  # Romans series example
    "psalms": "https://www.youtube.com/c/WisdomfortheHeart/videos?view=2&sort=dd&shelf_id=0",
    "john": "https://www.youtube.com/results?search_query=Stephen+Davey+John+sermon",
}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def log_session(event, data=None):
    """Log session activity."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event,
        "data": data
    }
    
    try:
        if SESSION_LOG.exists():
            with open(SESSION_LOG, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(entry)
        
        with open(SESSION_LOG, 'w') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"[LOG ERROR] {e}")

def check_yt_dlp():
    """Verify yt-dlp is installed."""
    try:
        result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[✓] yt-dlp: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        print("[!] yt-dlp not found. Install: brew install yt-dlp")
        log_session("yt_dlp_missing", {"note": "install via: brew install yt-dlp"})
        return False

def extract_playlist_videos(playlist_url, series_name):
    """Extract video URLs from playlist."""
    try:
        print(f"[→] Extracting videos from {series_name}...")
        
        cmd = [
            "yt-dlp",
            "--flat-playlist",
            "-j",
            playlist_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"[!] Could not extract playlist: {result.stderr[:200]}")
            log_session("playlist_extraction_failed", {"series": series_name, "error": result.stderr[:200]})
            return []
        
        videos = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    data = json.loads(line)
                    videos.append({
                        "id": data.get("id"),
                        "title": data.get("title"),
                        "url": f"https://www.youtube.com/watch?v={data.get('id')}"
                    })
                except json.JSONDecodeError:
                    pass
        
        print(f"[+] Found {len(videos)} videos in {series_name}")
        log_session("playlist_extracted", {"series": series_name, "count": len(videos)})
        
        return videos
    
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Playlist extraction timed out for {series_name}")
        log_session("playlist_timeout", {"series": series_name})
        return []
    except Exception as e:
        print(f"[ERROR] Failed to extract playlist {series_name}: {e}")
        log_session("playlist_error", {"series": series_name, "error": str(e)})
        return []

def download_transcript(video_url, video_title):
    """Download video transcript using yt-dlp."""
    try:
        print(f"[→] Extracting transcript: {video_title[:60]}...")
        
        # Sanitize filename
        safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in video_title)[:80]
        output_file = OUTPUT_DIR / f"stephen-davey-{safe_title}.txt"
        
        # Extract subtitle/transcript via yt-dlp
        cmd = [
            "yt-dlp",
            "--write-auto-subs",
            "--sub-format", "vtt",
            "--skip-download",
            "-o", str(OUTPUT_DIR / "temp-%(id)s"),
            video_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Convert VTT to readable text
            vtt_file = list(OUTPUT_DIR.glob("temp-*.en.vtt"))
            if vtt_file:
                vtt_path = vtt_file[0]
                
                # Parse VTT format
                with open(vtt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remove VTT metadata
                text_lines = []
                for line in content.split('\n'):
                    if line and not line.startswith('WEBVTT') and not '-->' in line and not line[0].isdigit():
                        text_lines.append(line.strip())
                
                transcript = '\n'.join(text_lines)
                
                # Save transcript
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {video_title}\n")
                    f.write(f"URL: {video_url}\n")
                    f.write(f"Date Downloaded: {datetime.now().isoformat()}\n")
                    f.write(f"Source: YouTube (auto-captions)\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(transcript)
                
                # Cleanup
                vtt_path.unlink()
                
                print(f"[✓] Saved: {output_file.name}")
                log_session("transcript_downloaded", {"title": video_title, "filename": output_file.name})
                return True
        
        print(f"[!] Could not extract transcript for {video_title[:40]}")
        log_session("transcript_extraction_failed", {"title": video_title, "error": result.stderr[:100]})
        return False
    
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Extraction timed out: {video_title[:40]}")
        log_session("extraction_timeout", {"title": video_title})
        return False
    except Exception as e:
        print(f"[ERROR] Failed to download transcript {video_title[:40]}: {e}")
        log_session("transcript_error", {"title": video_title, "error": str(e)})
        return False

def main():
    print("[Path 2: YouTube Transcript Extractor]")
    print(f"Target: YouTube 'Wisdom for the Heart' channel")
    print(f"Method: yt-dlp (no API key)")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    log_session("harvest_started", {"method": "youtube_yt-dlp", "playlists": list(PLAYLISTS.keys())})
    
    # Check dependencies
    if not check_yt_dlp():
        print("[!] Cannot proceed without yt-dlp")
        return
    
    all_videos = []
    for series_name, playlist_url in PLAYLISTS.items():
        videos = extract_playlist_videos(playlist_url, series_name)
        all_videos.extend(videos)
    
    print(f"\n[+] Total videos to process: {len(all_videos)}")
    
    # Download transcripts
    count = 0
    for video in all_videos:
        if download_transcript(video["url"], video["title"]):
            count += 1
            time.sleep(2)  # Small delay between downloads
    
    print(f"\n[✓] YouTube harvest complete: {count}/{len(all_videos)} transcripts downloaded")
    log_session("harvest_completed", {"count": count, "total": len(all_videos)})

if __name__ == "__main__":
    main()
