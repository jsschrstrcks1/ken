"""Google Gemini adapter — Vertex AI (API key) first, AI Studio SDK fallback.

Rate-limit aware: automatically switches from free-tier to paid-tier
GOOGLE_API_KEY when quota is exhausted (HTTP 429 / quota errors).
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error

from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash"

# Pricing per 1M tokens (USD) — update as rates change
COST_PER_1M = {"input": 0.15, "output": 0.60}

# ── Rate-limit state ────────────────────────────────────────────────

_tier_state = {
    "current_tier": "free",        # "free" or "paid"
    "free_exhausted_at": None,     # timestamp when free tier hit quota
    "free_cooldown_secs": 60,      # wait before retrying free tier
    "consecutive_429s": 0,         # track repeated failures
    "total_requests": 0,
    "total_tier_switches": 0,
}

# Quota error indicators from Google APIs
_QUOTA_SIGNALS = [
    "429",
    "RESOURCE_EXHAUSTED",
    "quota",
    "rate limit",
    "rateLimitExceeded",
    "too many requests",
]


def _is_quota_error(error):
    """Check if an error indicates quota/rate-limit exhaustion."""
    error_str = str(error).lower()
    return any(signal.lower() in error_str for signal in _QUOTA_SIGNALS)


def _get_active_api_key():
    """Return the appropriate API key based on current tier state.

    Logic:
      - If free tier is active and not exhausted → use GOOGLE_API_KEY
      - If free tier was exhausted recently → use GOOGLE_API_KEY_PAID
      - If cooldown has elapsed → try free tier again
    """
    free_key = os.environ.get("GOOGLE_API_KEY", "")
    paid_key = os.environ.get("GOOGLE_API_KEY_PAID", "")

    # If we only have one key, use it regardless of tier state
    if free_key and not paid_key:
        return free_key, "free (only key)"
    if paid_key and not free_key:
        return paid_key, "paid (only key)"
    if not free_key and not paid_key:
        return "", "none"

    # Both keys available — check tier state
    if _tier_state["current_tier"] == "free":
        return free_key, "free"

    # On paid tier — check if cooldown has elapsed to retry free
    if _tier_state["free_exhausted_at"]:
        elapsed = time.time() - _tier_state["free_exhausted_at"]
        if elapsed >= _tier_state["free_cooldown_secs"]:
            _switch_to_free()
            return free_key, "free (cooldown elapsed)"

    return paid_key, "paid"


def _switch_to_paid(reason="quota exhausted"):
    """Switch from free tier to paid tier."""
    _tier_state["current_tier"] = "paid"
    _tier_state["free_exhausted_at"] = time.time()
    _tier_state["total_tier_switches"] += 1
    # Exponential cooldown: 60s, 120s, 240s, max 900s (15 min)
    _tier_state["free_cooldown_secs"] = min(
        60 * (2 ** min(_tier_state["consecutive_429s"], 4)), 900
    )
    print(
        f"[gemini] ⚠ Switched to PAID tier ({reason}). "
        f"Will retry free tier in {_tier_state['free_cooldown_secs']}s. "
        f"Total switches: {_tier_state['total_tier_switches']}",
        file=sys.stderr,
    )


def _switch_to_free():
    """Switch back to free tier after cooldown."""
    _tier_state["current_tier"] = "free"
    _tier_state["consecutive_429s"] = 0
    print("[gemini] ✓ Cooldown elapsed, switching back to free tier", file=sys.stderr)


def get_tier_status():
    """Return current tier state for diagnostics."""
    return {
        "current_tier": _tier_state["current_tier"],
        "total_requests": _tier_state["total_requests"],
        "total_tier_switches": _tier_state["total_tier_switches"],
        "consecutive_429s": _tier_state["consecutive_429s"],
    }


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


def _aistudio_with_fallback(prompt, system, max_tokens, temperature):
    """Call AI Studio with automatic free→paid tier switching on quota errors.

    Retry logic:
      1. Try with current tier's key
      2. On quota error → switch to paid key and retry once
      3. On paid tier quota error → raise (nothing left to try)
    """
    api_key, tier_label = _get_active_api_key()
    if not api_key:
        raise RuntimeError("No Gemini credentials available (set GOOGLE_API_KEY or GOOGLE_API_KEY_PAID)")

    print(f"[gemini] Using AI Studio ({tier_label})", file=sys.stderr)

    try:
        result = _aistudio_sdk(prompt, system, max_tokens, temperature, api_key)
        # Success — reset consecutive 429 counter if on free tier
        if _tier_state["current_tier"] == "free":
            _tier_state["consecutive_429s"] = 0
        return result

    except Exception as e:
        if not _is_quota_error(e):
            raise  # Not a rate-limit issue — propagate

        _tier_state["consecutive_429s"] += 1

        # If we're already on paid tier, nothing to fall back to
        if _tier_state["current_tier"] == "paid" or not os.environ.get("GOOGLE_API_KEY_PAID"):
            raise RuntimeError(
                f"Gemini quota exhausted on {_tier_state['current_tier']} tier "
                f"and no fallback available: {e}"
            )

        # Switch to paid and retry
        _switch_to_paid(reason=str(e)[:80])
        paid_key = os.environ["GOOGLE_API_KEY_PAID"]
        print("[gemini] Retrying with paid tier key...", file=sys.stderr)
        return _aistudio_sdk(prompt, system, max_tokens, temperature, paid_key)


# ── Public API ───────────────────────────────────────────────────────

def query(prompt, system="You are a helpful assistant.", max_tokens=4096, temperature=0.7):
    """Send a prompt to Gemini and return structured response with usage metadata."""

    _tier_state["total_requests"] += 1
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
            if _is_quota_error(e):
                print(f"[gemini] Vertex AI quota hit: {e}", file=sys.stderr)
            else:
                print(f"[gemini] Vertex AI failed: {e}", file=sys.stderr)

    # 2. Fallback: AI Studio SDK with automatic tier switching
    if text is None:
        result = _aistudio_with_fallback(prompt, system, max_tokens, temperature)
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
            "tier": _tier_state["current_tier"],
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
