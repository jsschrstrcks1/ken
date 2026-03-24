"""Google Gemini adapter — Vertex AI first, AI Studio API key fallback."""

import json
import os
import sys
from google import genai
from google.genai import types

MODEL = "gemini-2.0-flash"

# Pricing per 1M tokens (USD) — update as rates change
COST_PER_1M = {"input": 0.10, "output": 0.40}


def _make_client():
    """Build a genai Client. Vertex AI if credentials exist, else API key."""
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    has_creds = (
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        or os.path.exists(os.path.expanduser("~/.config/gcloud/application_default_credentials.json"))
    )

    if project and has_creds:
        print(f"[gemini] Using Vertex AI (project={project}, location={location})", file=sys.stderr)
        return genai.Client(vertexai=True, project=project, location=location)

    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY_PAID", "")
    if key:
        print("[gemini] Using AI Studio (API key)", file=sys.stderr)
        return genai.Client(api_key=key)

    raise RuntimeError("No Gemini credentials: set GOOGLE_CLOUD_PROJECT + service account, or GOOGLE_API_KEY")


def _call(client, prompt, system, max_tokens, temperature):
    """Single generate_content call."""
    return client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
            temperature=temperature,
            response_mime_type="application/json",
        ),
    )


def query(prompt, system="You are a helpful assistant.", max_tokens=4096, temperature=0.7):
    """Send a prompt to Gemini and return structured response with usage metadata."""
    client = _make_client()

    try:
        response = _call(client, prompt, system, max_tokens, temperature)
    except Exception:
        # Fallback: if Vertex AI failed, try API key; if API key failed, try paid key
        paid_key = os.environ.get("GOOGLE_API_KEY_PAID")
        free_key = os.environ.get("GOOGLE_API_KEY")
        fallback_key = paid_key if paid_key and paid_key != free_key else free_key
        if fallback_key:
            print("[gemini] Primary failed, trying API key fallback", file=sys.stderr)
            fallback_client = genai.Client(api_key=fallback_key)
            response = _call(fallback_client, prompt, system, max_tokens, temperature)
        else:
            raise

    # Token counts from usage_metadata
    meta = response.usage_metadata
    input_tokens = getattr(meta, "prompt_token_count", 0) or 0
    output_tokens = getattr(meta, "candidates_token_count", 0) or 0

    input_cost = (input_tokens / 1_000_000) * COST_PER_1M["input"]
    output_cost = (output_tokens / 1_000_000) * COST_PER_1M["output"]

    return {
        "response": _parse_json(response.text),
        "raw": response.text,
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
