#!/usr/bin/env python3
"""
Orchestrator LoRA Integration
Wires /cluster (local Ollama LoRA) alongside existing orchestrator modes.

Usage in orchestrator config:
  modes:
    cluster:
      steps:
        - tool: cluster
          input: "{message}"
          systemPrompt: "{CAREFUL_NOT_CLEVER_PROMPT}"
"""

import subprocess
import json
import sys
from pathlib import Path

# Careful Not Clever system prompt for LoRA
INTEGRITY_SYSTEM_PROMPT = """You are an integrity-focused assistant trained on:
- 732 cross-domain memories (decision patterns, lessons learned)
- 7 sermons on integrity, goodness, and Soli Deo Gloria
- Careful, Not Clever discipline (read before acting, verify before claiming, one change at a time)

Your core rules:
1. [Verified] - grounded facts, widely known, or retrieved
2. [Inference] - reasoned but not guaranteed
3. [Unverified] - uncertain or missing data

Be disciplined:
- Answer only what is asked
- Maintain tone and constraints throughout
- Catch your own contradictions
- Prefer partial truth over confident guesses
- Recognize when you're guessing and interrupt yourself

Your voice is:
- Direct, not flowery
- Thorough before complete
- Humble about limits
- Pastoral when appropriate (you've read Romans sermons)
- Practical and actionable
"""

class OrchestratorClusterIntegration:
    def __init__(self):
        self.cluster_path = Path("/Volumes/1TB External/openclaw/workspace-main/tools/cluster-lora.py")
    
    def call_cluster(self, prompt: str, system_prompt: str = None) -> str:
        """Call /cluster with graceful error handling."""
        cmd = [
            "python3",
            str(self.cluster_path),
            prompt,
        ]
        
        if system_prompt:
            cmd.extend(["--system", system_prompt])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180,
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"[Error from cluster: {result.stderr}]"
        
        except subprocess.TimeoutExpired:
            return "[Cluster request timed out]"
        except Exception as e:
            return f"[Cluster error: {e}]"
    
    def integrate_with_orchestrator(self):
        """Generate orchestrator config snippet for /cluster mode."""
        config = {
            "modes": {
                "cluster": {
                    "description": "Local LoRA on 3-node Ollama cluster with failover",
                    "steps": [
                        {
                            "name": "cluster-call",
                            "tool": "cluster",
                            "input": "{message}",
                            "systemPrompt": INTEGRITY_SYSTEM_PROMPT,
                            "timeout": 180,
                            "fallback": "orchestrate",  # Falls back to multi-model orchestrator if cluster fails
                        }
                    ]
                }
            }
        }
        return config
    
    def get_cluster_status(self) -> dict:
        """Get cluster node status."""
        cmd = ["python3", str(self.cluster_path), "status"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"error": result.stderr}

def main():
    integration = OrchestratorClusterIntegration()
    
    # Show integration config
    config = integration.integrate_with_orchestrator()
    print("🔗 Orchestrator /cluster Integration Config:")
    print(json.dumps(config, indent=2))
    
    # Show cluster status
    print("\n📊 Cluster Status:")
    status = integration.get_cluster_status()
    print(json.dumps(status, indent=2))

if __name__ == "__main__":
    main()
