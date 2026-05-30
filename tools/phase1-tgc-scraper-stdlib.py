#!/usr/bin/env python3
"""
Phase 1: The Gospel Coalition Carson Article Harvester (Stdlib-only)

Uses only Python stdlib (urllib, json) — no external dependencies.
Scrapes TGC search results for Carson articles.
Target: 50+ articles, 100,000+ words initially, scalable to full TGC Carson corpus.
"""

import urllib.request
import urllib.parse
import json
import time
from html.parser import HTMLParser
from datetime import datetime
from pathlib import Path
import re
import sys

class LinkExtractor(HTMLParser):
    """Extract links from HTML."""
    def __init__(self):
        super().__init__()
        self.links = []
    
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href' and value:
                    self.links.append(value)

class TGCCarsonHarvester:
    def __init__(self):
        self.base_url = "https://www.thegospelcoalition.org"
        self.output_dir = Path("/Volumes/1TB External/openclaw/workspace-main/carson-harvest/blog-writings")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.articles = []
        self.harvest_log = {
            "started": datetime.now().isoformat(),
            "source": "The Gospel Coalition",
            "articles_found": 0,
            "articles_harvested": 0,
            "total_words": 0,
            "articles": []
        }
    
    def fetch_page(self, url, retry=3):
        """Fetch page with retries."""
        for attempt in range(retry):
            try:
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    return response.read().decode('utf-8', errors='ignore')
            except Exception as e:
                if attempt < retry - 1:
                    time.sleep(2 ** attempt)
                else:
                    print(f"    Error fetching {url}: {e}")
                    return None
    
    def extract_links_from_html(self, html):
        """Extract all links from HTML."""
        extractor = LinkExtractor()
        try:
            extractor.feed(html)
            return extractor.links
        except:
            return []
    
    def get_carson_article_urls(self):
        """Get Carson article URLs from TGC."""
        print(f"Searching The Gospel Coalition for D.A. Carson articles...\n")
        
        # Direct TGC search URL
        search_queries = [
            "D.A. Carson",
            "Donald Carson",
        ]
        
        all_urls = set()
        
        for query in search_queries:
            print(f"  Query: '{query}'")
            try:
                # TGC search endpoint
                search_url = f"{self.base_url}/search?s={urllib.parse.quote(query)}"
                html = self.fetch_page(search_url)
                
                if html:
                    links = self.extract_links_from_html(html)
                    
                    # Filter for article/post URLs
                    article_urls = [
                        l for l in links 
                        if ('article' in l or 'blog' in l or 'post' in l) 
                        and 'thegospelcoalition.org' in l
                        and not l.endswith('#')
                        and 'comment' not in l.lower()
                    ]
                    
                    for url in article_urls:
                        all_urls.add(url)
                    
                    print(f"    Found {len(article_urls)} article links")
            except Exception as e:
                print(f"    Error: {e}")
            
            time.sleep(1)
        
        print(f"\nTotal unique article URLs found: {len(all_urls)}\n")
        return list(all_urls)[:50]  # Start with first 50
    
    def extract_text_from_html(self, html):
        """Simple HTML to text extraction."""
        # Remove scripts and styles
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        html = re.sub(r'<nav[^>]*>.*?</nav>', '', html, flags=re.DOTALL)
        html = re.sub(r'<footer[^>]*>.*?</footer>', '', html, flags=re.DOTALL)
        
        # Extract body or article content
        match = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
        if not match:
            match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL)
        if not match:
            match = re.search(r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
        
        content_html = match.group(1) if match else html
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '\n', content_html)
        
        # Clean whitespace
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        
        return text
    
    def extract_title(self, html):
        """Extract article title."""
        # Try h1
        match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
        if match:
            return match.group(1).strip()
        
        # Try title tag
        match = re.search(r'<title>([^<]+)</title>', html)
        if match:
            return match.group(1).replace(' - The Gospel Coalition', '').strip()
        
        return "Unknown Title"
    
    def save_article(self, article, index):
        """Save article to markdown."""
        if not article or not article.get('content'):
            return False
        
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' 
                            for c in article['title']).rstrip()
        safe_title = safe_title[:70]
        filename = f"tgc-{index:04d}-{safe_title.replace(' ', '-')}.md"
        filepath = self.output_dir / filename
        
        markdown = f"""---
source: "The Gospel Coalition"
title: "{article['title']}"
url: "{article['url']}"
word_count: {article['word_count']}
extracted: "{datetime.now().isoformat()}"
---

# {article['title']}

**Source:** [The Gospel Coalition]({article['url']})

---

{article['content']}

---

_Harvested from gospelcoalition.org_
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown)
            return True
        except Exception as e:
            print(f"      Error saving: {e}")
            return False
    
    def harvest(self):
        """Execute harvest."""
        print("="*80)
        print("PHASE 1: THE GOSPEL COALITION CARSON ARTICLE HARVESTING")
        print("="*80 + "\n")
        
        # Get URLs
        urls = self.get_carson_article_urls()
        
        if not urls:
            print("No articles found.\n")
            return
        
        # Extract content
        print(f"Extracting content from {len(urls)} articles...\n")
        
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] {url[:70]}")
            
            try:
                html = self.fetch_page(url)
                
                if not html:
                    print(f"    ✗ Failed to fetch")
                    continue
                
                title = self.extract_title(html)
                content = self.extract_text_from_html(html)
                word_count = len(content.split())
                
                if word_count < 100:
                    print(f"    ✗ Too short ({word_count} words)")
                    continue
                
                article = {
                    'url': url,
                    'title': title,
                    'content': content,
                    'word_count': word_count,
                }
                
                if self.save_article(article, i):
                    self.harvest_log["articles_harvested"] += 1
                    self.harvest_log["total_words"] += word_count
                    self.harvest_log["articles"].append({
                        "index": i,
                        "title": title,
                        "url": url,
                        "word_count": word_count,
                    })
                    print(f"    ✓ Saved ({word_count} words)")
                else:
                    print(f"    ✗ Save failed")
                
            except Exception as e:
                print(f"    ✗ Error: {e}")
            
            time.sleep(0.5)
        
        # Save log
        log_file = self.output_dir / "TGC_HARVEST_LOG.json"
        with open(log_file, 'w') as f:
            json.dump(self.harvest_log, f, indent=2)
        
        # Summary
        print("\n" + "="*80)
        print("PHASE 1 COMPLETE")
        print("="*80)
        print(f"\nResults:")
        print(f"  Articles harvested: {self.harvest_log['articles_harvested']}")
        print(f"  Total words: {self.harvest_log['total_words']:,}")
        if self.harvest_log['articles_harvested'] > 0:
            avg = self.harvest_log['total_words'] // self.harvest_log['articles_harvested']
            print(f"  Average words/article: {avg:,}")
        print(f"  Output directory: {self.output_dir}")
        print(f"  Log file: {log_file}\n")

if __name__ == "__main__":
    harvester = TGCCarsonHarvester()
    harvester.harvest()
