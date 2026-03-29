"""Perplexity Sonar adapter — web-grounded answers with cited sources."""

import json
import os
import urllib.request
import urllib.error

RESPONSES_URL = "https://api.perplexity.ai/v1/responses"
PRESET = "fast-search"

# Pricing: ~$0.006 per request (input + output + search)
COST_PER_REQUEST = 0.006


def query(prompt, system="You are a helpful assistant.", max_tokens=4096, temperature=0.7):
    """Send a prompt to Perplexity Responses API and return structured response with citations."""
    api_key = os.environ["PERPLEXITY_API_KEY"]

    # Prepend system context to the prompt
    full_prompt = f"{system}\n\n{prompt}" if system else prompt

    payload = json.dumps({
        "preset": PRESET,
        "input": full_prompt,
        "max_output_tokens": max_tokens,
        "temperature": temperature,
    }).encode("utf-8")

    req = urllib.request.Request(
        RESPONSES_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    # Extract text from output blocks
    content = ""
    citations = []
    for block in data.get("output", []):
        if block.get("type") == "search_results":
            for result in block.get("results", []):
                url = result.get("url", "")
                if url:
                    citations.append(url)
        elif block.get("type") == "message":
            for part in block.get("content", []):
                if part.get("type") == "output_text":
                    content += part.get("text", "")

    # Extract usage/cost from response
    usage_data = data.get("usage", {})
    cost_data = usage_data.get("cost", {})
    input_tokens = usage_data.get("input_tokens", 0)
    output_tokens = usage_data.get("output_tokens", 0)
    total_cost = cost_data.get("total_cost", COST_PER_REQUEST)

    result = {
        "response": _parse_json(content),
        "raw": content,
        "usage": {
            "model": data.get("model", "perplexity"),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": round(total_cost, 4),
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
