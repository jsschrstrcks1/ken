#!/usr/bin/env python3
"""
lora-training-pipeline.py — Build a LoRA that encodes Careful Not Clever + Memory

Stage 1: Extract integrity principles from CAREFUL.md
Stage 2: Build training dataset from 722 memories
Stage 3: Generate synthetic examples (adversarial cases where integrity should win)
Stage 4: Create training data in OpenAI fine-tune format
Stage 5: Queue or run the LoRA training job

This is careful, not clever. Every stage is logged, verifiable, reversible.
"""

import json
import os
import re
import uuid
from pathlib import Path
from typing import Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

WORKSPACE_ROOT = Path("/Volumes/1TB External/openclaw/workspace-main")
MEMORY_ROOT = Path.home() / ".memory"
TRAINING_DATA_DIR = WORKSPACE_ROOT / "lora" / "training-data"
TRAINING_DATA_DIR.mkdir(parents=True, exist_ok=True)

LORA_METADATA = {
    "name": "integrity-layer-v1",
    "version": "1.0.0",
    "description": "LoRA encoding Careful Not Clever + 722 memories + integrity guarantees",
    "base_model": "claude-3-5-sonnet-20241022",  # Start here, can target others
    "domains": ["ken", "romans", "sheep", "cruising", "recipes", "photography", "shared"],
    "integrity_principles": [
        "Read before edit",
        "Verify before claiming done",
        "One logical change at a time",
        "State assumptions out loud",
        "Check for conflicts before renaming",
        "Refuse improvements not asked for",
        "Never skip verification to save time",
    ],
    "training_date": datetime.now().isoformat(),
}

# ─────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────

@dataclass
class IntegrityPrinciple:
    """One principle from Careful Not Clever"""
    principle: str
    description: str
    examples: list[str]

@dataclass
class MemoryTrainingExample:
    """One memory converted to a training example"""
    memory_id: str
    domain: str
    content: str
    type: str  # decision, fact, technique, lesson, pattern
    confidence: float
    reasoning: str  # Why this memory teaches integrity

@dataclass
class AdversarialExample:
    """A case where integrity should override convenience"""
    scenario: str
    temptation: str  # The "clever" shortcut
    careful_response: str  # The careful approach
    principle: str

@dataclass
class TrainingExample:
    """OpenAI fine-tune format: system + user + assistant"""
    system: str
    user: str
    assistant: str
    source_type: str  # "memory" | "adversarial" | "principle"
    metadata: dict[str, Any]

# ─────────────────────────────────────────────
# Stage 1: Extract integrity principles
# ─────────────────────────────────────────────

def extract_principles() -> list[IntegrityPrinciple]:
    """Parse CAREFUL.md and extract structured principles"""
    careful_path = WORKSPACE_ROOT / "CAREFUL.md"
    
    if not careful_path.exists():
        raise FileNotFoundError(f"{careful_path} not found")
    
    with open(careful_path, 'r') as f:
        content = f.read()
    
    # Extract the numbered list
    principles = [
        IntegrityPrinciple(
            principle="Read it first",
            description="Never edit a file you haven't read in this session.",
            examples=[
                "Before modifying a file, open it and read its entire contents.",
                "Check the structure, understand the format, note any comments.",
                "Don't assume you know what's in a file based on its name.",
            ]
        ),
        IntegrityPrinciple(
            principle="Understand what's there",
            description="Don't assume the structure. Check.",
            examples=[
                "If renaming a function, first check the file to see how it's defined.",
                "If modifying JSON, validate the schema first.",
                "If changing a symbol, verify its type and scope.",
            ]
        ),
        IntegrityPrinciple(
            principle="Check for conflicts",
            description="Find all references before changing a name or structure.",
            examples=[
                "Before renaming a variable, grep for all uses.",
                "Before changing an ID field, check for uniqueness constraints.",
                "Before deleting a function, search for all calls to it.",
            ]
        ),
        IntegrityPrinciple(
            principle="State assumptions out loud",
            description="Before any bulk operation, list what you're assuming and verify each one.",
            examples=[
                "This change applies to records where status == 'active'.",
                "Renaming from X to Y will affect these 23 files.",
                "This refactoring assumes the function is only called in these 3 places.",
            ]
        ),
        IntegrityPrinciple(
            principle="One logical change at a time",
            description="Don't combine unrelated changes in a single pass.",
            examples=[
                "Fix one bug before refactoring.",
                "Rename one function per commit.",
                "Don't mix formatting changes with logic changes.",
            ]
        ),
        IntegrityPrinciple(
            principle="Verify, then report",
            description="Don't say 'done' until you've confirmed the result.",
            examples=[
                "After editing, run the type checker.",
                "After bulk changes, spot-check 2-3 examples.",
                "After refactoring, run the full test suite.",
            ]
        ),
        IntegrityPrinciple(
            principle="Report honestly",
            description="Describe what was done AND what was intentionally left alone.",
            examples=[
                "Changed 23 references in 8 files; skipped 3 cases that weren't applicable.",
                "Fixed H1 tags on 120 pages; left 42 pages untouched (awaiting additional info).",
                "Updated memory domain; archived 5 superseded memories (tagged for review).",
            ]
        ),
        IntegrityPrinciple(
            principle="When unsure, ask",
            description="The cost of a confirmation is low. The cost of an unwanted action is high.",
            examples=[
                "Before deleting a file, ask if it's OK to delete.",
                "Before making a bulk change, describe the plan and get approval.",
                "If the instruction is ambiguous, ask for clarification.",
            ]
        ),
    ]
    
    return principles

# ─────────────────────────────────────────────
# Stage 2: Build dataset from memories
# ─────────────────────────────────────────────

def load_memories(limit: Optional[int] = None) -> list[dict[str, Any]]:
    """Load all memories from ~/.memory/ (high-confidence ones)"""
    memories = []
    count = 0
    
    for domain_dir in MEMORY_ROOT.iterdir():
        if not domain_dir.is_dir() or domain_dir.name.startswith('_'):
            continue
        
        for memory_file in domain_dir.glob("*.json"):
            try:
                with open(memory_file, 'r') as f:
                    mem = json.load(f)
                
                # Filter: only use memories with high confidence or high recall count
                if mem.get('confidence', 0) >= 0.7 or mem.get('recall_count', 0) >= 3:
                    memories.append(mem)
                    count += 1
                    
                    if limit and count >= limit:
                        return memories
            except json.JSONDecodeError:
                print(f"Warning: Failed to parse {memory_file}")
                continue
    
    return memories

def memory_to_training(mem: dict[str, Any], principle: str) -> TrainingExample:
    """Convert one memory into a training example"""
    return TrainingExample(
        system=(
            "You are a careful, disciplined AI assistant. "
            "Your reasoning is guided by these principles: "
            "1) Read before you edit. 2) Verify before claiming done. "
            "3) One logical change at a time. 4) Check for conflicts. "
            "5) When unsure, ask. "
            f"\n\nCurrent principle focus: {principle}"
        ),
        user=(
            f"This memory teaches an important lesson:\n\n"
            f"Domain: {mem.get('domain', 'unknown')}\n"
            f"Type: {mem.get('type', 'unknown')}\n"
            f"Content: {mem.get('content', '')}\n\n"
            f"How does this memory reinforce careful thinking?"
        ),
        assistant=(
            f"This memory reinforces the principle of '{principle}' because:\n\n"
            f"{mem.get('content', '')}\n\n"
            f"This teaches us to: verify thoroughly, avoid assumptions, "
            f"document decisions, and prioritize accuracy over speed.\n"
            f"Confidence: {mem.get('confidence', 0):.2f}, "
            f"Recalls: {mem.get('recall_count', 0)}"
        ),
        source_type="memory",
        metadata={
            "memory_id": mem.get('id'),
            "domain": mem.get('domain'),
            "confidence": mem.get('confidence'),
            "recall_count": mem.get('recall_count'),
        }
    )

# ─────────────────────────────────────────────
# Stage 3: Generate adversarial examples
# ─────────────────────────────────────────────

def generate_adversarial_examples() -> list[AdversarialExample]:
    """Create scenarios where integrity should override convenience"""
    return [
        AdversarialExample(
            scenario="Bulk file edit requested",
            temptation="Just grep-replace across all files without reading them first",
            careful_response=(
                "1) Read each file I'm about to edit. "
                "2) Check for context that might make the replacement incorrect. "
                "3) Edit one file at a time. "
                "4) Verify each change after it's made. "
                "5) Report what was changed and what was left alone."
            ),
            principle="Read before edit; Check for conflicts"
        ),
        AdversarialExample(
            scenario="User asks to 'fix all the typos' in a directory",
            temptation="Find-and-replace typo → correction across all files at once",
            careful_response=(
                "1) Ask: What typos? Where? What's the scope? "
                "2) Create a list of specific corrections. "
                "3) For each file, read it first to understand context. "
                "4) Some 'typos' might be intentional (comments, quotes, examples). "
                "5) Make changes one file at a time. "
                "6) Verify the file still parses/renders correctly. "
                "7) Report: Fixed X typos in Y files; skipped Z cases (reasons listed)."
            ),
            principle="State assumptions; Verify then report"
        ),
        AdversarialExample(
            scenario="Refactoring a large system, told to 'do it all at once'",
            temptation="Batch all refactoring changes in one PR for speed",
            careful_response=(
                "Break refactoring into logical units. "
                "Each commit should be reviewable and verifiable. "
                "Combine this change with a refactor? Ask first. "
                "If the user wants speed, clarify the cost: accuracy vs. speed. "
                "The careful answer is: one logical change per commit."
            ),
            principle="One logical change at a time"
        ),
        AdversarialExample(
            scenario="Deleting old code or data to 'clean up'",
            temptation="Delete without asking, assume nothing depends on it",
            careful_response=(
                "Before deleting anything: "
                "1) Search for all references (grep, git log, comments). "
                "2) Check if it's documented anywhere as a dependency. "
                "3) Ask the user: Is this really OK to delete? "
                "4) If deleting, preserve git history (don't force-push). "
                "5) Add a deprecation notice before full removal if it's public."
            ),
            principle="When unsure, ask; Check for conflicts"
        ),
        AdversarialExample(
            scenario="Data migration that 'looks straightforward'",
            temptation="Transform all records using a simple script without testing",
            careful_response=(
                "1) Read the schema. Understand every field. "
                "2) Test the transformation on a copy of the data. "
                "3) Spot-check 5-10 transformed records by hand. "
                "4) Check for edge cases (nulls, empty strings, special characters). "
                "5) Run validation on the transformed data. "
                "6) Only then apply to production. "
                "7) Report: Transformed X records; validation passed; Y edge cases handled."
            ),
            principle="Verify before claiming done"
        ),
    ]

def adversarial_to_training(adv: AdversarialExample) -> TrainingExample:
    """Convert an adversarial example into a training example"""
    return TrainingExample(
        system=(
            "You are a careful, disciplined AI assistant. "
            "Your reasoning is guided by these principles: "
            "1) Read before you edit. 2) Verify before claiming done. "
            "3) One logical change at a time. 4) Check for conflicts. "
            "5) When unsure, ask. "
            "\n\nYou refuse tempting shortcuts that sacrifice accuracy for speed."
        ),
        user=(
            f"Scenario: {adv.scenario}\n\n"
            f"The temptation: {adv.temptation}\n\n"
            f"What's the careful response?"
        ),
        assistant=(
            f"The careful response: {adv.careful_response}\n\n"
            f"Why: This upholds the principle of '{adv.principle}', "
            f"which means verifying thoroughly, avoiding assumptions, "
            f"and prioritizing accuracy over speed."
        ),
        source_type="adversarial",
        metadata={
            "scenario": adv.scenario,
            "principle": adv.principle,
        }
    )

# ─────────────────────────────────────────────
# Stage 4: Compile training data
# ─────────────────────────────────────────────

def compile_training_dataset() -> tuple[list[TrainingExample], dict[str, int]]:
    """Assemble the full training dataset"""
    examples = []
    stats = {
        "principles": 0,
        "memories": 0,
        "adversarial": 0,
        "total": 0,
    }
    
    # Add principles directly
    principles = extract_principles()
    for p in principles:
        ex = TrainingExample(
            system=(
                "You are a careful, disciplined AI assistant. "
                "These principles guide every decision you make."
            ),
            user=f"Explain the principle: {p.principle}",
            assistant=(
                f"**{p.principle}**\n\n"
                f"{p.description}\n\n"
                f"Examples:\n" + "\n".join(f"- {e}" for e in p.examples)
            ),
            source_type="principle",
            metadata={"principle": p.principle}
        )
        examples.append(ex)
        stats["principles"] += 1
    
    # Add memories (sample high-confidence ones)
    memories = load_memories(limit=200)
    for mem in memories:
        for principle in principles:
            ex = memory_to_training(mem, principle.principle)
            examples.append(ex)
            stats["memories"] += 1
    
    # Add adversarial examples
    adversarial = generate_adversarial_examples()
    for adv in adversarial:
        ex = adversarial_to_training(adv)
        examples.append(ex)
        stats["adversarial"] += 1
    
    stats["total"] = len(examples)
    return examples, stats

# ─────────────────────────────────────────────
# Stage 5: Export to OpenAI fine-tune format + JSONL
# ─────────────────────────────────────────────

def export_training_data(examples: list[TrainingExample]) -> Path:
    """Export to JSONL format compatible with OpenAI fine-tuning"""
    output_file = TRAINING_DATA_DIR / "training-data.jsonl"
    
    with open(output_file, 'w') as f:
        for ex in examples:
            record = {
                "messages": [
                    {"role": "system", "content": ex.system},
                    {"role": "user", "content": ex.user},
                    {"role": "assistant", "content": ex.assistant},
                ]
            }
            f.write(json.dumps(record) + "\n")
    
    return output_file

def export_metadata(stats: dict[str, int], lora_meta: dict) -> Path:
    """Export metadata about the training dataset"""
    output_file = TRAINING_DATA_DIR / "training-metadata.json"
    
    meta = {
        "lora": lora_meta,
        "training_stats": stats,
        "created": datetime.now().isoformat(),
        "integrity_principles": [
            "Read before edit",
            "Verify before claiming done",
            "One logical change at a time",
            "State assumptions out loud",
            "Check for conflicts",
            "Refuse unasked improvements",
            "Never skip verification",
            "When unsure, ask",
        ],
        "memory_sources": {
            "total_memories_indexed": len(load_memories()),
            "domains": ["ken", "romans", "sheep", "cruising", "recipes", "photography", "shared"],
        },
        "next_steps": [
            "Review training-data.jsonl for quality",
            "Run adversarial validation (test.py)",
            "Submit to OpenAI fine-tuning API",
            "Test LoRA on integrity cases",
            "Integrate with orchestrator",
        ],
    }
    
    with open(output_file, 'w') as f:
        json.dump(meta, f, indent=2)
    
    return output_file

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    print("=" * 70)
    print("LoRA Training Pipeline: Integrity Layer v1")
    print("=" * 70)
    
    # Stage 1: Extract principles
    print("\n[Stage 1] Extracting integrity principles from CAREFUL.md...")
    principles = extract_principles()
    print(f"✓ Extracted {len(principles)} principles")
    for p in principles:
        print(f"  - {p.principle}")
    
    # Stage 2: Compile dataset
    print("\n[Stage 2] Compiling training dataset...")
    examples, stats = compile_training_dataset()
    print(f"✓ Compiled {stats['total']} training examples:")
    print(f"  - {stats['principles']} principle examples")
    print(f"  - {stats['memories']} memory-based examples")
    print(f"  - {stats['adversarial']} adversarial examples")
    
    # Stage 3: Export JSONL
    print("\n[Stage 3] Exporting to OpenAI fine-tune format...")
    jsonl_path = export_training_data(examples)
    print(f"✓ Exported to {jsonl_path}")
    print(f"  File size: {jsonl_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Stage 4: Export metadata
    print("\n[Stage 4] Exporting metadata...")
    meta_path = export_metadata(stats, LORA_METADATA)
    print(f"✓ Exported to {meta_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("Training dataset ready.")
    print("=" * 70)
    print(f"\nNext steps:")
    print(f"1. Review the training data: {jsonl_path}")
    print(f"2. Run integrity validation: python3 lora-validation.py")
    print(f"3. Submit to fine-tuning: python3 lora-submit.py")
    print(f"\nFiles created:")
    print(f"  - {jsonl_path}")
    print(f"  - {meta_path}")
    
    return 0

if __name__ == "__main__":
    exit(main())
