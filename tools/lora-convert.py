#!/usr/bin/env python3
"""
lora-convert.py — Convert integrity LoRA training data to formats for open models.

The source data is OpenAI JSONL (messages: [{role, content}]).
This tool converts to formats used by:
  - Alpaca (instruction/input/output) — llama.cpp, Ollama fine-tune, LM Studio
  - ShareGPT (conversations) — axolotl, unsloth, FastChat
  - HuggingFace Chat (role/content) — transformers SFTTrainer
  - Plain text (prompt: / response:) — for direct Modelfile injection

Usage:
    python3 tools/lora-convert.py --format alpaca
    python3 tools/lora-convert.py --format sharegpt
    python3 tools/lora-convert.py --format hf
    python3 tools/lora-convert.py --format modelfile   # generates Ollama Modelfile snippet
    python3 tools/lora-convert.py --format all         # generate all formats

Output goes to lora/training-data/<format>/ directory.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE_ROOT = Path(__file__).parent.parent
TRAINING_DATA_DIR = WORKSPACE_ROOT / "lora" / "training-data"
SOURCE_FILE = TRAINING_DATA_DIR / "training-data.jsonl"
INTEGRITY_PROMPT_PATH = (
    Path("/Volumes/1TB External/Projects/ken/orchestrator/INTEGRITY_PROMPT.md")
)


def load_source() -> list[dict]:
    """Load the OpenAI-format JSONL training data."""
    if not SOURCE_FILE.exists():
        print(f"Error: source file not found: {SOURCE_FILE}")
        sys.exit(1)
    examples = []
    with open(SOURCE_FILE) as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                examples.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Warning: skipping malformed line {i+1}: {e}")
    return examples


def extract_turns(example: dict) -> tuple[str, str, str]:
    """Extract (system, user, assistant) from an OpenAI messages example."""
    messages = example.get("messages", [])
    system = ""
    user = ""
    assistant = ""
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "system":
            system = content
        elif role == "user":
            user = content
        elif role == "assistant":
            assistant = content
    return system, user, assistant


def to_alpaca(examples: list[dict]) -> list[dict]:
    """Convert to Alpaca format: {instruction, input, output}.
    
    System + user combined → instruction. No separate input field.
    Used by: llama.cpp fine-tune scripts, LM Studio, many open-source trainers.
    """
    out = []
    for ex in examples:
        system, user, assistant = extract_turns(ex)
        if system:
            instruction = f"{system}\n\n{user}".strip()
        else:
            instruction = user.strip()
        out.append({
            "instruction": instruction,
            "input": "",
            "output": assistant.strip(),
        })
    return out


def to_sharegpt(examples: list[dict]) -> list[dict]:
    """Convert to ShareGPT format: {conversations: [{from, value}]}.
    
    Used by: axolotl, unsloth, FastChat, many HuggingFace trainers.
    System message becomes a 'system' turn at the start.
    """
    out = []
    for ex in examples:
        system, user, assistant = extract_turns(ex)
        conversations = []
        if system:
            conversations.append({"from": "system", "value": system})
        conversations.append({"from": "human", "value": user})
        conversations.append({"from": "gpt", "value": assistant})
        out.append({"conversations": conversations})
    return out


def to_hf_chat(examples: list[dict]) -> list[dict]:
    """Convert to HuggingFace chat format: {messages: [{role, content}]}.
    
    Compatible with transformers SFTTrainer + apply_chat_template.
    Roles: system, user, assistant.
    """
    # This is essentially the same as the source — kept for explicitness
    out = []
    for ex in examples:
        system, user, assistant = extract_turns(ex)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": assistant})
        out.append({"messages": messages})
    return out


def to_modelfile_snippet(examples: list[dict]) -> str:
    """Generate an Ollama Modelfile SYSTEM block from the integrity preamble.
    
    This doesn't include all training examples — Ollama Modelfiles don't support
    that. Instead it produces the SYSTEM prompt + a representative set of
    MESSAGE examples (Ollama supports up to ~20 few-shot messages in Modelfile).
    
    Usage: Append this to any existing Modelfile for a household model.
    """
    # Load integrity preamble
    system_text = ""
    if INTEGRITY_PROMPT_PATH.exists():
        with open(INTEGRITY_PROMPT_PATH) as f:
            raw = f.read()
        lines = raw.splitlines()
        start = next((i for i, l in enumerate(lines) if l.startswith("## The 8 Principles")), None)
        if start is not None:
            block = "\n".join(lines[start:])
            system_text = block.split("---")[0].strip()
    
    if not system_text:
        system_text = (
            "You operate under the Careful Not Clever integrity framework. "
            "Read before acting. Verify before claiming done. One logical change at a time. "
            "Ask before destroying. Label epistemic status. Control scope. "
            "Maintain constraints throughout. Avoid self-contradiction."
        )

    # Pick a diverse sample of examples for few-shot messages (Ollama limit ~20 pairs)
    sample = examples[:10]  # principle examples first
    
    lines = [
        "# Ollama Modelfile — Integrity Baseline",
        "# Append this to any household model's Modelfile.",
        "# Generated: " + datetime.now().strftime("%Y-%m-%d"),
        "",
        'FROM llama3.2  # Change to your target model',
        "",
        "SYSTEM \"\"\"",
        system_text,
        "\"\"\"",
        "",
        "# Few-shot examples that demonstrate the integrity principles in action",
    ]
    
    for ex in sample:
        _, user, assistant = extract_turns(ex)
        if user and assistant:
            # Escape triple-quotes
            user_safe = user.replace('"""', '""\\"')
            asst_safe = assistant.replace('"""', '""\\"')
            lines.append(f'\nMESSAGE user """\n{user_safe}\n"""')
            lines.append(f'\nMESSAGE assistant """\n{asst_safe}\n"""')
    
    lines += [
        "",
        "PARAMETER temperature 0.7",
        "PARAMETER num_ctx 4096",
    ]
    
    return "\n".join(lines)


def write_jsonl(data: list[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")
    print(f"  Wrote {len(data):,} examples → {path}")


def write_json(data: list[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Wrote {len(data):,} examples → {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--format",
        choices=["alpaca", "sharegpt", "hf", "modelfile", "all"],
        default="all",
        help="Output format (default: all)",
    )
    args = parser.parse_args()

    print(f"Loading source data from {SOURCE_FILE}...")
    examples = load_source()
    print(f"  {len(examples):,} examples loaded\n")

    fmt = args.format
    ts = datetime.now().strftime("%Y%m%d")

    if fmt in ("alpaca", "all"):
        print("Converting → Alpaca format (llama.cpp, Ollama, LM Studio)...")
        data = to_alpaca(examples)
        write_json(data, TRAINING_DATA_DIR / "alpaca" / f"integrity-alpaca-{ts}.json")
        write_jsonl(
            [json.loads(json.dumps(d)) for d in data],
            TRAINING_DATA_DIR / "alpaca" / f"integrity-alpaca-{ts}.jsonl",
        )

    if fmt in ("sharegpt", "all"):
        print("\nConverting → ShareGPT format (axolotl, unsloth, FastChat)...")
        data = to_sharegpt(examples)
        write_json(data, TRAINING_DATA_DIR / "sharegpt" / f"integrity-sharegpt-{ts}.json")

    if fmt in ("hf", "all"):
        print("\nConverting → HuggingFace chat format (SFTTrainer)...")
        data = to_hf_chat(examples)
        write_jsonl(data, TRAINING_DATA_DIR / "hf" / f"integrity-hf-{ts}.jsonl")

    if fmt in ("modelfile", "all"):
        print("\nGenerating → Ollama Modelfile snippet...")
        snippet = to_modelfile_snippet(examples)
        out_path = TRAINING_DATA_DIR / "ollama" / f"Modelfile.integrity-{ts}"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(snippet)
        print(f"  Wrote Modelfile snippet → {out_path}")

    print("\n✓ Done.")
    print("\nNext steps:")
    print("  Alpaca:    python3 -m llama_cpp.server --model <model.gguf> --train alpaca/*.jsonl")
    print("  ShareGPT:  axolotl train --config axolotl.yaml (point dataset to sharegpt/*.json)")
    print("  HF:        trainer = SFTTrainer(dataset=load_dataset('json', data_files='hf/*.jsonl'))")
    print("  Ollama:    ollama create <name> -f ollama/Modelfile.integrity-*")


if __name__ == "__main__":
    main()
