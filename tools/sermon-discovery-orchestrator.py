#!/usr/bin/env python3
"""
Sermon Discovery Orchestrator
===============================

Find NEW (unpublished) content for all authors in the LoRA ecosystem.

Strategies:
  1. YouTube: yt-dlp + transcript extraction
  2. MP3 Podcasts: Direct feeds, Whisper transcription
  3. PDF Sermons: Direct downloads, text extraction
  4. Web Pages: Direct HTML scraping, text extraction
  5. Logos/Bible.com APIs: Structured data harvesting
  6. Twitter/Social: Latest announcements + links

Sources by Author:
  - Al Mohler: albertmohler.com, Podcast RSS, Twitter
  - Alistair Begg: truthforlife.org RSS, Logos, YouTube
  - D.A. Carson: TEDS.org, TGC (already covered), Logos
  - John MacArthur: GTY.org (Grace to You), YouTube, Logos
  - Conrad Mbewe: African Reformed network sites
  - Jeff Noblit: Founders.org, YouTube, sermon archives
  - TGC: thegospelcoalition.org RSS/API
  - Danny Akin: SEBTS, SBTS chapel feeds
  - Sinclair Ferguson: Ligonier.org, Westminster Seminary
  - Stephen Davey: TruthNetwork.com, YouTube (NEW)
  - David Platt: Radical.net, Logos, YouTube (NEW)
  - R.C. Sproul: Ligonier.org, YouTube, Logos
  - Tom Ascol: Founders.org, YouTube
  - Paul Washer: HeartCry RSS, YouTube
  - Mark Dever: 9Marks.org, Capitol Hill Baptist
  - John Frame: Personal site, seminary archives
  + All others: YouTube, Logos, direct websites

Output:
  - New content discovered + metadata (source, date, URL)
  - Deduplicated against existing archive
  - Ready for transcription pipeline (Whisper for audio)
  - JSONL format for LoRA training data prep

"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SermonSource:
    """Discovered sermon metadata"""
    author: str
    title: str
    date: str
    source_url: str
    source_type: str  # youtube, podcast, pdf, webpage, logos, etc.
    content_type: str  # text, audio, video
    download_url: str
    status: str  # new, duplicate, queued, transcribed
    last_checked: str

class DiscoveryOrchestrator:
    """Main orchestrator for discovering new sermon content"""
    
    def __init__(self):
        self.archive_root = Path("/Volumes/1TB External/openclaw-main/sermon-archive/_EXTERNAL-PREACHERS")
        self.projects_root = Path("/Volumes/1TB External/Projects/Romans")
        self.discovery_log = Path.home() / "lora-data" / "discovery-log.jsonl"
        self.discovery_state = Path.home() / "lora-data" / "discovery-state.json"
        
        self.authors = self._load_authors()
        self.existing_hashes = self._load_existing_hashes()
        self.discovery_state_data = self._load_discovery_state()
        
    def _load_authors(self):
        """Load all authors from archive"""
        authors = {}
        for author_dir in self.archive_root.iterdir():
            if author_dir.is_dir() and not author_dir.name.startswith('_'):
                authors[author_dir.name] = {
                    "path": author_dir,
                    "sources": self._get_sources_for_author(author_dir.name)
                }
        return authors
    
    def _get_sources_for_author(self, author_name):
        """Return known content sources for this author"""
        sources_map = {
            "al-mohler": {
                "website": "https://www.albertmohler.com/podcast",
                "podcast_feed": "https://www.albertmohler.com/feed/podcast",
                "logos": True,
                "youtube": "https://www.youtube.com/@albertmohler",
            },
            "alistair-begg": {
                "website": "https://www.truthforlife.org",
                "podcast_feed": "https://www.truthforlife.org/feed/podcast",
                "logos": True,
                "youtube": "https://www.youtube.com/@TruthForLife",
            },
            "macarthur": {
                "website": "https://www.gty.org/library",
                "podcast_feed": "https://feeds.gty.org/podcast",
                "logos": True,
                "youtube": "https://www.youtube.com/@MacArthurPastor",
            },
            "danny-akin": {
                "sebts": "https://chapel.sebts.edu",
                "sbts": "https://chapel.sbts.edu",
                "podcast_feed": "https://www.danielakin.org/feed",
                "logos": True,
            },
            "sproul": {
                "website": "https://www.ligonier.org/rc-sproul",
                "podcast_feed": "https://www.ligonier.org/podcast/feed",
                "logos": True,
                "youtube": "https://www.youtube.com/@LigonierMinistries",
            },
            "tgc": {
                "website": "https://www.thegospelcoalition.org/resources",
                "podcast_feed": "https://www.thegospelcoalition.org/feed/podcast",
            },
            "stephen-davey": {
                "website": "https://www.truthnetwork.com",
                "youtube": "https://www.youtube.com/@WisdomInternational",
            },
            "david-platt": {
                "website": "https://www.radical.net/resources",
                "logos": True,
                "youtube": "https://www.youtube.com/@DavidPlattResources",
            },
            "mark-dever": {
                "website": "https://www.9marks.org",
                "youtube": "https://www.youtube.com/@9Marks",
            },
            "tom-ascol": {
                "website": "https://www.founders.org",
                "youtube": "https://www.youtube.com/@FoundersMinistries",
            },
            "paul-washer": {
                "website": "https://www.heartcrymissionary.com",
                "podcast_feed": "https://www.heartcrymissionary.com/podcast",
            },
        }
        return sources_map.get(author_name, {})
    
    def _load_existing_hashes(self):
        """Load hashes of existing content to detect duplicates"""
        hashes = set()
        
        for author_dir in self.archive_root.iterdir():
            if not author_dir.is_dir():
                continue
            
            for content_file in author_dir.rglob("*.md"):
                try:
                    with open(content_file, 'r', errors='ignore') as f:
                        content = f.read()
                        # Hash first 1000 chars to detect duplicates
                        h = hashlib.md5(content[:1000].encode()).hexdigest()
                        hashes.add(h)
                except:
                    pass
        
        logger.info(f"Loaded {len(hashes)} existing content hashes")
        return hashes
    
    def _load_discovery_state(self):
        """Load last discovery state (when did we last check each source?)"""
        if self.discovery_state.exists():
            with open(self.discovery_state, 'r') as f:
                return json.load(f)
        return {"authors": {}, "last_check": datetime.now().isoformat()}
    
    def _save_discovery_state(self):
        """Save discovery state"""
        self.discovery_state.parent.mkdir(parents=True, exist_ok=True)
        with open(self.discovery_state, 'w') as f:
            json.dump(self.discovery_state_data, f, indent=2)
    
    def discover_youtube(self, author_name: str, youtube_url: str) -> list:
        """
        Discover new YouTube sermons
        
        Requires: yt-dlp installed
        
        Process:
          1. Fetch video list from channel
          2. Extract metadata (date, title, duration)
          3. Compare against existing
          4. Queue for transcript extraction (Whisper)
        """
        logger.info(f"[{author_name}] Discovering YouTube channel: {youtube_url}")
        
        # Placeholder: actual implementation uses yt-dlp
        # yt-dlp -j --flat-playlist <url> > videos.json
        # Then parse JSON for date, title, video_id, duration
        
        new_sermons = []
        # TODO: Implement yt-dlp integration
        return new_sermons
    
    def discover_podcast_feed(self, author_name: str, feed_url: str) -> list:
        """
        Discover new podcasts from RSS feed
        
        Process:
          1. Fetch RSS feed
          2. Parse episodes (date, title, audio URL, duration)
          3. Compare against existing
          4. Queue for Whisper transcription
        """
        logger.info(f"[{author_name}] Checking podcast feed: {feed_url}")
        
        new_sermons = []
        # TODO: Implement RSS feed parsing + feedparser
        return new_sermons
    
    def discover_logos_api(self, author_name: str) -> list:
        """
        Discover new sermons via Logos API (requires auth)
        
        Process:
          1. Query Logos API for author
          2. Filter to date range (since last check)
          3. Extract metadata
          4. Check for duplicates
        """
        logger.info(f"[{author_name}] Querying Logos API")
        
        new_sermons = []
        # TODO: Implement Logos API integration
        # Requires: HF_LOGOS_API_TOKEN
        return new_sermons
    
    def discover_website_scrape(self, author_name: str, website_url: str) -> list:
        """
        Discover new sermons by scraping website
        
        Process:
          1. Fetch website (using web_fetch tool or requests)
          2. Parse HTML for sermon links
          3. Extract metadata
          4. Download PDFs or direct text links
        """
        logger.info(f"[{author_name}] Scraping website: {website_url}")
        
        new_sermons = []
        # TODO: Implement website scraping (BeautifulSoup)
        return new_sermons
    
    def discover_all(self) -> dict:
        """
        Orchestrate discovery across all authors and sources
        
        Returns:
          {
            "new_discovered": [SermonSource, ...],
            "duplicates_found": int,
            "errors": [str, ...],
            "summary": {...}
          }
        """
        results = {
            "new_discovered": [],
            "duplicates_found": 0,
            "errors": [],
            "timestamp": datetime.now().isoformat(),
        }
        
        logger.info("=" * 80)
        logger.info("SERMON DISCOVERY ORCHESTRATOR - STARTING")
        logger.info("=" * 80)
        
        for author_name, author_data in self.authors.items():
            sources = author_data["sources"]
            
            logger.info(f"\n📖 {author_name}")
            
            if not sources:
                logger.info(f"   ⚠️  No known sources configured")
                continue
            
            # YouTube discovery
            if "youtube" in sources:
                logger.info(f"   📺 YouTube: {sources['youtube']}")
                new = self.discover_youtube(author_name, sources['youtube'])
                results["new_discovered"].extend(new)
            
            # Podcast RSS discovery
            if "podcast_feed" in sources:
                logger.info(f"   🎙️  Podcast: {sources['podcast_feed']}")
                new = self.discover_podcast_feed(author_name, sources['podcast_feed'])
                results["new_discovered"].extend(new)
            
            # Website scraping
            if "website" in sources:
                logger.info(f"   🌐 Website: {sources['website']}")
                new = self.discover_website_scrape(author_name, sources['website'])
                results["new_discovered"].extend(new)
            
            # Logos API (if configured)
            if sources.get("logos"):
                logger.info(f"   📚 Logos API")
                new = self.discover_logos_api(author_name)
                results["new_discovered"].extend(new)
        
        logger.info(f"\n" + "=" * 80)
        logger.info(f"DISCOVERY COMPLETE")
        logger.info(f"=" * 80)
        logger.info(f"New sermons discovered: {len(results['new_discovered'])}")
        logger.info(f"Duplicates found: {results['duplicates_found']}")
        logger.info(f"Errors: {len(results['errors'])}")
        
        return results
    
    def save_results(self, results: dict):
        """Save discovery results to JSONL log"""
        self.discovery_log.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.discovery_log, 'a') as f:
            for sermon in results['new_discovered']:
                f.write(json.dumps(asdict(sermon)) + "\n")
        
        logger.info(f"Results saved to {self.discovery_log}")

def main():
    """Main entry point"""
    orchestrator = DiscoveryOrchestrator()
    
    # Discover new content
    results = orchestrator.discover_all()
    
    # Save results
    orchestrator.save_results(results)
    
    # Update state
    orchestrator.discovery_state_data["last_check"] = datetime.now().isoformat()
    orchestrator._save_discovery_state()
    
    print(f"\n✅ Discovery complete. Results in: {orchestrator.discovery_log}")

if __name__ == "__main__":
    main()
