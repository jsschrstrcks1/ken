#!/usr/bin/env python3
"""
/cluster LoRA Interface
Routes requests through your 3-node Ollama cluster with graceful failover.

Nodes (priority order):
1. m4max (qwen3:32b) — primary, best quality
2. m3pro (qwen3:14b) — secondary, medium quality
3. homeserve (qwen2.5:7b) — tertiary, always available
"""

import json
import sys
import time
import requests
from typing import Optional, Dict, Any
from pathlib import Path

# Cluster configuration
NODES = [
    {
        "name": "m4max",
        "url": "http://100.120.40.114:11434",
        "model": "qwen3:32b",
        "priority": 1,
        "timeout": 120,
    },
    {
        "name": "m3pro",
        "url": "http://kens-macbook-pro.local:11434",
        "model": "qwen3:14b",
        "priority": 2,
        "timeout": 90,
    },
    {
        "name": "homeserve",
        "url": "http://homeserve.local:11434",
        "model": "qwen2.5:7b",
        "priority": 3,
        "timeout": 60,
    },
]

LORA_PATH = "/Volumes/1TB External/Projects/lora/models/integrity-romans-v1.gguf"

class ClusterClient:
    def __init__(self):
        self.nodes = sorted(NODES, key=lambda x: x["priority"])
        self.cache = {}
    
    def health_check(self, node: Dict[str, Any]) -> bool:
        """Check if node is online and responsive."""
        try:
            response = requests.get(
                f"{node['url']}/api/tags",
                timeout=5,
            )
            return response.status_code == 200
        except:
            return False
    
    def get_healthy_node(self) -> Optional[Dict[str, Any]]:
        """Find first healthy node in priority order."""
        for node in self.nodes:
            if self.health_check(node):
                print(f"✅ Using node: {node['name']} ({node['model']})", file=sys.stderr)
                return node
        
        print("❌ No healthy nodes available in cluster", file=sys.stderr)
        return None
    
    def call(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """
        Send request through cluster with failover.
        
        Falls back to next node if current one times out or errors.
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        for attempt, node in enumerate(self.nodes, 1):
            if not self.health_check(node):
                print(f"⏭️  Skipping {node['name']} (offline)", file=sys.stderr)
                continue
            
            try:
                print(f"📤 Sending to {node['name']} ({node['model']})...", file=sys.stderr)
                
                response = requests.post(
                    f"{node['url']}/api/chat",
                    json={
                        "model": node["model"],
                        "messages": messages,
                        "stream": False,
                        **kwargs,
                    },
                    timeout=node["timeout"],
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("message", {}).get("content", "")
                else:
                    print(f"⚠️  {node['name']} error: {response.status_code}", file=sys.stderr)
            
            except requests.exceptions.Timeout:
                print(f"⏱️  {node['name']} timed out, trying next...", file=sys.stderr)
            except Exception as e:
                print(f"❌ {node['name']} error: {e}", file=sys.stderr)
        
        print("❌ All nodes failed", file=sys.stderr)
        return ""
    
    def status(self) -> Dict[str, Any]:
        """Get cluster status."""
        status = {}
        for node in self.nodes:
            health = self.health_check(node)
            status[node["name"]] = {
                "url": node["url"],
                "model": node["model"],
                "online": health,
                "priority": node["priority"],
            }
        return status

def main():
    if len(sys.argv) < 2:
        print("Usage: cluster <prompt> [--system <system_prompt>]")
        sys.exit(1)
    
    prompt = sys.argv[1]
    system_prompt = None
    
    # Parse optional system prompt
    if "--system" in sys.argv:
        idx = sys.argv.index("--system")
        if idx + 1 < len(sys.argv):
            system_prompt = sys.argv[idx + 1]
    
    # Check for status request
    if prompt == "status":
        client = ClusterClient()
        status = client.status()
        print(json.dumps(status, indent=2))
        return
    
    # Make request
    client = ClusterClient()
    response = client.call(prompt, system_prompt=system_prompt)
    print(response)

if __name__ == "__main__":
    main()
