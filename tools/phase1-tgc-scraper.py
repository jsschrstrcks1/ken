#!/usr/bin/env python3
"""
Phase 1: The Gospel Coalition Carson Article Harvester

Scrapes all Carson articles from The Gospel Coalition (gospelcoalition.org).
Target: 100+ articles, 150,000+ words.

TGC is a public platform with open access to all articles.
No authentication required. No copy restrictions.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
import sys

class TGCCarsonHarvester:
    def __init__(self):
        self.base_url = "https://www.thegospelcoalition.org"
        self.search_endpoint = f"{self.base_url}/search"
        self.output_dir = Path("/Volumes/1TB External/openclaw/workspace-main/carson-harvest/blog-writings")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        
        self.articles = []
        self.harvest_log = {
            "started": datetime.now().isoformat(),
            "source": "The Gospel Coalition",
            "articles_found": 0,
            "articles_harvested": 0,
            "total_words": 0,
            "articles": []
        }
    
    def search_carson_articles(self):
        """Search TGC for Carson articles."""
        print(f"Searching The Gospel Coalition for D.A. Carson articles...\n")
        
        # TGC search endpoint
        search_queries = [
            "D.A. Carson",
            "Donald Carson",
            "Carson theology",
            "Carson baptist",
        ]
        
        all_articles = set()  # Use set to avoid duplicates
        
        for query in search_queries:
            print(f"  Searching: '{query}'")
            try:
                # Make search request
                params = {"s": query}
                response = self.session.get(self.search_endpoint, params=params, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find article links (TGC uses various selectors)
                article_links = soup.find_all('a', class_=['article-link', 'post-link', 'link'], href=True)
                
                # Also try generic approach
                if not article_links:
                    article_links = soup.find_all('a', href=True)
                
                for link in article_links:
                    url = link.get('href', '')
                    # Filter for actual article URLs
                    if '/articles/' in url or '/blogs/' in url:
                        full_url = urljoin(self.base_url, url)
                        if full_url.startswith(self.base_url):
                            all_articles.add(full_url)
                
                print(f"    Found {len(article_links)} links")
                
            except Exception as e:
                print(f"    Error searching '{query}': {e}")
            
            time.sleep(1)  # Respect rate limiting
        
        print(f"\nTotal unique articles found: {len(all_articles)}\n")
        self.harvest_log["articles_found"] = len(all_articles)
        
        return list(all_articles)
    
    def extract_article_content(self, url):
        """Extract article content from TGC article page."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = None
            title_tag = soup.find('h1', class_=['article-title', 'post-title', 'entry-title'])
            if title_tag:
                title = title_tag.get_text(strip=True)
            else:
                title = soup.find('title')
                if title:
                    title = title.get_text(strip=True).replace(' - The Gospel Coalition', '')
            
            # Extract date
            date_str = None
            date_tag = soup.find('time') or soup.find('span', class_=['publish-date', 'posted-on'])
            if date_tag:
                date_str = date_tag.get_text(strip=True)
            
            # Extract author
            author = None
            author_tag = soup.find('span', class_=['author-name', 'by-author']) or soup.find('a', class_=['author-link'])
            if author_tag:
                author = author_tag.get_text(strip=True)
            
            # Extract article content
            content = None
            content_selectors = [
                ('article', {'class': 'article-content'}),
                ('div', {'class': 'entry-content'}),
                ('div', {'class': 'post-content'}),
                ('article', {}),
                ('main', {}),
            ]
            
            for tag_name, attrs in content_selectors:
                content_tag = soup.find(tag_name, attrs)
                if content_tag:
                    # Remove scripts and styles
                    for script in content_tag(['script', 'style', 'nav', 'footer']):
                        script.decompose()
                    content = content_tag.get_text(separator='\n', strip=True)
                    break
            
            if not content:
                return None
            
            # Count words
            word_count = len(content.split())
            
            return {
                'url': url,
                'title': title or 'Unknown Title',
                'author': author or 'Unknown Author',
                'date': date_str or 'Unknown Date',
                'content': content,
                'word_count': word_count,
            }
            
        except Exception as e:
            print(f"    Error extracting {url}: {e}")
            return None
    
    def save_article(self, article, index):
        """Save article to markdown file."""
        if not article or not article['content']:
            return False
        
        # Create safe filename
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' 
                            for c in article['title']).rstrip()
        safe_title = safe_title[:80]  # Limit length
        filename = f"tgc-{index:04d}-{safe_title}.md"
        filepath = self.output_dir / filename
        
        # Create markdown with front matter
        markdown = f"""---
source: "The Gospel Coalition"
title: "{article['title']}"
author: "{article['author']}"
date: "{article['date']}"
url: "{article['url']}"
word_count: {article['word_count']}
extracted: "{datetime.now().isoformat()}"
---

# {article['title']}

**Author:** {article['author']}  
**Date:** {article['date']}  
**Source:** [The Gospel Coalition]({article['url']})

---

{article['content']}

---

_Article harvested from The Gospel Coalition (gospelcoalition.org)_
"""
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown)
            return True
        except Exception as e:
            print(f"    Error saving {filepath}: {e}")
            return False
    
    def harvest(self, max_articles=None):
        """Execute the full harvest."""
        print("="*80)
        print("PHASE 1: THE GOSPEL COALITION CARSON ARTICLE HARVESTING")
        print("="*80 + "\n")
        
        # Step 1: Search for Carson articles
        article_urls = self.search_carson_articles()
        
        if not article_urls:
            print("No articles found. Exiting.\n")
            return
        
        # Limit articles if specified
        if max_articles:
            article_urls = article_urls[:max_articles]
        
        # Step 2: Extract content from each article
        print(f"Extracting content from {len(article_urls)} articles...\n")
        
        for i, url in enumerate(article_urls, 1):
            print(f"[{i}/{len(article_urls)}] Extracting: {url}")
            
            article = self.extract_article_content(url)
            
            if article:
                self.articles.append(article)
                success = self.save_article(article, i)
                
                if success:
                    self.harvest_log["articles"].append({
                        "index": i,
                        "title": article['title'],
                        "url": article['url'],
                        "word_count": article['word_count'],
                    })
                    self.harvest_log["articles_harvested"] += 1
                    self.harvest_log["total_words"] += article['word_count']
                    print(f"    ✓ Saved ({article['word_count']} words)")
                else:
                    print(f"    ✗ Failed to save")
            else:
                print(f"    ✗ Failed to extract")
            
            # Rate limiting
            time.sleep(0.5)
        
        # Step 3: Save harvest log
        log_file = self.output_dir / "TGC_HARVEST_LOG.json"
        with open(log_file, 'w') as f:
            json.dump(self.harvest_log, f, indent=2)
        
        # Summary
        print("\n" + "="*80)
        print("HARVEST COMPLETE")
        print("="*80)
        print(f"\nResults:")
        print(f"  Articles harvested: {self.harvest_log['articles_harvested']}")
        print(f"  Total words: {self.harvest_log['total_words']:,}")
        print(f"  Avg words/article: {self.harvest_log['total_words'] // max(1, self.harvest_log['articles_harvested'])}")
        print(f"  Saved to: {self.output_dir}")
        print(f"  Log: {log_file}\n")

def main():
    harvester = TGCCarsonHarvester()
    
    # Execute harvest (limit to 50 articles for testing, remove limit for full harvest)
    # For production, call with max_articles=None to get all articles
    harvester.harvest(max_articles=None)

if __name__ == "__main__":
    main()
