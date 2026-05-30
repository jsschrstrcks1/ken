#!/usr/bin/env python3
"""
SEBTS Seminary Podcast Extraction Pipeline

Extract all SEBTS chapel + podcast episodes:
  1. Discover RSS feeds
  2. Download audio
  3. Transcribe with Whisper
  4. Route to SEBTS Institutional + Individual Faculty LoRAs
  5. Prepare JSONL training data

Usage:
  python3 sebts-podcast-extractor.py [--limit 50] [--model medium]

Output:
  ~/lora-data/sebts-transcriptions/     (.md files)
  ~/lora-data/sebts/train.jsonl         (institutional LoRA)
  ~/lora-data/gregg-allison/train.jsonl (faculty LoRAs)
  etc.
"""

import argparse
import feedparser
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import Dict, List


# ============================================================================
# SEBTS FEED CONFIGURATION
# ============================================================================

SEBTS_FEEDS = {
    "chapel": "https://www.sebts.edu/chapel/feed/",
    "podcast": "https://www.sebts.edu/podcast/feed/",
    "seminary": "https://www.sebts.edu/seminary/feed/",
}

FACULTY_PATTERNS = {
    "Russell Moore": ["moore", "russell"],
    "Gregg Allison": ["allison", "gregg"],
    "Owen Strachan": ["strachan", "owen", "worldview"],
    "Keith Whitfield": ["whitfield", "keith", "new testament"],
    "Dan Doriani": ["doriani", "dan", "old testament"],
    "Matthew Barrett": ["barrett", "matthew", "theology"],
    "Jason Thacker": ["thacker", "jason", "ethics"],
    "Tom Schreiner": ["schreiner", "tom"],
    "Gregg Allison": ["allison", "gregg"],
}


# ============================================================================
# PHASE 1: DISCOVERY
# ============================================================================

def discover_feeds(limit: int = 100) -> Dict[str, List[Dict]]:
    """Discover SEBTS podcast feeds and extract episode metadata."""
    
    print("=" * 80)
    print("PHASE 1: FEED DISCOVERY")
    print("=" * 80)
    
    discovery_dir = Path.home() / "lora-data" / "sebts-discovery"
    discovery_dir.mkdir(parents=True, exist_ok=True)
    
    all_episodes = {}
    
    for feed_name, feed_url in SEBTS_FEEDS.items():
        print(f"\n📡 {feed_name}...", end=" ", flush=True)
        
        try:
            feed = feedparser.parse(feed_url)
            episodes = feed.entries[:limit]
            
            feed_data = {
                "feed_name": feed_name,
                "feed_url": feed_url,
                "title": feed.feed.get('title', 'Unknown'),
                "total_episodes": len(episodes),
                "episodes": []
            }
            
            for episode in episodes:
                # Extract audio URL
                audio_url = None
                
                # Try media_content
                if hasattr(episode, 'media_content') and episode.media_content:
                    audio_url = episode.media_content[0].get('url')
                
                # Try enclosure (standard podcast)
                if not audio_url and hasattr(episode, 'enclosures'):
                    for enc in episode.enclosures:
                        if 'audio' in enc.type:
                            audio_url = enc.href
                            break
                
                # Try links
                if not audio_url:
                    for link in episode.get('links', []):
                        if link.get('type', '').startswith('audio'):
                            audio_url = link.get('href')
                            break
                
                episode_data = {
                    "title": episode.get('title', 'Unknown'),
                    "published": episode.get('published', 'Unknown'),
                    "audio_url": audio_url,
                    "duration": episode.get('itunes_duration', 'Unknown'),
                    "summary": (episode.get('summary', '') or '')[:200],
                    "link": episode.get('link', '')
                }
                
                feed_data["episodes"].append(episode_data)
            
            # Save feed data
            output_file = discovery_dir / f"{feed_name}-discovery.json"
            with open(output_file, "w") as f:
                json.dump(feed_data, f, indent=2)
            
            all_episodes[feed_name] = feed_data["episodes"]
            print(f"✓ {len(episodes)} episodes")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            all_episodes[feed_name] = []
    
    print(f"\n✅ Discovery complete: {discovery_dir}")
    return all_episodes


# ============================================================================
# PHASE 2: AUDIO DOWNLOAD
# ============================================================================

def download_audio(all_episodes: Dict[str, List[Dict]]) -> List[Path]:
    """Download all podcast audio files."""
    
    print("\n" + "=" * 80)
    print("PHASE 2: AUDIO DOWNLOAD")
    print("=" * 80)
    
    audio_queue = Path.home() / "lora-data" / "sebts-audio-queue"
    audio_queue.mkdir(parents=True, exist_ok=True)
    
    downloaded_files = []
    
    for feed_name, episodes in all_episodes.items():
        print(f"\n📥 {feed_name}...")
        
        for i, episode in enumerate(episodes, 1):
            audio_url = episode.get("audio_url")
            title = episode.get("title", f"episode-{i}").replace("/", "-")[:50]
            
            if not audio_url:
                continue
            
            output_file = audio_queue / f"{feed_name}-{i:03d}-{title}.mp3"
            
            if output_file.exists():
                print(f"  ✓ Already present: {title}")
                downloaded_files.append(output_file)
                continue
            
            try:
                print(f"  📥 {title}...", end=" ", flush=True)
                urllib.request.urlretrieve(audio_url, output_file)
                print("✓")
                downloaded_files.append(output_file)
            except Exception as e:
                print(f"✗ Error: {e}")
    
    print(f"\n✅ Download complete: {audio_queue}")
    print(f"   Total files: {len(downloaded_files)}")
    return downloaded_files


# ============================================================================
# PHASE 3: TRANSCRIPTION
# ============================================================================

def transcribe_audio(audio_files: List[Path], model: str = "medium") -> Dict[Path, str]:
    """Transcribe audio files with Whisper."""
    
    print("\n" + "=" * 80)
    print("PHASE 3: TRANSCRIPTION")
    print("=" * 80)
    
    output_dir = Path.home() / "lora-data" / "sebts-transcriptions"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    transcripts = {}
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"[{i}/{len(audio_files)}] {audio_file.name[:60]}", end=" ", flush=True)
        
        try:
            # Transcribe
            result = subprocess.run([
                'whisper',
                str(audio_file),
                '--model', model,
                '--output_format', 'txt',
                '--output_dir', str(output_dir),
                '--fp16',
                '--device', 'cuda:0'
            ], capture_output=True, timeout=3600)
            
            # Read transcript
            txt_file = output_dir / f"{audio_file.stem}.txt"
            if txt_file.exists():
                with open(txt_file) as f:
                    transcript = f.read()
                
                # Extract feed name
                feed_name = audio_file.name.split("-")[0]
                episode_num = audio_file.name.split("-")[1] if len(audio_file.name.split("-")) > 1 else "unknown"
                
                # Create .md file
                md_file = output_dir / f"{feed_name}-{episode_num}.md"
                md_content = f"""# SEBTS — {feed_name.upper()} Episode {episode_num}

**Source:** SEBTS Podcast — {feed_name}  
**Audio File:** {audio_file.name}  
**Transcribed:** {datetime.now().isoformat()}  
**Model:** Whisper {model}  
**Language:** English  

---

{transcript}
"""
                
                with open(md_file, "w") as f:
                    f.write(md_content)
                
                # Save metadata
                metadata = {
                    "source": "SEBTS",
                    "feed": feed_name,
                    "episode": episode_num,
                    "audio_file": audio_file.name,
                    "transcript_file": md_file.name,
                    "words": len(transcript.split()),
                    "model": f"whisper-{model}",
                    "date_transcribed": datetime.now().isoformat()
                }
                
                metadata_file = output_dir / f"{feed_name}-{episode_num}-metadata.json"
                with open(metadata_file, "w") as f:
                    json.dump(metadata, f, indent=2)
                
                print(f"✓ {len(transcript.split())} words")
                
                # Delete .txt (keep .md)
                os.remove(txt_file)
                transcripts[md_file] = transcript
            else:
                print(f"✗ No transcript")
        
        except subprocess.TimeoutExpired:
            print("✗ Timeout (audio too long)")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print(f"\n✅ Transcription complete: {output_dir}")
    print(f"   Total transcripts: {len(transcripts)}")
    return transcripts


# ============================================================================
# PHASE 4: FACULTY DETECTION & ROUTING
# ============================================================================

def detect_and_route(transcripts: Dict[Path, str]) -> Dict[str, List[Path]]:
    """Detect faculty speaker and route transcripts."""
    
    print("\n" + "=" * 80)
    print("PHASE 4: FACULTY DETECTION & ROUTING")
    print("=" * 80)
    
    routing = {
        "sebts-institutional": [],
        "individual": {}
    }
    
    for faculty_name in FACULTY_PATTERNS.keys():
        routing["individual"][faculty_name] = []
    
    for md_file, content in transcripts.items():
        # Always add to institutional
        routing["sebts-institutional"].append(md_file)
        
        # Detect faculty
        detected = None
        content_lower = content.lower()
        
        for faculty_name, patterns in FACULTY_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in content_lower:
                    detected = faculty_name
                    break
            if detected:
                break
        
        # Route to individual
        if detected:
            routing["individual"][detected].append(md_file)
            print(f"  {md_file.name}: {detected}")
        else:
            print(f"  {md_file.name}: Unknown")
    
    # Save routing map
    routing_file = Path.home() / "lora-data" / "sebts-transcriptions" / "routing-map.json"
    with open(routing_file, "w") as f:
        json.dump({
            k: [str(p) for p in v] if isinstance(v, list) else {kk: [str(p) for p in vv] for kk, vv in v.items()}
            for k, v in routing.items()
        }, f, indent=2)
    
    print(f"\n✅ Routing complete")
    print(f"   Institutional: {len(routing['sebts-institutional'])} episodes")
    for faculty, files in routing["individual"].items():
        if files:
            print(f"   {faculty}: {len(files)} episodes")
    
    return routing


# ============================================================================
# PHASE 5: JSONL PREPARATION
# ============================================================================

def prepare_jsonl(routing: Dict[str, List]) -> None:
    """Convert transcripts to JSONL training format."""
    
    print("\n" + "=" * 80)
    print("PHASE 5: JSONL PREPARATION")
    print("=" * 80)
    
    lora_data_dir = Path.home() / "lora-data"
    
    # SEBTS Institutional
    print("\n📝 SEBTS Institutional LoRA...")
    sebts_samples = []
    
    for md_file in routing["sebts-institutional"]:
        md_path = Path(md_file) if isinstance(md_file, str) else md_file
        with open(md_path) as f:
            content = f.read()
        
        lines = content.split("\n")
        body = "\n".join(lines[10:])
        
        words = body.split()
        for i in range(0, len(words), 500):  # ~2k tokens
            chunk = " ".join(words[i:i+500])
            if len(chunk) > 100:
                sebts_samples.append({
                    "text": chunk,
                    "author": "SEBTS Faculty",
                    "source": md_path.stem,
                    "institution": "SEBTS",
                    "date_transcribed": datetime.now().isoformat()
                })
    
    sebts_train = lora_data_dir / "sebts" / "train.jsonl"
    sebts_eval = lora_data_dir / "sebts" / "eval.jsonl"
    sebts_train.parent.mkdir(parents=True, exist_ok=True)
    
    with open(sebts_train, "w") as f:
        for i, sample in enumerate(sebts_samples):
            if i % 20 != 0:  # 95% train
                f.write(json.dumps(sample) + "\n")
    
    with open(sebts_eval, "w") as f:
        for i, sample in enumerate(sebts_samples):
            if i % 20 == 0:  # 5% eval
                f.write(json.dumps(sample) + "\n")
    
    print(f"   Train: {sebts_train} ({sum(1 for line in open(sebts_train))} samples)")
    print(f"   Eval: {sebts_eval} ({sum(1 for line in open(sebts_eval))} samples)")
    
    # Individual Faculty LoRAs
    for faculty_name, files in routing["individual"].items():
        if not files:
            continue
        
        print(f"\n📝 {faculty_name}...")
        faculty_samples = []
        
        for md_file in files:
            md_path = Path(md_file) if isinstance(md_file, str) else md_file
            with open(md_path) as f:
                content = f.read()
            
            lines = content.split("\n")
            body = "\n".join(lines[10:])
            
            words = body.split()
            for i in range(0, len(words), 500):
                chunk = " ".join(words[i:i+500])
                if len(chunk) > 100:
                    faculty_samples.append({
                        "text": chunk,
                        "author": faculty_name,
                        "source": md_path.stem,
                        "institution": "SEBTS",
                        "date_transcribed": datetime.now().isoformat()
                    })
        
        faculty_dir = lora_data_dir / faculty_name.lower().replace(" ", "-")
        faculty_dir.mkdir(parents=True, exist_ok=True)
        
        faculty_train = faculty_dir / "train.jsonl"
        faculty_eval = faculty_dir / "eval.jsonl"
        
        with open(faculty_train, "w") as f:
            for i, sample in enumerate(faculty_samples):
                if i % 20 != 0:
                    f.write(json.dumps(sample) + "\n")
        
        with open(faculty_eval, "w") as f:
            for i, sample in enumerate(faculty_samples):
                if i % 20 == 0:
                    f.write(json.dumps(sample) + "\n")
        
        print(f"   Train: {faculty_train} ({sum(1 for line in open(faculty_train))} samples)")
        print(f"   Eval: {faculty_eval} ({sum(1 for line in open(faculty_eval))} samples)")
    
    print(f"\n✅ JSONL preparation complete")


# ============================================================================
# CLEANUP
# ============================================================================

def cleanup_audio() -> None:
    """Delete audio files after transcription."""
    
    print("\n" + "=" * 80)
    print("CLEANUP")
    print("=" * 80)
    
    audio_queue = Path.home() / "lora-data" / "sebts-audio-queue"
    
    if audio_queue.exists():
        print(f"🗑️  Deleting {audio_queue}...")
        import shutil
        shutil.rmtree(audio_queue)
        print("✓ Deleted")
    
    print(f"\n✅ Cleanup complete")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="SEBTS Podcast Extraction")
    parser.add_argument("--limit", type=int, default=50, help="Limit episodes per feed")
    parser.add_argument("--model", default="medium", help="Whisper model (tiny/base/small/medium/large)")
    parser.add_argument("--no-cleanup", action="store_true", help="Keep audio files")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("SEBTS PODCAST EXTRACTION PIPELINE")
    print("=" * 80)
    
    try:
        # Phase 1: Discovery
        all_episodes = discover_feeds(limit=args.limit)
        
        # Phase 2: Download
        audio_files = download_audio(all_episodes)
        
        if not audio_files:
            print("❌ No audio files downloaded")
            return
        
        # Phase 3: Transcription
        transcripts = transcribe_audio(audio_files, model=args.model)
        
        if not transcripts:
            print("❌ No transcriptions generated")
            return
        
        # Phase 4: Routing
        routing = detect_and_route(transcripts)
        
        # Phase 5: JSONL Preparation
        prepare_jsonl(routing)
        
        # Cleanup
        if not args.no_cleanup:
            cleanup_audio()
        
        print("\n" + "=" * 80)
        print("✅ COMPLETE")
        print("=" * 80)
        print(f"\nOutput locations:")
        print(f"   Transcripts: ~/lora-data/sebts-transcriptions/")
        print(f"   SEBTS Institutional: ~/lora-data/sebts/train.jsonl")
        print(f"   Faculty LoRAs: ~/lora-data/<faculty-name>/train.jsonl")
        print(f"\nReady for training!")
        
    except KeyboardInterrupt:
        print("\n❌ Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
