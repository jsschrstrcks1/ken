#!/usr/bin/env python3
"""
Path 1: Subsplash Harvester
- Target: Wisdom International (thewisdomof.me) via Subsplash backend
- Rate: 25 sermons with 3-minute separation (respectful throttling)
- Output: /Volumes/1TB External/Projects/Romans/stephen-davey-transcripts/
"""

import requests
import time
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

# Configuration
BASE_URL = "https://www.subsplash.com/api/v1"
WISDOM_ORG_ID = "3TZNBD"  # Wisdom International Subsplash ID
OUTPUT_DIR = Path("/Volumes/1TB External/Projects/Romans/stephen-davey-transcripts")
RATE_LIMIT_SECONDS = 180  # 3 minutes between requests
MAX_SERMONS = 25
SESSION_LOG = OUTPUT_DIR / "path1-session.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json"
})

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

def get_sermon_list():
    """Fetch sermon list from Subsplash API."""
    try:
        # Subsplash public API endpoint for sermon archives
        url = f"{BASE_URL}/organization/{WISDOM_ORG_ID}/messages"
        
        print(f"[*] Fetching sermon list from Subsplash...")
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
        
        data = resp.json()
        log_session("sermon_list_fetched", {"count": len(data.get("messages", []))})
        
        return data.get("messages", [])
    
    except Exception as e:
        print(f"[ERROR] Failed to fetch sermon list: {e}")
        log_session("sermon_list_error", {"error": str(e)})
        return []

def download_sermon(sermon_id, sermon_title, book_chapter=None):
    """Download individual sermon transcript."""
    try:
        # Construct Subsplash API URL for sermon details + transcript
        url = f"{BASE_URL}/messages/{sermon_id}"
        
        print(f"[→] Downloading: {sermon_title}...")
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
        
        sermon_data = resp.json()
        transcript_text = sermon_data.get("notes") or sermon_data.get("description") or ""
        
        # Sanitize filename
        safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in sermon_title)[:80]
        filename = f"stephen-davey-{safe_title}.txt"
        filepath = OUTPUT_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Title: {sermon_title}\n")
            f.write(f"Sermon ID: {sermon_id}\n")
            f.write(f"Date Downloaded: {datetime.now().isoformat()}\n")
            f.write(f"Source: Wisdom International (Subsplash)\n")
            f.write("=" * 80 + "\n\n")
            f.write(transcript_text)
        
        print(f"[✓] Saved: {filename}")
        log_session("sermon_downloaded", {"title": sermon_title, "filename": filename})
        
        return True
    
    except Exception as e:
        print(f"[ERROR] Failed to download {sermon_title}: {e}")
        log_session("sermon_download_error", {"title": sermon_title, "error": str(e)})
        return False

def main():
    print("[Path 1: Subsplash Harvester]")
    print(f"Target: Wisdom International (Subsplash)")
    print(f"Rate: {RATE_LIMIT_SECONDS}s between requests")
    print(f"Max: {MAX_SERMONS} sermons")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    log_session("harvest_started", {"max_sermons": MAX_SERMONS, "rate_limit_seconds": RATE_LIMIT_SECONDS})
    
    # Fetch sermon list
    sermons = get_sermon_list()
    if not sermons:
        print("[!] No sermons found. Exiting.")
        log_session("harvest_failed", {"reason": "no_sermons_found"})
        return
    
    # Filter Stephen Davey sermons (by speaker, organization)
    davey_sermons = [s for s in sermons if "Davey" in s.get("speaker", "") or "davey" in s.get("title", "").lower()]
    
    print(f"[+] Found {len(davey_sermons)} Stephen Davey sermons")
    
    # Download with throttling
    count = 0
    for sermon in davey_sermons[:MAX_SERMONS]:
        sermon_id = sermon.get("id")
        sermon_title = sermon.get("title", "Unknown")
        
        if download_sermon(sermon_id, sermon_title):
            count += 1
            
            if count < MAX_SERMONS:
                print(f"[⏳] Waiting {RATE_LIMIT_SECONDS}s before next request...")
                time.sleep(RATE_LIMIT_SECONDS)
    
    print(f"\n[✓] Harvest complete: {count}/{MAX_SERMONS} sermons downloaded")
    log_session("harvest_completed", {"count": count, "max": MAX_SERMONS})

if __name__ == "__main__":
    main()
