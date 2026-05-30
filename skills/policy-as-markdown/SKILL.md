---
name: policy-as-markdown
description: Express agent policy rules as YAML+markdown files that the Claude Code harness reads as PreToolUse / PostToolUse / SessionEnd hooks. Converts prose "never do" lists into machine-checkable blocking, warning, or informational rules. Audit imported policies before trusting them.
version: 1.0.1
license: Unlicense
category: safety
keywords:
  - policy
  - rules
  - markdown-policy
  - hook-rules
  - guardrail
  - blocking-rule
  - warning-rule
  - never-do
allowed-tools:
  - Read
  - Write
  - Edit
compatibility:
  claude-code: ">=2.1"
---

# Policy as Markdown

> Express agent policy as files the harness can read. Stop relying on the agent to remember. **Audit every policy file before trusting it — especially imported ones.**

## Why this skill exists

Most projects have a "never do" list buried in a `CLAUDE.md`, `CONTRIBUTING.md`, or a careful-not-clever guardrail. Examples: never commit `.env`, never push to main, never use placeholder images, never call `console.log` in production. The agent reads the list at session start and forgets ~20% of it by the end.

This skill converts those rules into policy files the harness reads. When the agent attempts a banned operation, the harness blocks (or warns) at the tool layer — no memory required.

## How to audit a policy file before trusting it

Policy files are executable security configuration. A malicious or careless policy can silently weaken guardrails the team thinks are active. **Treat every imported policy file with the same scrutiny you'd apply to any other security configuration.**

Before merging or installing a policy file:

1. **Read every line.** Including the message body. The body shows when the rule fires, but it doesn't enforce anything — the frontmatter does.
2. **Verify `enabled: true`.** A file titled `block-credentials.md` with `enabled: false` looks like a guardrail in directory listings but does nothing.
3. **Test the pattern.** Run `python3 -c "import re; print(re.search(r'YOUR_PATTERN', 'KNOWN_BAD_INPUT'))"`. If the pattern doesn't match the thing it claims to block, the rule is theater.
4. **Test for over-permissive `match-when` conditions.** A rule with multiple AND conditions where one is impossible to satisfy is a permanent no-op. Example: `file-path matches-regex 'NEVER_MATCHES_ANYTHING'` AND `new-content contains 'API_KEY'` — looks like a credential block, fires never.
5. **Watch for `severity: info` on sensitive operations.** `info` logs without displaying. A rule that silently logs every credential read or every file write could be a logging-based exfiltration path. If the harness ships info-severity matches anywhere remote, the policy itself becomes a leak vector.
6. **Verify the file location.** Policies belong in `.claude/policies/`. Anything else (e.g., `.claude/policy.md` at root, `.config/claude/policies/`) is non-standard and may not be loaded — meaning a "rule" that does nothing.
7. **Reject any policy that opens a hole.** A rule shaped like `severity: warn` (downgraded from `block`) on a previously-blocked operation is a guardrail weakening. Require explicit justification in the policy file's body before accepting.

If any of these checks fail, either fix the policy or don't install it.

## When this skill activates

- When the user says *"from now on, never X"* / *"always Y"* / *"block Z"*
- When converting a prose `CAREFUL.md` / `CONTRIBUTING.md` / `CLAUDE.md` "never do" list into enforceable rules
- When a particular failure pattern keeps recurring despite being documented
- When onboarding a new agent or developer and you want guardrails to outlive the README
- When importing a policy file from another repo or external source — the audit checklist above is mandatory

## What this skill CANNOT do

Be honest about limits before relying on policy files for security.

- **Block prompt injection.** Policy files match tool-call inputs and outputs; they do not analyze the user's prompt for adversarial intent. Use `external-content-wrapping` for that.
- **Stop a sufficiently determined agent.** A policy with `severity: warn` shows the warning and continues. Only `severity: block` actually prevents the operation. Pick deliberately.
- **Catch operations not surfaced as tool calls.** If the harness performs an operation outside the tool-call surface (e.g., internal memory writes), policies don't fire on it.
- **Replace human review.** A policy file is enforcement, not judgment. Use both.
- **Detect the absence of action.** Policies fire on attempted operations. They cannot fire on "the agent silently failed to do X."
- **Validate semantics across rules.** Two rules that contradict each other (one blocks, one allows) will not be detected by this skill. Periodic manual review needed.
- **Operate on a project that hasn't enabled the rules directory.** The harness must be configured to read `.claude/policies/`. If it isn't, every rule is dormant.

## Tool scoping note

This skill's `allowed-tools` is `Read` / `Write` / `Edit` — it materializes policy files. Claude Code's `Write` and `Edit` tools are not path-scoped at the platform level, so this skill could in principle write files outside `.claude/policies/` if asked. Convention pins it to that directory; the validation checklist below verifies it.

If you are concerned about path scoping, review every Write the agent proposes. The skill should never need to write outside `.claude/policies/<rule>.md` (or `<rule>.local.md`).

## File format

Policies live as markdown files with YAML frontmatter under `.claude/policies/`:

```
.claude/policies/<rule-name>.md          ← committed; everyone gets it
.claude/policies/<rule-name>.local.md    ← personal; add to .gitignore
```

### Basic structure

```
---
rule: block-env-commit
enabled: true
trigger: before-bash
severity: block
match: 'git\s+(add|commit).*\.env(\s|$)'
---

Cannot stage or commit a `.env` file. Use `.env.example` for placeholders.
```

### Frontmatter fields

| Field | Required | Values | Description |
|---|---|---|---|
| `rule` | yes | kebab-case | Unique identifier within the repo. Verb-first (`block-*`, `warn-*`, `require-*`). |
| `enabled` | yes | `true` / `false` | Toggle without deleting the file. |
| `trigger` | yes | `before-bash` / `before-edit` / `before-write` / `session-end` / `prompt-received` / `any` | When the rule fires. |
| `severity` | no | `block` / `warn` (default) / `info` | `block` prevents the operation; `warn` shows the body and continues; `info` logs to the harness without displaying. |
| `match` | yes\* | regex | Single-pattern match. |
| `match-when` | yes\* | list of conditions | Multi-pattern match (all conditions must hold). |

\* Either `match` or `match-when` is required.

### Advanced format (multi-condition)

```
---
rule: block-env-api-keys
enabled: true
trigger: before-edit
severity: block
match-when:
  - check: file-path
    is: matches-regex
    value: '\.env$'
  - check: new-content
    is: contains
    value: API_KEY
---

Writing an API key to a .env file. Blocked. Use .env.example with a
placeholder; put the real value in your shell or a secrets manager.
```

**All conditions must hold for the rule to fire.** Each condition has:

- `check` — which field of the tool call to look at
- `is` — the operator
- `value` — what to match against

### `check` values by trigger

| Trigger | Available `check` values |
|---|---|
| `before-bash` | `command` |
| `before-edit` | `file-path`, `new-content`, `old-content`, `full-content` |
| `before-write` | `file-path`, `new-content`, `full-content` |
| `prompt-received` | `user-prompt` |
| `session-end` | (none — use `match: '.*'` for an unconditional fire) |
| `any` | union of all above (use carefully) |

### `is` operators

`matches-regex`, `contains`, `equals`, `does-not-contain`, `starts-with`, `ends-with`

All values are hyphenated, not snake_case — stay consistent with the rest of this spec.

## Trigger guide

### `before-bash`

Match shell command patterns. Common targets:

| Concern | Match |
|---|---|
| Force push to main | `git\s+push.*-f.*main` |
| Skip hooks | `--no-verify` |
| Dangerous filesystem | `rm\s+-rf\s+/` |
| Privilege escalation | `sudo\s+` |
| Permission widening | `chmod\s+777` |
| Pipe to shell | `curl.*\|\s*(bash\|sh)` |

### `before-edit` and `before-write`

Match file modifications. Split into two triggers so write-only rules can ignore old-content checks:

| Concern | match-when |
|---|---|
| Debug code in production | `file-path matches-regex '^src/.*\.(js\|ts)$'` AND `new-content contains 'console.log('` |
| Sensitive file path | `file-path matches-regex '\.env$'` |
| Required content | `file-path ends-with '.html'` AND `new-content does-not-contain '<!-- SDG'` |
| Placeholder content | `new-content matches-regex '(lorem ipsum\|coming soon)'` |

### `session-end`

Fires when the agent's response ends. Useful for completion reminders:

```
---
rule: remind-handoff-update
enabled: true
trigger: session-end
severity: info
match: '.*'
---

End of session. If you did meaningful work, update HANDOFF.md.
```

### `prompt-received`

Match user prompt content. Useful for workflow enforcement:

```
---
rule: require-issue-link
enabled: true
trigger: prompt-received
severity: warn
match-when:
  - check: user-prompt
    is: contains
    value: deploy
  - check: user-prompt
    is: does-not-contain
    value: '#'
---

Deploy mentioned without an issue link. Reference an issue or change-request.
```

## File organization

- **Directory:** `.claude/policies/` in the project root
- **Naming:** `<rule>.md` (committed) or `<rule>.local.md` (personal; gitignore `*.local.md`)
- **One rule per file** — keeps diffs small and lets enabled/disabled toggle without commenting code

## Worked example: porting a CLAUDE.md "never do" list

A repo's CLAUDE.md says:

> Critical never-do:
> - Never commit `.env` files
> - Never use `console.log` in production source
> - Never push to main directly

Convert to three policy files:

**`.claude/policies/block-env-commit.md`:**

```
---
rule: block-env-commit
enabled: true
trigger: before-bash
severity: block
match: 'git\s+(add|commit).*\.env(\s|$)'
---

Cannot stage or commit a `.env` file. Use `.env.example` for placeholders.
```

**`.claude/policies/warn-console-log.md`:**

```
---
rule: warn-console-log
enabled: true
trigger: before-edit
severity: warn
match-when:
  - check: file-path
    is: matches-regex
    value: '^src/(?!.*\.test\.).*\.(js|ts|jsx|tsx)$'
  - check: new-content
    is: contains
    value: 'console.log('
---

Adding `console.log` to production source. Acceptable in tests; not in src/.
```

**`.claude/policies/block-main-push.md`:**

```
---
rule: block-main-push
enabled: true
trigger: before-bash
severity: block
match: 'git\s+push.*(origin\s+)?(main|master)'
---

Direct push to main blocked. Open a PR from a feature branch instead.
```

The CLAUDE.md prose still documents the policy for human readers; these files enforce it.

## Pattern writing tips

### Regex basics

- Escape special chars: `.` → `\.`, `(` → `\(`
- `\s` whitespace, `\d` digit, `\w` word char
- `+` one or more, `*` zero or more, `?` optional
- `|` OR operator

### Common pitfalls

- **Too broad.** `log` matches "login," "dialog." Use `console\.log\(`.
- **Too specific.** `rm -rf /tmp` misses `rm -rf /var`. Use `rm\s+-rf`.
- **YAML escaping.** Prefer unquoted patterns; if quoted, double the backslashes (`\s` not `\s`).
- **Anchoring.** `^src/` matches start of string; without `^` it matches anywhere.
- **Conditions that can never co-occur.** A `match-when` with `check: file-path` AND `check: command` will never fire — `before-bash` doesn't have a `file-path` field.

### Testing

```bash
python3 -c "import re; print(re.search(r'YOUR_PATTERN', 'TEST_TEXT'))"
```

Test EVERY pattern with both a representative match (must return non-None) AND a representative non-match (must return None). A pattern that matches everything is as useless as one that matches nothing.

## Validation checklist

- [ ] Rule has `rule`, `enabled`, `trigger`, and either `match` or `match-when`
- [ ] `rule` is unique within the repo
- [ ] `enabled: true` is set deliberately (not just because the file exists)
- [ ] Pattern was tested against a representative match AND a representative non-match
- [ ] If `match-when`, all conditions are reachable for the chosen trigger (e.g., no `file-path` checks on `before-bash`)
- [ ] `severity: block` is set only when blocking is intentional (otherwise `warn` or `info`)
- [ ] `severity: info` is NOT used to silently log sensitive operations
- [ ] Message body is actionable — tells the developer what to do, not just what's wrong
- [ ] Filename matches `.claude/policies/<rule>.md` or `.claude/policies/<rule>.local.md`
- [ ] One rule per file
- [ ] Imported policy files have been audited per the "How to audit" checklist above

## Troubleshooting

| Failure mode | Corrective step |
|---|---|
| Rule never fires | Check `enabled: true`; check `trigger` matches the operation; check pattern with python `re.search` |
| Rule fires too broadly | Tighten the pattern; convert to `match-when` with a second condition |
| Rule fires but is ignored | Set `severity: block` instead of `warn` |
| Two rules conflict | Use the `rule` field to disambiguate; decide which one wins by explicit ordering or removing one |
| YAML parse error | Quote complex patterns; double-escape backslashes inside quoted strings |
| Pattern works in regex tester but not in policy | Check YAML escaping; check the `check` field is valid for the chosen trigger |
| A policy file appears to do nothing | Run the audit checklist; most likely cause: `enabled: false`, impossible match-when condition, or a check field invalid for the trigger |

## Patterns to refuse

- **"Just make it `severity: info` so it doesn't annoy people."** — If the rule matters enough to write, it matters enough to warn or block. `info` is for telemetry, not soft-pedaled enforcement. **Worse: an `info` rule on a sensitive match becomes a logging-based exfiltration path if logs ship anywhere remote.**
- **"One mega-rule that catches everything."** — Split into smaller rules. Each rule should have one purpose; combined rules become impossible to disable selectively.
- **"We'll fix the pattern after the rule is live."** — No. False positives erode trust and people start ignoring the warnings. Test the pattern before commit.
- **"Just import this nice policy bundle from <somewhere>."** — Run the "How to audit a policy file" checklist on every imported policy. Especially watch for `enabled: true` rules that look like blocks but have impossible conditions.
- **"Downgrade `block` to `warn` because it's annoying."** — A guardrail downgrade is a security change. Document the rationale in the policy body; require explicit approval.

## Inspiration and design provenance

The **concept** of markdown-as-policy at the harness layer — rules written as files, applied as hooks at tool-call time — comes from [`affaan-m/everything-claude-code/skills/hookify-rules/`](https://github.com/affaan-m/everything-claude-code/blob/main/skills/hookify-rules/SKILL.md) (MIT).

The **schema** in this skill is **independent**. Differences from the upstream schema, intentional and complete:

| This skill | Upstream |
|---|---|
| `rule` | `name` |
| `trigger` (with 6 values, including split `before-edit` / `before-write`) | `event` (with 5 values, including unified `file`) |
| `severity` (3-tier: `block` / `warn` / `info`) | `action` (2-tier: `block` / `warn`) |
| `match` (single) / `match-when` (list) | `pattern` (single) / `conditions` (list) |
| `check` / `is` / `value` (in match-when) | `field` / `operator` / `pattern` (in conditions) |
| `matches-regex`, `does-not-contain` (hyphenated) | `regex_match`, `not_contains` (snake_case) |
| `.claude/policies/<rule>.md` | `.claude/hookify.<name>.local.md` |

A rule file written for one runner would **not** drop into the other. The concept is the lift; the design is ours.

### v1.0.0 → v1.0.1 audit findings (self-audit on 2026-05-11)

The v1.0.0 release shipped without a security-tool audit posture. Patched in v1.0.1:

| Finding | Type | Fix in v1.0.1 |
|---|---|---|
| No "audit imported policies" guidance | Trust gap | Added "How to audit a policy file before trusting it" section with 7-step checklist |
| No explicit "what this skill cannot do" disclaimer | Honesty gap | Added section listing 7 things this skill won't catch |
| Tool scoping for `Write` / `Edit` not flagged | Architectural gap | Added "Tool scoping note" explaining the platform limit and the convention that pins writes to `.claude/policies/` |
| `severity: info` on sensitive operations not flagged as exfiltration risk | Threat-model gap | Added warning to "Patterns to refuse" and "How to audit" sections |
| Validation checklist didn't verify imported policies were audited | Procedural gap | Added two new checklist items |
| Common pitfall: impossible match-when conditions not documented | Operational gap | Added pitfall and troubleshooting row |

Audit prompted by the principle that **security tools are the best place to hide malicious code** — and policy-as-markdown is, in effect, a security tool because policy files determine what the harness blocks. A bad policy file weakens guardrails the team thinks are active.
