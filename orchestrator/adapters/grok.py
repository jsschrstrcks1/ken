"""xAI Grok adapter — uses OpenAI-compatible API with cost tracking."""

import json
import os
from openai import OpenAI

MODEL = "grok-3"
BASE_URL = "https://api.x.ai/v1"

# Pricing per 1M tokens (USD) — update as rates change
COST_PER_1M = {"input": 3.00, "output": 15.00}


def query(prompt, system="You are a helpful assistant.", max_tokens=4096, temperature=0.7):
    """Send a prompt to Grok and return structured response with usage metadata."""
    client = OpenAI(
        api_key=os.environ["XAI_API_KEY"],
        base_url=BASE_URL,
    )

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        response_format={"type": "json_object"},
    )

    choice = response.choices[0]
    usage = response.usage

    input_tokens = getattr(usage, "prompt_tokens", 0)
    output_tokens = getattr(usage, "completion_tokens", 0)

    input_cost = (input_tokens / 1_000_000) * COST_PER_1M["input"]
    output_cost = (output_tokens / 1_000_000) * COST_PER_1M["output"]

    return {
        "response": _parse_json(choice.message.content),
        "raw": choice.message.content,
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
