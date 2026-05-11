---
rule: warn-edit-high-context-surface
enabled: true
trigger: before-edit
severity: warn
match-when:
  - check: file-path
    is: matches-regex
    value: '(schema|schemas|models|contracts|orchestrator/(orchestrate|orchestra|investigate|memory_ops|smart_routing|verify|iteration)\.py|orchestrator/(adapters|modes)/[^/]+\.py|\.claude/(settings|skill-rules)\.json|\.claude/policies/|skills/[^/]+/SKILL\.md|CLAUDE\.md|WORKING-CONTEXT\.md|souls/)'
---

# Fact-forcing gate (concept lift)

About to edit a **high-context surface** — a file whose semantics ripple
outward to many callers, sessions, or repos. Before continuing, verify
you have answers to these three questions:

1. **Who imports / depends on this?**
   - For Python: `grep -r 'from <module>' --include='*.py'`
   - For markdown surfaces (CLAUDE.md, SKILL.md): which sessions / hooks
     consume this?
2. **What is the schema or contract you are about to change?**
   - For JSON / YAML: is the new shape compatible with existing readers?
   - For prose policy (CLAUDE.md, soul docs): is the new wording stronger,
     weaker, or orthogonal to what's there?
3. **What did the user actually ask for?**
   - The edit you're proposing must trace back to a user instruction in
     this session. If it doesn't — pause and ask before changing a file
     this far from where the conversation started.

This is a `warn`, not a `block`. Proceed if you've answered all three.
If you haven't, the careful move is to investigate first, then edit.

---

**Concept origin:** lifted from ECC's `fact-forcing-gate` hook in
`affaan-m/everything-claude-code` (MIT). ECC's version fires before
the *first* Edit/Write/MultiEdit on *any* file — every first edit
trips it. Our narrower scope fires only on high-context surfaces
(schemas, contracts, orchestrator core, harness config, skill defs,
top-level prose docs) to keep the signal/noise ratio livable. The
three-question framing is independent.

**Not a substitute for:** `verification-before-completion` (which
gates *claims of doneness*) or `careful-not-clever` (which gates
*style of edits*). This gate fires earlier — at the moment of edit
attempt — and complements both.
