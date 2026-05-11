---
rule: warn-edit-quality-config
enabled: true
trigger: before-edit
severity: warn
match-when:
  - check: file-path
    is: matches-regex
    value: '(\.eslintrc(\.[a-z]+)?|\.prettierrc(\.[a-z]+)?|tsconfig(\..+)?\.json|pyproject\.toml|setup\.cfg|\.flake8|\.pylintrc|pylintrc|\.editorconfig|jest\.config\.[a-z]+|pytest\.ini|tox\.ini|\.pre-commit-config\.ya?ml|\.github/workflows/[^/]+\.ya?ml|Makefile|ruff\.toml|mypy\.ini)$'
---

# Configuration protection (concept lift)

About to edit a **quality-enforcement configuration file** — linter,
formatter, test runner, type-checker, pre-commit, or CI workflow.

These files define the rules that catch problems in code. **Editing
them changes the rules; it does not fix the code.** Before continuing,
answer this:

> **Am I (a) adding a new rule, or (b) weakening an existing rule
> because some code currently fails it?**

- **(a) Adding a new rule** — proceed. Document the rule's purpose in
  the commit message.
- **(b) Weakening an existing rule** — **stop**. Fix the code instead.
  Loosening a lint rule because a function fails it is how guardrails
  rot. The next person to write similar code gets no warning, and the
  problem propagates.
- **(c) Removing a rule that is genuinely obsolete** — proceed, but
  explain *why* it's obsolete in the commit, not just *that* you
  removed it.

This is a `warn`, not a `block`. Legitimate edits are common
(adding a workflow step, bumping a tool version, configuring a new
plugin). The warning exists to make sure the *kind* of edit is the
one you intended.

---

**Concept origin:** lifted from ECC's `configuration-protection` hook
in `affaan-m/everything-claude-code` (MIT). ECC's version blocks edits
to linter/formatter configs outright; ours warns and asks the
"adding vs weakening" question. The block-vs-warn choice is
deliberate: a hard block on every config edit creates a steady stream
of false positives (legitimate config additions are common), and false
positives erode trust until people start ignoring the warning. Better
to surface the question and let the agent answer in the affirmative
before proceeding.

**Pairs with:** `verification-before-completion` (claim-time check) and
`opensource-sanitizer` Stage 5 (audit of CI/workflow files for risky
permissions). This policy fires at edit time; the others fire later.
