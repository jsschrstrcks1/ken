"""You.com adapter — research endpoint with web-grounded, cited answers."""

import json
import os
import urllib.request
import urllib.error

RESEARCH_URL = "https://api.you.com/v1/research"
RESEARCH_EFFORT = "standard"

# Pricing: ~$6.50 per 1,000 requests
COST_PER_REQUEST = 0.0065

# Cloudflare on api.you.com blocks Python's default User-Agent (error 1010).
_HEADERS_BASE = {
    "Content-Type": "application/json",
    "User-Agent": "orchestrator/1.0",
}


def query(prompt, system="You are a helpful assistant.", max_tokens=4096, temperature=0.7):
    """Send a prompt to You.com Research API and return response with sources."""
    api_key = os.environ["YDC_API_KEY"]

    full_prompt = f"{system}\n\n{prompt}" if system else prompt

    payload = json.dumps({
        "input": full_prompt,
        "research_effort": RESEARCH_EFFORT,
    }).encode("utf-8")

    headers = {**_HEADERS_BASE, "X-API-Key": api_key}

    req = urllib.request.Request(
        RESEARCH_URL,
        data=payload,
        headers=headers,
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    output = data.get("output", {})
    content = output.get("content", "")
    sources = output.get("sources", [])

    citations = [s.get("url", "") for s in sources if s.get("url")]

    result = {
        "response": _parse_json(content),
        "raw": content,
        "usage": {
            "model": "you.com-research",
            "input_tokens": 0,
            "output_tokens": 0,
            "estimated_cost_usd": COST_PER_REQUEST,
        },
    }

    if citations:
        result["citations"] = citations

    return result


def _parse_json(text):
    """Try to parse JSON; return raw text in a wrapper if it fails."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {"raw_text": text}
