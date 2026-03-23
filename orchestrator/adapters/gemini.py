"""Google Gemini adapter — thin wrapper with cost tracking."""

import json
import os
import google.generativeai as genai

MODEL = "gemini-1.5-pro"

# Pricing per 1M tokens (USD) — update as rates change
COST_PER_1M = {"input": 3.50, "output": 10.50}


def _get_api_key():
    """Return Gemini API key — free tier first, paid tier as fallback."""
    return os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY_PAID", "")


def query(prompt, system="You are a helpful assistant.", max_tokens=4096, temperature=0.7):
    """Send a prompt to Gemini and return structured response with usage metadata."""
    key = _get_api_key()
    genai.configure(api_key=key)

    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=system,
        generation_config=genai.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            response_mime_type="application/json",
        ),
    )

    try:
        response = model.generate_content(prompt)
    except Exception as e:
        # If free tier exhausted (429/quota), try paid tier
        paid_key = os.environ.get("GOOGLE_API_KEY_PAID")
        if paid_key and paid_key != key:
            genai.configure(api_key=paid_key)
            model = genai.GenerativeModel(
                model_name=MODEL,
                system_instruction=system,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                    response_mime_type="application/json",
                ),
            )
            response = model.generate_content(prompt)
        else:
            raise

    # Gemini exposes token counts via usage_metadata
    meta = response.usage_metadata
    input_tokens = getattr(meta, "prompt_token_count", 0)
    output_tokens = getattr(meta, "candidates_token_count", 0)

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
