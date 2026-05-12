# Continuous-Learning-v2 Doctrine

This is the plain-language statement of the principles the `_assert_*` invariants in `memory_ops.py` enforce in code. Read this when a `CarefulNotCleverError` fires and you want context, or when proposing a change that touches the invariant layer.

The doctrine lives alongside `CONTINUOUS_LEARNING_PLAN.md` (the architecture) and `CONTINUOUS_LEARNING_REVIEWS.md` (the LLM review provenance). It is the human-facing companion to the 9 invariants in `memory_ops.py` (Slice 0).

---

## Seven principles

### 1. Verified work over clever shortcuts (`careful-not-clever`)

When a clustering algorithm could be either "exact TF-IDF replicated from the existing `_build_tfidf`" or "a shiny new library that's faster," pick the replicated one. Mirroring `memory_ops`'s existing patterns is required, not optional. Boring before elegant.

**Anti-example.** A future PR adds `import numpy as np` to `_build_tfidf` "because it's faster." Even if true, it introduces a new dependency, changes the failure surface (numpy install on every consumer machine), and replaces a working pattern with a clever one. Reject; if speed matters, profile the existing code first and optimize in place.

### 2. Safety-guard for autonomous operations (`safety-guard`)

Every mutation entry point must call `_assert_safety_guard_compliant` before destructive operations on shielded targets. An instinct or protected memory cannot be deleted/forgotten/demoted without explicit `force=True`. This is the runtime expression of the household-OS safety-guard skill.

**Anti-example.** A bug in a future slice silently calls `forget(instinct_id)` during cleanup. Without this invariant, the instinct disappears. With it, the operation refuses; the bug surfaces visibly.

### 3. Verification before completion (`verification-before-completion`)

Ship-gate of every slice requires actual verification output in the PR description: tests passing, edge probe re-run, `~/.memory/` byte diff, snapshot evidence. "Looks done, ship it" is not acceptable when the slice touches the defense layer.

**Anti-example.** PR text says "all 82 tests pass" without paste-evidence. Reviewer asks for the actual test runner output. If unavailable, slice doesn't merge.

### 4. Systematic debugging over shallow fixes (`systematic-debugging`)

When an adversarial probe finds a gap, fix the root cause. Don't add a special-case check that papers over the symptom. The 3 rounds of LLM review surfaced 23 threats; each was traced to a structural cause and the fix was structural.

**Anti-example.** Edge probe AM1 found that auto-merge could discard an instinct. The wrong fix would be "if target.is_instinct: skip." The actual fix was shield-aware merge logic (swap keep/discard when shielded) — a structural change. The symptom and the cause aligned.

### 5. Security review for new attack surface (`security-review`)

Any slice that introduces a new disk surface (observation log in 3A, integrity sidecar in 3C) or a new hook (Slice 6) goes through the security-review discipline. Three rounds of red-team review surfaced cryptographic weaknesses (T14 SHA256 length-extension → HMAC-SHA256) and runtime bypass paths (T15 AST-walk dynamic dispatch) that would not have been caught by general code review.

### 6. Simplify clever code at review (`simplify`)

`careful-not-clever` constrains the agent at write-time; `simplify` catches what survives. Final pre-merge review on every slice asks: "could this be 30% shorter with the same correctness?" Often yes; the work that survives is the work that matters.

**Anti-example.** A slice ships a `@dataclass` with 12 fields and a `__post_init__` validator chain. Review notes that all 12 fields are accessed exactly once, never mutated, and could be a plain dict. Reject the dataclass; ship the dict.

### 7. Adversarial review before merge (`requesting-code-review`)

Every slice's ship gate includes an adversarial probe (≥10 cases). Three rounds of LLM review found 23 threats; the same discipline applies per-slice locally. A slice without an adversarial probe is not ready to merge regardless of test count.

---

## Mapping principles to runtime invariants

The 9 `_assert_*` helpers in `memory_ops.py` are the runtime expression of the seven principles. The mapping:

| Principle | Runtime invariant(s) |
|---|---|
| `careful-not-clever` | `_assert_single_id` (no bulk; no shortcut), `_assert_no_silent_skip` (surface, don't drop) |
| `safety-guard` | `_assert_safety_guard_compliant`, `_assert_panic_check` |
| `verification-before-completion` | CI gate `test_every_mutation_path_invokes_invariants` (verifies invariant calls exist) |
| `systematic-debugging` | `_assert_temporal_consistency` (root-cause defense for T12), `_assert_evidence_integrity` (root-cause defense for T2 fabricated evidence) |
| `security-review` | `_assert_evidence_present` (no bare-pattern candidates), `_assert_evidence_integrity` (HMAC, post Slice 3C) |
| `simplify` | (no runtime invariant — process-level) |
| `requesting-code-review` | (no runtime invariant — process-level) |

Two principles (`simplify`, `requesting-code-review`) have no runtime invariant because they govern review process, not runtime behavior. That doesn't make them less important; it means they fail in PR review, not at function call.

---

## The five inviolable principles (cross-slice invariants)

These are locked across every slice and every profile:

1. **`_assert_panic_check` is the first executable statement of every public learning function.** AST-enforced by the CI gate. Override requires explicit allowlist entry visible in PR diff.
2. **No auto-promotion to instinct in `multi-operator-shared` profile.** Single-id explicit `promote_to_instinct` only. In `single-operator-local`, auto-promotion is permitted but only when `_assert_promotion_eligibility` passes (Slice 7.5 invariant; cryptographic consensus).
3. **No always-on Python daemon.** Hooks are harness-driven; extraction is synchronous from an explicit trigger.
4. **Bounded storage.** Observation log has hard cap (10MB or 10,000 lines per session); rotation evicts 10% not whole-file (T10 mitigation).
5. **`~/.memory/` byte-diff empty when feature flag off.** The defense layer ships dark when not in use.

---

## What this doctrine does NOT enforce

Five things it explicitly cannot prevent. Documented so future operators are not surprised:

- **Operator coercion** (T21). In `single-operator-local`, non-applicable. In `multi-operator-shared`, no structural defense — only doctrine and literacy.
- **OS-level privilege escalation** (T19). Household trusts the OS.
- **Side-channel timing on `consolidate()`** (T11). Co-located trusted operators assumed.
- **Supply-chain compromise of Python interpreter itself.** Beyond defense layer's reach.
- **Operator deliberately disabling defenses for legitimate reasons.** The kill-switch flips on `MEMORY_LEARNING_PANIC_DISABLE_ALL`; the operator can flip it off. Doctrine assumes the operator's choices are deliberate.

When a future PR proposes weakening or removing one of the invariants, search this file. If the proposed change is consistent with a principle, document the principle in PR text. If it isn't, the change is a doctrine departure and needs explicit operator approval — the kind documented in `CONTINUOUS_LEARNING_REVIEWS.md`.
