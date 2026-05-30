#!/usr/bin/env python3
"""
D.A. Carson Content Extractor from Logos.com

Systematically harvests all Carson materials Ken owns in Logos.
Respects copy-paste limits by chunking extraction.
"""

import json
import time
from datetime import datetime
from pathlib import Path

# Note: This is a planning script. Actual extraction requires:
# 1. Logos API access (if available)
# 2. Or: Browser automation + Logos login
# 3. Or: Manual copy-paste with documented sources

CARSON_SEARCH_QUERIES = [
    "Carson sermon",
    "D.A. Carson",
    "Donald Carson",
    "Carson commentary",
    "Carson Exegetical",
    "Carson Christ Culture",
    "Carson Divine Sovereignty",
    "Carson Gagging God",
]

KNOWN_CARSON_RESOURCES = {
    # Sermons
    "carson-sermon-library": {
        "title": "D.A. Carson Sermon Library",
        "type": "sermon_collection",
        "copy_limit": "restricted",
        "status": "needs_extraction",
        "estimated_sermons": 300,
    },
    # Commentaries
    "gospel-john": {
        "title": "The Gospel According to John (Pillar New Testament Commentary)",
        "type": "commentary",
        "copy_limit": "restricted",
        "status": "needs_extraction",
        "word_count": 150000,
    },
    # Books
    "exegetical-fallacies": {
        "title": "Exegetical Fallacies",
        "type": "book",
        "copy_limit": "restricted",
        "status": "needs_extraction",
        "word_count": 40000,
    },
    "divine-sovereignty": {
        "title": "Divine Sovereignty and Human Responsibility",
        "type": "book",
        "copy_limit": "restricted",
        "status": "needs_extraction",
        "word_count": 80000,
    },
    "christ-culture": {
        "title": "Christ and Culture Revisited",
        "type": "book",
        "copy_limit": "restricted",
        "status": "needs_extraction",
        "word_count": 60000,
    },
    "gagging-god": {
        "title": "The Gagging of God: Christianity Confronts Pluralism",
        "type": "book",
        "copy_limit": "restricted",
        "status": "needs_extraction",
        "word_count": 200000,
    },
    # Other known titles
    "intolerance-tolerance": {
        "title": "The Intolerance of Tolerance",
        "type": "book",
        "copy_limit": "unknown",
        "status": "inventory_needed",
        "word_count": 40000,
    },
    "love-hard-places": {
        "title": "Love in Hard Places",
        "type": "book",
        "copy_limit": "unknown",
        "status": "inventory_needed",
        "word_count": 50000,
    },
    "how-long-o-lord": {
        "title": "How Long, O Lord? Reflections on Suffering and Evil",
        "type": "book",
        "copy_limit": "unknown",
        "status": "inventory_needed",
        "word_count": 60000,
    },
}

class CarsonExtractor:
    def __init__(self):
        self.harvest_dir = Path("/Volumes/1TB External/openclaw/workspace-main/carson-harvest")
        self.harvest_dir.mkdir(exist_ok=True)
        self.log = []
        self.extracted_content = {}
        
    def log_action(self, action, status, details=""):
        """Log extraction actions."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "details": details,
        }
        self.log.append(entry)
        print(f"[{action}] {status}: {details}")
    
    def create_logos_inventory(self):
        """Create inventory of known Carson resources in Logos."""
        inventory_file = self.harvest_dir / "LOGOS_INVENTORY.md"
        
        content = "# D.A. Carson Resources in Logos.com\n\n"
        content += "**Inventory Date:** " + datetime.now().isoformat() + "\n\n"
        content += "## Resources Needing Extraction\n\n"
        
        total_words = 0
        for key, resource in KNOWN_CARSON_RESOURCES.items():
            if resource["copy_limit"] == "restricted":
                content += f"### {resource['title']}\n"
                content += f"- **Type:** {resource['type']}\n"
                content += f"- **Copy Limit:** {resource['copy_limit']}\n"
                content += f"- **Estimated Words:** {resource.get('word_count', 'unknown')}\n"
                content += f"- **Status:** {resource['status']}\n"
                content += f"- **Action:** Requires manual/chunked extraction from Logos\n\n"
                
                if isinstance(resource.get('word_count'), int):
                    total_words += resource['word_count']
        
        content += f"\n## Summary\n"
        content += f"- **Total Resources Identified:** {len([r for r in KNOWN_CARSON_RESOURCES.values() if r['copy_limit'] == 'restricted'])}\n"
        content += f"- **Estimated Total Words:** {total_words:,}\n"
        content += f"- **Extraction Status:** READY TO BEGIN\n"
        
        with open(inventory_file, "w") as f:
            f.write(content)
        
        self.log_action("create_inventory", "success", f"Inventory created: {inventory_file}")
        return inventory_file
    
    def create_extraction_guide(self):
        """Create step-by-step extraction guide for Logos materials."""
        guide_file = self.harvest_dir / "EXTRACTION_GUIDE.md"
        
        content = """# Logos.com Manual Extraction Guide

## Overview
Due to Logos copy-paste limits, extraction must be done in chunks.
This guide provides the process.

## Resources to Extract (Priority Order)

### 1. Carson Sermon Library (Highest Priority)
**Logos Location:** Search "D.A. Carson Sermon Library"
**Process:**
1. Open in Logos
2. Copy sermons in chunks (10–15 at a time)
3. Paste into individual .md files
4. Save as: `/carson-harvest/sermons/sermon-XXXX.md`

**Fields to capture:**
- Date preached
- Title
- Bible text
- Full sermon text
- Any notes/context

### 2. Gospel of John Commentary
**Logos Location:** Search "Gospel According to John Carson"
**Process:**
1. Open by book chapter
2. Copy chapter sections (Logos may limit per chapter)
3. Save as: `/carson-harvest/logos-books/gospel-john-Ch01.md` (etc.)

### 3. Exegetical Fallacies
**Logos Location:** Search "Exegetical Fallacies Carson"
**Process:**
1. Copy chapter by chapter
2. Save as: `/carson-harvest/logos-books/exegetical-fallacies-Ch01.md` (etc.)

### 4. Divine Sovereignty & Human Responsibility
**Similar process as above**

### 5. Christ and Culture Revisited
**Similar process as above**

### 6. The Gagging of God (Largest; ~200k words)
**Process:**
1. This is long; expect 15–20 sessions
2. Copy section by section
3. Save progressively

## File Naming Convention

```
/carson-harvest/
├─ sermons/
│  ├─ sermon-2024-001-john-516.md
│  ├─ sermon-2024-002-romans-3.md
│  └─ ...
│
├─ logos-books/
│  ├─ gospel-john-Ch01.md
│  ├─ gospel-john-Ch02.md
│  ├─ exegetical-fallacies-Ch01.md
│  ├─ divine-sovereignty-Ch01.md
│  ├─ christ-culture-Ch01.md
│  └─ gagging-god-Pt1-Ch01.md
│
└─ EXTRACTION_LOG.json
```

## Front Matter for Each File

Every extracted file should include:

```yaml
---
source: "Logos.com"
resource_title: "[Logos resource name]"
author: "D.A. Carson"
type: "[sermon|commentary|book]"
extraction_date: "2026-05-30"
logos_copy_limit: "restricted"
notes: "[Any special notes about extraction]"
---

[Content here]
```

## Tracking Progress

After each extraction session:
1. Record in `EXTRACTION_LOG.json`:
   ```json
   {
     "date": "2026-05-30",
     "resource": "Carson Sermon Library",
     "sermons_extracted": 15,
     "words_extracted": 12500,
     "status": "in_progress"
   }
   ```
2. Commit to git: `git commit -m "harvest: Carson [resource] — X sermons/chapters extracted"`
3. Update inventory

## Estimated Timeline

- **Carson Sermon Library:** 20 sessions × 1–2 hours = 20–40 hours
- **Gospel of John:** 21 chapters × 30 min = 10.5 hours
- **Exegetical Fallacies:** 8 chapters × 20 min = 2.7 hours
- **Divine Sovereignty:** 10 chapters × 30 min = 5 hours
- **Christ and Culture:** 6 chapters × 25 min = 2.5 hours
- **Gagging of God:** 40+ sections × 20 min = 13+ hours
- **Total:** 50–70 hours of focused extraction

## Tips for Efficient Extraction

1. **Batch similar work:** Do all sermon extraction together, then all books
2. **Use Logos' native export if available:** Check for "Export" option
3. **Screenshot + OCR fallback:** If copy fails, take screenshot + OCR
4. **Track word counts:** Use `wc -w` to verify extraction completeness
5. **Deduplication:** Check for overlaps across resources later

## When Complete

1. Consolidate all files into unified corpus
2. Count total words: `find /carson-harvest -name "*.md" | xargs wc -w`
3. Commit with: `git commit -m "harvest: Carson complete — [total] words extracted from Logos"`
4. Ready for LoRA training

---

**This is a long but systematic process. Break it into small sessions.**
"""
        
        with open(guide_file, "w") as f:
            f.write(content)
        
        self.log_action("create_guide", "success", f"Extraction guide created: {guide_file}")
        return guide_file
    
    def create_tracking_log(self):
        """Create JSON tracking file for extraction sessions."""
        log_file = self.harvest_dir / "EXTRACTION_LOG.json"
        
        tracking = {
            "harvest_started": datetime.now().isoformat(),
            "target_author": "D.A. Carson",
            "target_words": 600000,
            "sessions": [],
            "summary": {
                "total_words_extracted": 0,
                "total_files_created": 0,
                "resources_completed": [],
                "resources_in_progress": [],
            }
        }
        
        with open(log_file, "w") as f:
            json.dump(tracking, f, indent=2)
        
        self.log_action("create_tracking", "success", f"Tracking log created: {log_file}")
        return log_file
    
    def create_directories(self):
        """Create directory structure for Carson harvest."""
        dirs = [
            self.harvest_dir / "sermons",
            self.harvest_dir / "logos-books",
            self.harvest_dir / "blog-writings",
            self.harvest_dir / "academic-papers",
            self.harvest_dir / "interviews",
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(exist_ok=True)
            self.log_action("mkdir", "success", str(dir_path))
    
    def start_harvest(self):
        """Initialize Carson harvest."""
        print("\n" + "="*80)
        print("D.A. CARSON LOGOS HARVEST STARTED")
        print("="*80 + "\n")
        
        self.create_directories()
        self.create_logos_inventory()
        self.create_extraction_guide()
        self.create_tracking_log()
        
        print("\n" + "="*80)
        print("READY FOR EXTRACTION")
        print("="*80)
        print("\nNext steps:")
        print("1. Go to Logos.com (app.logos.com)")
        print("2. Search for Carson resources using the inventory guide")
        print("3. Extract content following EXTRACTION_GUIDE.md")
        print("4. Save files to /carson-harvest/ with proper naming")
        print("5. Commit progress regularly to git")
        print("\nEstimated total time: 50–70 hours of focused extraction")
        print("Estimated total yield: 600,000+ words\n")

if __name__ == "__main__":
    extractor = CarsonExtractor()
    extractor.start_harvest()
