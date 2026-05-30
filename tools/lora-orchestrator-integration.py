#!/usr/bin/env python3
"""
lora-orchestrator-integration.py — Wire the integrity LoRA into orchestration

This module provides:

1. IntegrityGate — Pre-checks every orchestrator call against integrity rules
2. LoRAAdapter — Wraps model calls through the LoRA when available
3. IntegrityCheckpoint — Logs decision points for audit/verification

Usage in orchestrator:

    from lora_orchestrator_integration import IntegrityGate, LoRAAdapter
    
    # In orchestrate/orchestra/consult:
    integrity_gate = IntegrityGate()
    
    if not integrity_gate.pre_check(user_request):
        return integrity_gate.refusal_reason()
    
    # Wrap model calls through LoRA
    adapter = LoRAAdapter(model="gpt-4o", lora_id="...")
    response = adapter.call(prompt, system_prompt)
    
    # Log for audit
    integrity_gate.checkpoint(decision="approved", reasoning="...")

Architecture:

    User Request
        ↓
    [IntegrityGate.pre_check]  ← Check for red flags (bulk ops, deletions, etc.)
        ↓ (passes)
    [LoRAAdapter.call]  ← Route through LoRA if available
        ↓
    [Orchestrator Logic]  ← Original orchestrate/orchestra/consult
        ↓
    [LoRAAdapter.verify]  ← Check response for integrity violations
        ↓
    [IntegrityCheckpoint.log]  ← Audit trail
        ↓
    Return to User

This ensures every orchestrator call is:
  - Pre-checked (before running)
  - LoRA-influenced (baseline caution)
  - Verified (before returning)
  - Logged (for audit)
"""

import json
import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

WORKSPACE_ROOT = Path("/Volumes/1TB External/openclaw/workspace-main")
LORA_DIR = WORKSPACE_ROOT / "lora"
CHECKPOINT_DIR = WORKSPACE_ROOT / "lora" / "checkpoints"
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

INTEGRITY_RULES = {
    "bulk_edit_threshold": 10,  # Warn if >10 files affected
    "bulk_delete_threshold": 1,  # Always ask before deleting
    "bulk_rename_threshold": 3,  # Warn if renaming >3 symbols
    "data_migration_threshold": 100,  # Always validate before migrating >100 records
}

RED_FLAGS = [
    "just grep-replace",
    "find-and-replace",
    "all files",
    "don't need to read",
    "assume it's correct",
    "skip",
    "without checking",
    "bulk operation",
]

# ─────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────

@dataclass
class IntegrityCheckpoint:
    """Audit trail for one orchestrator call"""
    timestamp: str
    session_id: str
    user_request: str
    pre_check_result: str  # "approved", "conditional", "refused"
    pre_check_reason: str
    lora_influence: Optional[str] = None  # System prompt injected by LoRA
    orchestrator_response: Optional[str] = None
    verify_result: str = "pending"  # "passed", "flagged", "blocked"
    verify_notes: str = ""
    final_action: str = "pending"

# ─────────────────────────────────────────────
# IntegrityGate — Pre-check before orchestration
# ─────────────────────────────────────────────

class IntegrityGate:
    """
    Checks incoming requests for integrity violations before they reach the orchestrator.
    
    Green flags (approve immediately):
    - Small, focused changes
    - Read-before-edit is clear
    - Verification is built-in
    
    Yellow flags (conditional approval):
    - Bulk operations that need assumptions stated
    - Refactoring that should be one logical change
    
    Red flags (refuse, ask user):
    - Delete without asking
    - Bulk operation without verification plan
    - Skip problems to save time
    """
    
    def __init__(self, session_id: str = "unknown"):
        self.session_id = session_id
        self.last_verdict = None
        self.last_reason = None
    
    def pre_check(self, request: str) -> bool:
        """
        Returns True if request passes integrity checks, False otherwise.
        Call refusal_reason() to get the explanation.
        """
        # Scan for red flags
        for flag in RED_FLAGS:
            if flag.lower() in request.lower():
                self.last_verdict = False
                self.last_reason = f"Red flag detected: '{flag}'"
                return False
        
        # Check for bulk operations without verification
        if any(word in request.lower() for word in ["bulk", "all files", "all records"]):
            # Check if verification is mentioned
            if not any(word in request.lower() for word in ["verify", "test", "check", "validate"]):
                self.last_verdict = "conditional"
                self.last_reason = "Bulk operation without explicit verification plan"
                return True  # Conditional (allowed, but flagged)
        
        # Check for deletions without asking
        if "delete" in request.lower() and "ask" not in request.lower():
            self.last_verdict = False
            self.last_reason = "Deletion without confirmation"
            return False
        
        # Default: approved
        self.last_verdict = True
        self.last_reason = "No integrity concerns detected"
        return True
    
    def refusal_reason(self) -> str:
        """Returns the reason for refusing the request"""
        return self.last_reason or "Unknown reason"
    
    def is_conditional(self) -> bool:
        """Returns True if approval is conditional (yellow flag)"""
        return self.last_verdict == "conditional"

# ─────────────────────────────────────────────
# LoRAAdapter — Route through integrity LoRA
# ─────────────────────────────────────────────

class LoRAAdapter:
    """
    Wraps model API calls through the integrity LoRA when available.
    
    If no LoRA is loaded, falls back to standard calls.
    """
    
    def __init__(self, model: str = "gpt-4o", lora_id: Optional[str] = None):
        self.model = model
        self.lora_id = lora_id
        self.lora_available = self._check_lora()
    
    def _check_lora(self) -> bool:
        """Check if LoRA is ready to use"""
        if not self.lora_id:
            return False
        
        # In production, check with OpenAI API:
        # response = openai.models.retrieve(self.lora_id)
        # return response.status == "ready"
        
        # For now, return True if job info exists
        job_info_path = LORA_DIR / "training-data" / "job-info.json"
        if job_info_path.exists():
            with open(job_info_path, 'r') as f:
                job_info = json.load(f)
                return job_info.get("status") in ["succeeded", "ready"]
        
        return False
    
    def call(self, user_prompt: str, system_prompt: str = None) -> str:
        """
        Call the model, optionally through LoRA.
        
        If LoRA is available, injects integrity principles into system prompt.
        """
        
        # Build enhanced system prompt (integrity baseline)
        integrity_system = (
            "You are a careful, disciplined AI assistant. "
            "Every decision is guided by these principles: "
            "1) Read before you edit. "
            "2) Verify before claiming done. "
            "3) One logical change at a time. "
            "4) State assumptions out loud. "
            "5) Check for conflicts before renaming. "
            "6) Refuse unasked improvements. "
            "7) Never skip verification. "
            "8) When unsure, ask. "
        )
        
        if system_prompt:
            final_system = f"{integrity_system}\n\nContext: {system_prompt}"
        else:
            final_system = integrity_system
        
        # In production, route through OpenAI API with LoRA:
        # if self.lora_available:
        #     response = openai.ChatCompletion.create(
        #         model=self.lora_id,  # Use LoRA model ID
        #         messages=[
        #             {"role": "system", "content": final_system},
        #             {"role": "user", "content": user_prompt},
        #         ]
        #     )
        #     return response.choices[0].message.content
        
        # For now, return a placeholder
        return f"[LoRA Response]\n{final_system}\n\nUser request: {user_prompt}"
    
    def verify_response(self, response: str) -> tuple[bool, str]:
        """
        Check response for integrity violations.
        Returns (passed, reason).
        """
        
        # Check for red flags in response
        for flag in RED_FLAGS:
            if flag.lower() in response.lower():
                return False, f"Response contains red flag: '{flag}'"
        
        # Check for required phrases
        required = ["verify", "check", "ask", "test"]
        if not any(word in response.lower() for word in required):
            # Not necessarily a failure, but a concern
            return True, "Response lacks explicit verification language"
        
        return True, "Integrity check passed"

# ─────────────────────────────────────────────
# IntegrityCheckpointer — Audit trail
# ─────────────────────────────────────────────

class IntegrityCheckpointer:
    """
    Logs every orchestrator call for audit and debugging.
    """
    
    def __init__(self, session_id: str = "unknown"):
        self.session_id = session_id
        self.checkpoints = []
    
    def checkpoint(
        self,
        user_request: str,
        pre_check_result: str,
        pre_check_reason: str,
        lora_influence: Optional[str] = None,
        orchestrator_response: Optional[str] = None,
        verify_result: str = "pending",
        verify_notes: str = "",
        final_action: str = "pending",
    ) -> IntegrityCheckpoint:
        """Record one orchestrator call"""
        
        cp = IntegrityCheckpoint(
            timestamp=datetime.now().isoformat(),
            session_id=self.session_id,
            user_request=user_request,
            pre_check_result=pre_check_result,
            pre_check_reason=pre_check_reason,
            lora_influence=lora_influence,
            orchestrator_response=orchestrator_response,
            verify_result=verify_result,
            verify_notes=verify_notes,
            final_action=final_action,
        )
        
        self.checkpoints.append(cp)
        return cp
    
    def save(self, filename: Optional[str] = None) -> Path:
        """Save checkpoint log to disk"""
        
        if not filename:
            filename = f"integrity-checkpoint-{self.session_id}.json"
        
        filepath = CHECKPOINT_DIR / filename
        
        with open(filepath, 'w') as f:
            json.dump(
                [asdict(cp) for cp in self.checkpoints],
                f,
                indent=2,
                default=str
            )
        
        return filepath

# ─────────────────────────────────────────────
# Integration example
# ─────────────────────────────────────────────

def example_workflow(user_request: str, session_id: str = "example") -> tuple[bool, str]:
    """
    Example: How to integrate integrity checks into orchestrator.
    
    Returns (approved, response_or_reason)
    """
    
    # Step 1: Pre-check
    gate = IntegrityGate(session_id=session_id)
    if not gate.pre_check(user_request):
        return False, gate.refusal_reason()
    
    # Step 2: Prepare LoRA
    adapter = LoRAAdapter(model="gpt-4o", lora_id=None)
    lora_system = (
        "You are guided by integrity principles: "
        "read before edit, verify before claiming done, one logical change at a time"
    )
    
    # Step 3: Call orchestrator (simulated)
    response = adapter.call(user_request, system_prompt=lora_system)
    
    # Step 4: Verify response
    passed, verify_reason = adapter.verify_response(response)
    
    # Step 5: Log checkpoint
    checkpointer = IntegrityCheckpointer(session_id=session_id)
    checkpointer.checkpoint(
        user_request=user_request,
        pre_check_result="approved" if gate.pre_check(user_request) else "refused",
        pre_check_reason=gate.refusal_reason(),
        lora_influence=lora_system,
        orchestrator_response=response,
        verify_result="passed" if passed else "flagged",
        verify_notes=verify_reason,
        final_action="approved" if passed else "needs_review",
    )
    
    checkpointer.save()
    
    return passed, response

# ─────────────────────────────────────────────
# Main (test)
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    
    # Test with sample requests
    test_requests = [
        "Find all the typos in this codebase and fix them",  # Red flag
        "I want to rename a variable in 23 files. Read through each file first, list assumptions, and verify.",  # OK
        "Delete all old data without asking",  # Red flag
        "Fix bug #42 and while I'm at it, refactor the whole system",  # Yellow flag
    ]
    
    print("=" * 70)
    print("Integrity LoRA Orchestrator Integration - Test Suite")
    print("=" * 70)
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n[Test {i}] {request[:60]}...")
        passed, result = example_workflow(request, session_id=f"test-{i}")
        print(f"  Result: {'✓ APPROVED' if passed else '✗ FLAGGED'}")
        print(f"  Details: {result[:100]}...")
    
    print("\n" + "=" * 70)
    print("Checkpoints saved to lora/checkpoints/")
    print("=" * 70)
