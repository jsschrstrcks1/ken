#!/usr/bin/env python3
"""
Path 3: Podcast RSS Feed Harvester
- Target: "Wisdom for the Heart" podcast feed (Stephen Davey)
- Method: RSS parsing + full-text extraction from episode descriptions
- Output: /Volumes/1TB External/Projects/Romans/stephen-davey-transcripts/
- Deployment: m4max (100.120.40.114)
"""

import xml.etree.ElementTree as ET
import requests
import json
import html
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import time

# Configuration
OUTPUT_DIR = Path("/Volumes/1TB External/Projects/Romans/stephen-davey-transcripts")
SESSION_LOG = OUTPUT_DIR / "path3-session.json"

# Podcast RSS feeds for Stephen Davey / Wisdom International
FEED_URLS = {
    "wisdom_for_heart": "https://www.subsplash.com/api/v1/organization/3TZNBD/rss/podcast",
    "wisdom_journey": "https://feeds.megaphone.fm/wisdom-journey",  # Alternative feed
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

def fetch_feed(feed_url):
    """Fetch and parse RSS feed."""
    try:
        print(f"[→] Fetching feed: {feed_url[:60]}...")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(feed_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        # Extract episodes
        episodes = []
        for item in root.findall(".//item"):
            title_elem = item.find("title")
            desc_elem = item.find("description")
            content_elem = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")
            pubdate_elem = item.find("pubDate")
            link_elem = item.find("link")
            
            episode = {
                "title": title_elem.text if title_elem is not None else "Unknown",
                "description": desc_elem.text if desc_elem is not None else "",
                "content": content_elem.text if content_elem is not None else "",
                "pubdate": pubdate_elem.text if pubdate_elem is not None else "",
                "link": link_elem.text if link_elem is not None else "",
            }
            
            episodes.append(episode)
        
        print(f"[+] Found {len(episodes)} episodes in feed")
        log_session("feed_fetched", {"feed": feed_url[:60], "episodes": len(episodes)})
        
        return episodes
    
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch feed: {e}")
        log_session("feed_error", {"feed": feed_url, "error": str(e)})
        return []
    except ET.ParseError as e:
        print(f"[ERROR] Failed to parse feed XML: {e}")
        log_session("feed_parse_error", {"feed": feed_url, "error": str(e)})
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
    print("[Path 3: Podcast RSS Feed Harvester]")
    print(f"Target: Wisdom for the Heart podcast feed")
    print(f"Method: RSS parsing + HTML extraction")
    print(f"Output: {OUTPUT_DIR}")
    print()
    
    log_session("harvest_started", {"feeds": list(FEED_URLS.keys())})
    
    all_episodes = []
    for feed_name, feed_url in FEED_URLS.items():
        print(f"\n[Feed] {feed_name}")
        episodes = fetch_feed(feed_url)
        all_episodes.extend(episodes)
        time.sleep(2)  # Respectful delay between feeds
    
    print(f"\n[+] Total episodes collected: {len(all_episodes)}")
    
    # Save episodes
    count = 0
    for i, episode in enumerate(all_episodes, 1):
        if save_episode(episode, i):
            count += 1
    
    print(f"\n[✓] Podcast harvest complete: {count}/{len(all_episodes)} episodes saved")
    log_session("harvest_completed", {"count": count, "total": len(all_episodes)})

if __name__ == "__main__":
    main()
