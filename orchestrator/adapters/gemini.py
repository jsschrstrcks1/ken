"""Google Gemini adapter — Vertex AI (API key) first, AI Studio SDK fallback."""

import json
import os
import sys
import urllib.request
import urllib.error

from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash"

# Pricing per 1M tokens (USD) — update as rates change
COST_PER_1M = {"input": 0.15, "output": 0.60}


# ── Vertex AI via REST (API key + project) ──────────────────────────

def _vertex_rest(prompt, system, max_tokens, temperature):
    """Call Vertex AI REST API directly with an API key."""
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    key = os.environ["VERTEX_API_KEY"]

    url = (
        f"https://{location}-aiplatform.googleapis.com/v1/"
        f"projects/{project}/locations/{location}/"
        f"publishers/google/models/{MODEL}:generateContent"
    )

    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system}]},
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
            "responseMimeType": "application/json",
        },
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": key,
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


# ── AI Studio via SDK ────────────────────────────────────────────────

def _aistudio_sdk(prompt, system, max_tokens, temperature, api_key):
    """Call AI Studio via the google-genai SDK."""
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
            temperature=temperature,
            response_mime_type="application/json",
        ),
    )
    meta = response.usage_metadata
    return {
        "text": response.text,
        "input_tokens": getattr(meta, "prompt_token_count", 0) or 0,
        "output_tokens": getattr(meta, "candidates_token_count", 0) or 0,
    }


# ── Public API ───────────────────────────────────────────────────────

def query(prompt, system="You are a helpful assistant.", max_tokens=4096, temperature=0.7):
    """Send a prompt to Gemini and return structured response with usage metadata."""

    text = None
    input_tokens = 0
    output_tokens = 0

    # 1. Try Vertex AI REST (API key + project)
    vertex_key = os.environ.get("VERTEX_API_KEY")
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")

    if vertex_key and project:
        try:
            print("[gemini] Using Vertex AI REST", file=sys.stderr)
            raw = _vertex_rest(prompt, system, max_tokens, temperature)
            text = raw["candidates"][0]["content"]["parts"][0]["text"]
            meta = raw.get("usageMetadata", {})
            input_tokens = meta.get("promptTokenCount", 0)
            output_tokens = meta.get("candidatesTokenCount", 0)
        except Exception as e:
            print(f"[gemini] Vertex AI failed: {e}", file=sys.stderr)

    # 2. Fallback: AI Studio SDK
    if text is None:
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY_PAID", "")
        if not api_key:
            raise RuntimeError("No Gemini credentials available")
        print("[gemini] Using AI Studio (API key)", file=sys.stderr)
        result = _aistudio_sdk(prompt, system, max_tokens, temperature, api_key)
        text = result["text"]
        input_tokens = result["input_tokens"]
        output_tokens = result["output_tokens"]

    input_cost = (input_tokens / 1_000_000) * COST_PER_1M["input"]
    output_cost = (output_tokens / 1_000_000) * COST_PER_1M["output"]

    return {
        "response": _parse_json(text),
        "raw": text,
        "usage": {
            "model": MODEL,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": round(input_cost + output_cost, 4),
        },
    }


def _parse_json(text):
    """Try to parse JSON; return raw text in a wrapper if it fails."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {"raw_text": text}
