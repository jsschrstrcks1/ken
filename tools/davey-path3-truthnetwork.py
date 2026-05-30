#!/usr/bin/env python3
"""
Path 3: TruthNetwork Direct Scraper
- Target: TruthNetwork.com Stephen Davey sermon archive
- Method: Regex + text extraction from HTML
- Output: /Volumes/1TB External/Projects/Romans/stephen-davey-transcripts/
"""

import requests
import json
import re
from pathlib import Path
from datetime import datetime
import time

# Configuration
OUTPUT_DIR = Path("/Volumes/1TB External/Projects/Romans/stephen-davey-transcripts")
SESSION_LOG = OUTPUT_DIR / "path3-session.json"

ARCHIVE_URL = "https://www.truthnetwork.com/ondemand/wisdom-for-the-heart-dr-stephen-davey/"

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

def scrape_truthnetwork():
    """Scrape Stephen Davey sermons from TruthNetwork."""
    try:
        print(f"[→] Fetching TruthNetwork archive...")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        response = requests.get(ARCHIVE_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        html = response.text
        
        # Extract sermon entries using regex
        # Look for pattern: date | title | description
        episodes = []
        
        # Pattern 1: Lines with date (e.g., "May 26 2026") followed by title and description
        # This matches the structure visible in the fetched content
        pattern = r'(\w+\s+\d{1,2}\s+\d{4})\s*\n\s*([^\n]+?)\s*\n+\s*([^<\n]{20,500}?)(?:\n|<)'
        
        matches = re.finditer(pattern, html, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            date_str = match.group(1).strip()
            title = match.group(2).strip()
            description = match.group(3).strip()
            
            # Clean up
            title = re.sub(r'<[^>]+>', '', title)
            description = re.sub(r'<[^>]+>', '', description)
            
            if title and len(title) > 5:  # Filter out noise
                episode = {
                    "date": date_str,
                    "title": title,
                    "description": description,
                    "url": ARCHIVE_URL
                }
                episodes.append(episode)
        
        print(f"[+] Extracted {len(episodes)} sermon entries")
        log_session("sermons_extracted", {"count": len(episodes)})
        
        return episodes
    
    except Exception as e:
        print(f"[ERROR] Failed to scrape TruthNetwork: {e}")
        log_session("scrape_error", {"error": str(e)})
        return []

def save_sermon(episode, episode_num):
    """Save sermon to transcript file."""
    try:
        title = episode.get("title", f"Sermon {episode_num}")
        date = episode.get("date", "Unknown")
        description = episode.get("description", "")
        
        # Sanitize filename
        safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in title)[:80]
        filename = f"stephen-davey-{safe_title}.txt"
        filepath = OUTPUT_DIR / filename
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\n")
            f.write(f"Preached: {date}\n")
            f.write(f"Source: TruthNetwork (Wisdom for the Heart)\n")
            f.write(f"URL: {episode.get('url', 'N/A')}\n")
            f.write(f"Downloaded: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"{description}\n")
        
        print(f"[✓] Saved: {filename}")
        log_session("sermon_saved", {"title": title, "filename": filename})
        
        return True
    
    except Exception as e:
        print(f"[ERROR] Failed to save sermon {episode_num}: {e}")
        log_session("save_error", {"episode": episode_num, "error": str(e)})
        return False

def main():
    print("[Path 3: TruthNetwork Sermon Harvester]")
    print(f"Target: TruthNetwork (Wisdom for the Heart)")
    print(f"Method: HTML regex extraction")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    log_session("harvest_started", {"target": "truthnetwork"})
    
    # Scrape sermons
    episodes = scrape_truthnetwork()
    
    if not episodes:
        print("[!] No sermons found. Check the archive URL or page structure.")
        log_session("harvest_failed", {"reason": "no_sermons_found"})
        return
    
    print(f"\n[+] Total sermons to save: {len(episodes)}")
    
    # Save sermons
    count = 0
    for i, episode in enumerate(episodes, 1):
        if save_sermon(episode, i):
            count += 1
            if i % 5 == 0:
                time.sleep(1)  # Small delay every 5 saves
    
    print(f"\n[✓] TruthNetwork harvest complete: {count}/{len(episodes)} sermons saved")
    log_session("harvest_completed", {"count": count, "total": len(episodes)})

if __name__ == "__main__":
    main()
