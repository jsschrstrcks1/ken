#!/usr/bin/env python3
"""
Path 3: Podcast RSS Feed Harvester
- Target: "Wisdom for the Heart" podcast feed (Stephen Davey)
- Method: RSS parsing + full-text extraction from episode descriptions
- Output: /Volumes/1TB External/Projects/Romans/stephen-davey-transcripts/
- Deployment: m4max (100.120.40.114)
"""

import requests
import json
import html
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import time
import re

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("[!] BeautifulSoup4 not installed. Install: pip3 install beautifulsoup4")
    BeautifulSoup = None

# Configuration
OUTPUT_DIR = Path("/Volumes/1TB External/Projects/Romans/stephen-davey-transcripts")
SESSION_LOG = OUTPUT_DIR / "path3-session.json"

# TruthNetwork hosts Stephen Davey's complete sermon archive
TARGET_URL = "https://www.truthnetwork.com/ondemand/wisdom-for-the-heart-dr-stephen-davey/"

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

def scrape_truthnetwork(target_url):
    """Scrape sermon archive from TruthNetwork."""
    try:
        import re
        from bs4 import BeautifulSoup
        
        print(f"[→] Scraping TruthNetwork archive...")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(target_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        episodes = []
        
        # Extract sermon entries (TruthNetwork format)
        # Look for sermon entries with date, title, and description
        sermon_blocks = soup.find_all('div', class_=re.compile(r'sermon|episode|show'))
        
        if not sermon_blocks:
            # Fallback: find all elements with date/title/description pattern
            sermon_blocks = soup.find_all('article')
        
        for block in sermon_blocks:
            # Extract title
            title_elem = block.find(('h2', 'h3', 'h4', 'a'))
            title = title_elem.get_text().strip() if title_elem else "Unknown"
            
            # Extract description
            desc_elem = block.find(('p', 'div'), class_=re.compile(r'desc|summary|content'))
            description = desc_elem.get_text().strip() if desc_elem else ""
            
            # Extract date
            date_elem = block.find(('span', 'time'), class_=re.compile(r'date|published'))
            date_text = date_elem.get_text().strip() if date_elem else ""
            
            if title and title != "Unknown":
                episode = {
                    "title": title,
                    "description": description,
                    "pubdate": date_text,
                    "link": target_url,
                }
                episodes.append(episode)
        
        print(f"[+] Found {len(episodes)} sermons on TruthNetwork")
        log_session("truthnetwork_scraped", {"count": len(episodes)})
        
        return episodes
    
    except Exception as e:
        print(f"[ERROR] Failed to scrape TruthNetwork: {e}")
        log_session("truthnetwork_error", {"error": str(e)})
        return []

def extract_text_from_html(html_content):
    """Extract plain text from HTML/XHTML content."""
    try:
        # Remove HTML tags
        import re
        text = re.sub('<[^<]+?>', '', html_content)
        # Unescape HTML entities
        text = html.unescape(text)
        # Clean up whitespace
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        return text
    except Exception as e:
        print(f"[!] Error parsing HTML: {e}")
        return html_content

def save_episode(episode, episode_num):
    """Save episode to transcript file."""
    try:
        title = episode.get("title", f"Episode {episode_num}")
        
        # Sanitize filename
        safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in title)[:80]
        filename = f"stephen-davey-{safe_title}.txt"
        filepath = OUTPUT_DIR / filename
        
        # Get episode content
        content = episode.get("content") or episode.get("description") or ""
        
        # Clean up HTML if present
        if '<' in content:
            content = extract_text_from_html(content)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\n")
            f.write(f"Published: {episode.get('pubdate', 'Unknown')}\n")
            f.write(f"URL: {episode.get('link', 'N/A')}\n")
            f.write(f"Date Downloaded: {datetime.now().isoformat()}\n")
            f.write(f"Source: Podcast RSS Feed (Wisdom for the Heart)\n")
            f.write("=" * 80 + "\n\n")
            f.write(content)
        
        print(f"[✓] Saved: {filename}")
        log_session("episode_saved", {"title": title, "filename": filename})
        
        return True
    
    except Exception as e:
        print(f"[ERROR] Failed to save episode {episode_num}: {e}")
        log_session("episode_save_error", {"episode": episode_num, "error": str(e)})
        return False

def main():
    print("[Path 3: TruthNetwork Sermon Harvester]")
    print(f"Target: TruthNetwork (Wisdom for the Heart archive)")
    print(f"Method: HTML scraping + description extraction")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    log_session("harvest_started", {"target": "truthnetwork"})
    
    # Scrape sermons
    episodes = scrape_truthnetwork(TARGET_URL)
    
    print(f"\n[+] Total sermons collected: {len(episodes)}")
    
    # Save episodes
    count = 0
    for i, episode in enumerate(episodes, 1):
        if save_episode(episode, i):
            count += 1
            time.sleep(0.5)  # Small delay between saves
    
    print(f"\n[✓] TruthNetwork harvest complete: {count}/{len(episodes)} sermons saved")
    log_session("harvest_completed", {"count": count, "total": len(episodes)})

if __name__ == "__main__":
    main()
