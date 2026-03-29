"""You.com Search adapter — web search results with snippets and sources."""

import json
import os
import urllib.request
import urllib.error
import urllib.parse

SEARCH_URL = "https://ydc-index.io/v1/search"

# Pricing: $5 per 1,000 searches
COST_PER_REQUEST = 0.005


def query(prompt, system="You are a helpful assistant.", max_tokens=4096, temperature=0.7):
    """Send a search query to You.com and return results with sources."""
    api_key = os.environ["YDC_API_KEY"]

    params = urllib.parse.urlencode({"query": prompt})
    url = f"{SEARCH_URL}?{params}"

    req = urllib.request.Request(
        url,
        headers={"X-API-Key": api_key},
        method="GET",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    web_results = data.get("results", {}).get("web", [])

    # Build a readable summary from snippets
    lines = []
    citations = []
    for i, r in enumerate(web_results[:8], 1):
        title = r.get("title", "")
        url = r.get("url", "")
        snippets = r.get("snippets", [])
        snippet_text = " ".join(snippets[:2]) if snippets else r.get("description", "")
        lines.append(f"[{i}] {title}\n{snippet_text}")
        if url:
            citations.append(url)

    content = "\n\n".join(lines)

    result = {
        "response": {"raw_text": content, "result_count": len(web_results)},
        "raw": content,
        "usage": {
            "model": "you.com-search",
            "input_tokens": 0,
            "output_tokens": 0,
            "estimated_cost_usd": COST_PER_REQUEST,
        },
    }

    if citations:
        result["citations"] = citations

    return result
