#!/usr/bin/env python3
"""
Ingest memory dump from Markdown into memory_ops.py store.
Parses the structured dump from /Projects/memories_dump.md.
"""

import re
import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Source file
DUMP_FILE = "/Volumes/1TB External/Projects/memories_dump.md"
MEMORY_OPS = "/Volumes/1TB External/openclaw/workspace-main/tools/memory_ops.py"

def parse_memories_from_dump(filepath):
    """Parse all memories from the dump file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split by domain
    domains = {}
    current_domain = None
    
    # Find domain sections
    domain_pattern = r'^## Domain: `([^`]+)`'
    
    for line in content.split('\n'):
        domain_match = re.match(domain_pattern, line)
        if domain_match:
            current_domain = domain_match.group(1)
            domains[current_domain] = []
            continue
        
        if current_domain:
            # Parse memory headers: ### `<id>` — <type> (conf <conf>)
            header_pattern = r'^### `([a-f0-9]+)` — ([a-z]+) \(conf ([0-9.]+)\)'
            header_match = re.match(header_pattern, line)
            
            if header_match:
                mem_id = header_match.group(1)
                mem_type = header_match.group(2)
                conf = float(header_match.group(3))
                domains[current_domain].append({
                    'id': mem_id,
                    'type': mem_type,
                    'confidence': conf,
                    'domain': current_domain,
                    'raw_line': line
                })
    
    return domains

def encode_memories(domain, memories):
    """Encode memories via memory_ops.py."""
    
    # Read the dump to get full memory content
    with open(DUMP_FILE, 'r') as f:
        dump_content = f.read()
    
    encoded_count = 0
    failed = []
    
    for mem in memories:
        mem_id = mem['id']
        mem_type = mem['type']
        domain_name = mem['domain']
        
        # Find the memory content in the dump
        # Pattern: ### `<id>` ... **Content:** <text>
        pattern = rf"### `{mem_id}`.*?\n\n\*\*Content:\*\* (.+?)(?=\n\n-|$)"
        match = re.search(pattern, dump_content, re.DOTALL)
        
        if not match:
            failed.append((mem_id, "Content not found in dump"))
            continue
        
        content = match.group(1).strip()
        
        # Encode via memory_ops.py
        cmd = [
            "python3",
            MEMORY_OPS,
            "encode",
            domain_name,
            mem_type,
            content
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                encoded_count += 1
            else:
                failed.append((mem_id, result.stderr[:100]))
        except Exception as e:
            failed.append((mem_id, str(e)[:100]))
    
    return encoded_count, failed

def main():
    print("📖 Parsing memory dump...")
    domains = parse_memories_from_dump(DUMP_FILE)
    
    print(f"Found {sum(len(v) for v in domains.values())} memories across {len(domains)} domains")
    for domain, mems in domains.items():
        print(f"  {domain}: {len(mems)} memories")
    
    print("\n📝 Encoding memories...")
    total_encoded = 0
    total_failed = 0
    
    for domain in sorted(domains.keys()):
        print(f"\n  Encoding {domain}...")
        mems = domains[domain]
        encoded, failed = encode_memories(domain, mems)
        
        total_encoded += encoded
        total_failed += len(failed)
        
        print(f"    ✅ {encoded}/{len(mems)} encoded")
        if failed:
            print(f"    ❌ {len(failed)} failed:")
            for mem_id, reason in failed[:5]:
                print(f"       {mem_id}: {reason}")
    
    print(f"\n✅ DONE: {total_encoded} memories encoded, {total_failed} failed")
    
    # Verify
    print("\n📊 Verifying memory store...")
    for domain in sorted(domains.keys()):
        result = subprocess.run(
            ["python3", MEMORY_OPS, "tree", "--domain", domain],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            count = len([l for l in lines if l.startswith('  ')])
            print(f"  {domain}: {count} memories")

if __name__ == "__main__":
    main()
