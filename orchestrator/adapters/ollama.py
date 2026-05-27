"""Ollama adapter — routes to local Ollama API (http://localhost:11434).

Supports any model installed via `ollama pull` or `ollama create`, including
integrity-baked models like integrity-qwen3 and integrity-coder.

Model aliases (use these in mode YAML or consult CLI):
  ollama              → integrity-qwen3 (default, integrity-baked general)
  ollama:qwen3        → integrity-qwen3
  ollama:coder        → integrity-coder
  ollama:raw-qwen3    → qwen3:8b (no integrity preamble)
  ollama:raw-coder    → qwen2.5-coder:7b (no integrity preamble)
  ollama:<any>        → passes model name directly to Ollama

Usage from CLI:
    python3 consult.py ollama challenge "Review this breeding plan."
    python3 consult.py ollama:coder critique "Review this Python function."
"""

import json
import os
import time
import urllib.request
import urllib.error

OLLAMA_BASE = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# Model alias map — integrity-baked by default
MODEL_ALIASES = {
    "ollama":          "integrity-qwen3",
    "ollama:qwen3":    "integrity-qwen3",
    "ollama:coder":    "integrity-coder",
    "ollama:raw-qwen3": "qwen3:8b",
    "ollama:raw-coder": "qwen2.5-coder:7b",
}

DEFAULT_MODEL = "integrity-qwen3"


def _resolve_model(adapter_name: str) -> str:
    """Resolve adapter name to Ollama model string."""
    if adapter_name in MODEL_ALIASES:
        return MODEL_ALIASES[adapter_name]
    # e.g. "ollama:llama3.2" → "llama3.2"
    if adapter_name.startswith("ollama:"):
        return adapter_name[len("ollama:"):]
    return DEFAULT_MODEL


def query(
    prompt: str,
    system: str = "You are a helpful assistant.",
    max_tokens: int = 4096,
    temperature: float = 0.7,
    model_hint: str = "ollama",
) -> dict:
    """Send a prompt to Ollama and return structured response with usage metadata."""

    model = _resolve_model(model_hint)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_BASE}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise RuntimeError(f"Ollama unreachable at {OLLAMA_BASE}: {e}") from e

    elapsed = time.time() - t0
    content = body.get("message", {}).get("content", "")
    eval_count = body.get("eval_count", 0)
    prompt_eval_count = body.get("prompt_eval_count", 0)

    return {
        "response": _parse_json(content),
        "raw": content,
        "usage": {
            "model": model,
            "input_tokens": prompt_eval_count,
            "output_tokens": eval_count,
            "estimated_cost_usd": 0.0,  # local inference = free
            "elapsed_sec": round(elapsed, 2),
        },
    }


def _parse_json(text: str) -> dict:
    """Try to parse JSON from response; fall back to raw text wrapper."""
    # Strip markdown code fences if present
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        inner = [l for l in lines[1:] if not l.startswith("```")]
        t = "\n".join(inner).strip()
    try:
        return json.loads(t)
    except (json.JSONDecodeError, TypeError):
        return {"raw_text": text}
