"""Multi-LLM adapters. Each module exposes a query() function."""

from . import gpt
# from . import gemini  # disabled — generativelanguage.googleapis.com blocked in this environment
# from . import grok    # disabled temporarily

ADAPTERS = {
    "gpt": gpt,
    # "gemini": gemini,  # re-enable when Vertex AI or network access is available
    # "grok": grok,      # re-enable when ready
}
