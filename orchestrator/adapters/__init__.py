"""Multi-LLM adapters. Each module exposes a query() function."""

import sys

ADAPTERS = {}
ADAPTER_ERRORS = {}


def _try_load(name):
    """Try to import an adapter module. Register it if successful, log why if not."""
    try:
        mod = __import__(f"adapters.{name}", fromlist=[name])
        ADAPTERS[name] = mod
    except ImportError as e:
        ADAPTER_ERRORS[name] = f"SDK not installed: {e}"
    except BaseException as e:
        ADAPTER_ERRORS[name] = f"Load error: {e}"


# Load all adapters — each one that fails gets a clear error message
_try_load("gpt")
_try_load("gemini")
_try_load("grok")
_try_load("youdotcom")
_try_load("perplexity")

# Report on startup (to stderr so it doesn't pollute JSON output)
if ADAPTER_ERRORS:
    for name, err in ADAPTER_ERRORS.items():
        print(f"[adapters] {name}: {err}", file=sys.stderr)

if ADAPTERS:
    print(f"[adapters] Loaded: {', '.join(sorted(ADAPTERS.keys()))}", file=sys.stderr)
else:
    print("[adapters] WARNING: No adapters loaded!", file=sys.stderr)
