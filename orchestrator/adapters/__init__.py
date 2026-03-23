"""Multi-LLM adapters. Each module exposes a query() function."""

from . import gpt, gemini, grok

ADAPTERS = {
    "gpt": gpt,
    "gemini": gemini,
    "grok": grok,
}
