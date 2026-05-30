---
name: opensource-sanitizer
description: Audits a project for secrets, PII, internal references, dangerous files, MCP-config leaks, encoded credentials, Unicode injection patterns, and git-history leaks before any open-source publication. Read-only against source — describes a SANITIZATION_REPORT.md output that the agent's Write tool materializes; the skill itself never edits source files. Hardened May 2026 against current threat landscape (tj-actions, Shai-Hulud, MCPoison, ToxicSkills, Microsoft prompts-as-shells).
version: 1.2.0
license: Unlicense
category: safety
keywords:
  - opensource
  - sanitizer
  - secrets-scan
  - pii-scan
  - publication
  - pre-publish
  - supply-chain
  - audit
  - mcp-config
  - unicode-hygiene
  - trojan-source
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(grep:*)
  - Bash(rg:*)
  - Bash(git log:*)
  - Bash(git show:*)
  - Bash(git rev-list:*)
  - Bash(git diff:*)
  - Bash(git ls-files:*)
  - Bash(git fsck:*)
  - Bash(git reflog:*)
  - Bash(find:*)
  - Bash(base64:*)
  - Bash(xxd:*)
compatibility:
  claude-code: ">=2.1"
---

# Open-Source Sanitizer

> Verify everything independently. Never trust the forker's work. **Audit this skill before trusting it.**

## Why this skill exists

Repositories accumulate secrets, internal references, encoded credentials, and forgotten artifacts as they grow. Most are caught by `.gitignore`. The dangerous ones aren't. This skill is the audit pass before any push to a public surface — first publication, license change, fork-to-public, repo transfer.

This is v1.2.0 — hardened against the credential-leak landscape current as of May 2026. The threat surface has changed since v1.0 (April 2026): AI-lab credentials proliferated (OpenAI `sk-proj-`, Anthropic `sk-ant-oat01-`, MCP server tokens), supply-chain worms now harvest secrets actively (Shai-Hulud v1/v2/v3, Sept 2025–April 2026), and adversaries hide credentials in Unicode and obfuscation channels that simple regex misses (Trojan Source variants, encoded fragments). v1.2 addresses these directly.

## How to audit this skill before trusting it

Security tools are the best place to hide malicious code. Before you run any sanitizer — including this one — verify:

1. **Read every line of `SKILL.md`.** Every line. Including the inspiration section. Look for `<system-reminder>` blocks, instructions to fetch external URLs, suggestions to run destructive commands, regex examples that double as prompt injection.
2. **Verify `allowed-tools`.** Every tool listed should be read-only or scoped to a known-safe write path. If `Bash(*)` appears, that's a wildcard and should be scrutinized. Run `Bash(grep:*)` should permit `grep` only, not `grep $(curl evil.com)` — confirm your harness enforces the prefix scope.
3. **Test against a known-bad fixture.** Before trusting the scan output, drop a fake credential (e.g., a fake AWS key like `AKIAIOSFODNN7EXAMPLE`) into a tracked file and confirm the skill catches it. Repeat for at least three pattern categories. If any fails, the regex coverage is broken — or worse, intentionally narrow.
4. **Test for false positives that cause alert fatigue.** Drop a benign 16-digit number (e.g., a credit card test number `4111111111111111`) into a test fixture. If the skill flags it as CRITICAL, the pattern is too broad — the resulting alert fatigue is a real attack vector. (Grok-identified backdoor pattern: over-matching to desensitize.)
5. **Verify the redaction doesn't leak.** Confirm the report uses `[REDACTED-{type}-{length}]` for short keys (under 40 chars total) and `first2****last2 (length N)` for long keys. **A redaction format that exposes first4 + last4 of a 32-char high-entropy key reveals 25% of the secret — enough to narrow brute-force.** v1.2 strengthened this from v1.1's `first4****last4`.
6. **Verify no "soft" verdict tier exists.** v1.2 has exactly four verdicts: PASS, PASS WITH WARNINGS (low/medium only), PASS WITH ACCEPTED RISK (HIGH/MEDIUM accepted in writing), FAIL. **There is no "low-severity exception for critical findings."** If a future PR adds one, reject it.
7. **Verify the Inspiration section's links are still real.** External links can be retargeted. Open each. If any 404 or redirect to a different domain than the link text claims, treat as a tamper signal.
8. **Verify worked examples don't double as prompt injection.** Read every example in the SKILL.md. If any example contains an imperative instruction Claude could interpret as a real request (e.g., a "remediation step" that begins with `Run this command...`), reject the example.
9. **Reject any "temporary bypass," "whitelist," or "performance skip" flag.** Such flags become permanent. v1.2 has none. If a future PR adds one, reject it.
10. **Verify no external runtime dependency.** This skill calls only the tools in `allowed-tools`. **No `pip install`, no `npm install`, no `curl`-driven validation.** If a future PR adds one, that's an exfiltration channel.

If any of those checks fail, either fix the skill or use a different one.

## When this skill activates

- Before the first push of a new repo to a public remote.
- Before changing a private repo to public.
- Before forking a private repo for open-sourcing.
- Before merging a PR that adds new files to a public repo.
- On the schedule: any repo with public visibility, audited at least once a quarter.
- Before adding new dependencies that pull in significant third-party code.
- After any incident involving credential exposure (audit for related leaks).
- Before publishing or sharing any `.claude/skills/`, `.claude/mcp.json`, `claude_desktop_config.json`, or MCP server configuration.

## Core principle

**Read-only against source.** This skill never edits source files. It describes the format of a `SANITIZATION_REPORT.md`; the agent uses its own `Write` tool to materialize that single file. The skill's `allowed-tools` list is intentionally read-only.

**Don't trust filenames.** A file called `config.yaml` is just as suspect as a file called `.env`. Scan by content, not by name. (Stage 4 below also checks for known-dangerous filenames — that's a separate, complementary check.)

**Don't trust file types.** Credentials in May 2026 are routinely hidden in non-text formats: base64 envelopes for env-var transport, hex strings reconstructed at runtime, image EXIF metadata, sqlite blobs, polyglot files. Stage 7 handles these.

**Audit before you trust.** See the "How to audit this skill" section above. Apply the same scrutiny to any other sanitizer, including ones from well-known vendors.

## What this skill CANNOT do

Be honest about limits before relying on the verdict. This skill **does not** catch:

- **Custom or proprietary secret formats** that don't match the documented patterns. (Bring your own regex via `--extra-patterns`.)
- **Encrypted credentials** at rest (encrypted secrets look like random data; entropy detection alone is too noisy).
- **Dynamically constructed credentials** assembled from fragments at runtime that the AST-fragment detection in Stage 7 misses (e.g., credentials assembled across files, or via `getattr(module, encoded_name)`).
- **Credentials in compiled binaries** (`.pyc`, `.class`, ELF, Mach-O, PE). Run `strings` on suspect binaries first; this skill won't.
- **Credentials transmitted via images via steganography** (LSB manipulation). Stage 7 catches EXIF text metadata; it does not catch steganography.
- **Secrets passed via environment at runtime** that were never committed.
- **Credentials in private repo dependencies** pulled at install time. Stage 7 lints `npm preinstall` for suspicious shapes; it does not analyze every dependency's network behavior.
- **Runtime EDR-class detection** (e.g., a local `trufflehog` binary being invoked from a non-CI context — a known May 2026 attack). Add EDR alerts for that.
- **Novel obfuscation patterns released after this version's date.** This skill has a version date; treat patterns older than 6 months as suspect for coverage gaps.
- **Compromised-package detection beyond the static SBOM list** in Stage 7.5. Maintaining the list is the consumer's responsibility.

When in doubt, **also** run a vendor scanner (TruffleHog, Gitleaks, detect-secrets, GitGuardian) for second-opinion coverage. Don't trust a single scanner. The user's organization can also run GitHub's native secret scanning (push protection) as a third layer.

## Tool scoping caveat

The `allowed-tools` list scopes by command prefix, not by argument shape. `Bash(grep:*)` permits `grep <anything>`. If `<anything>` includes shell metacharacters (e.g., `grep -e "$(curl evil.com)"`), the scope is wider than it appears. This is a Claude Code platform constraint, not specific to this skill.

**Mitigation:** review each Bash invocation the agent proposes. If a `grep`, `git`, or `find` invocation includes:

- Command substitution (`$(...)`, backticks)
- Output redirection to a non-`/tmp` path (`> /etc/...`, `> ~/.ssh/...`)
- `-exec`, `--exec`, `-delete` flags on `find`
- A pipe to `bash`, `sh`, `eval`, or `xargs ... bash`

…reject the invocation. The scan does not legitimately need any of these.

## May 2026 threat context

Pattern selection in v1.2.0 was anchored to specific public incidents and disclosures between March 2025 and May 2026. The skill is designed to catch the credential-shape classes that appeared in these events. If you're auditing a repo for any of these threat models, this skill's coverage is calibrated against:

| Date | Incident / disclosure | Pattern class added |
|---|---|---|
| 2025-03-18 | GitHub: fine-grained PATs GA (366-day cap lifted) | `github_pat_` long-lived |
| 2025-03-14 | CVE-2025-30066 tj-actions/changed-files (>23k repos, double-base64 secret dump in Actions logs) | GH Actions workflow lint; base64 decode-then-rescan |
| 2025-07-18 | eslint-config-prettier hijack (npnjs.com phish) | lookalike-domain check |
| 2025-07-29 | CVE-2025-54136 Cursor MCPoison; CVE-2025-54135 CurXecute | MCP-config scanning |
| 2025-09-15 | Shai-Hulud worm v1 (~200 npm pkgs) — used trufflehog offensively | SBOM blocklist; npm preinstall audit |
| 2025-11-24 | Shai-Hulud 2.0 (796 pkgs, hit Zapier/Postman/PostHog) | SBOM blocklist |
| 2026-01 | CVE-2025-68143/68144/68145 Anthropic Git MCP server prompt-injection | external-content scrutiny in workflow |
| 2026-02 | Snyk ToxicSkills: 36% of ClawHub skills had prompt injection | SKILL.md / README static lint |
| 2026-03-10 | GitHub secret scanning: 28 new detectors, 39 push-protected | pattern roster sync |
| 2026-04 | MCP architectural class CVEs (7,000+ exposed servers, 150M+ DL) | MCP config + path scanning |
| 2026-04-14 | GitGuardian: 24,008 unique secrets leaked through MCP configs in 2025 | MCP config scanning is mandatory |
| 2026-04-22 / 04-29 | Shai-Hulud "Third Coming" + Mini variant | SBOM list maintained externally |
| 2026-05-07 | Microsoft "prompts-as-shells" RCE in AI agent frameworks | external-content fence (paired skill) |

Sources are listed in the Inspiration section.

## The seven-stage scan (six original + one expanded)

### 1. Secrets detection

Scan all tracked files for credential-shaped strings. Patterns are organized by provider so coverage gaps are visible.

#### Cloud providers

| Provider | Pattern | Notes |
|---|---|---|
| AWS long-term access key ID | `AKIA[0-9A-Z]{16}` | standard |
| AWS STS / IAM Identity Center (temporary) | `ASIA[0-9A-Z]{16}` | **new in v1.2** — pairs with session token entropy |
| AWS secret access key (quoted form) | `(?i)aws.{0,20}['"][0-9a-zA-Z/+]{40}['"]` | |
| GCP service account JSON (raw) | regex match on `"type":\s*"service_account"` AND `"private_key":` co-occurring within 2KB | |
| GCP service account (base64-wrapped for env transport) | base64-decode any string ≥200 chars starting with `eyJ` or matching `^[A-Za-z0-9+/]{300,}={0,2}$`; then re-match for `service_account` | **new in v1.2** |
| Azure storage connection string | `DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[A-Za-z0-9+/=]{88}` | |

#### AI / LLM providers

| Provider | Pattern | Notes |
|---|---|---|
| OpenAI legacy | `sk-(?![Aa]nt\|proj\|svcacct\|None)[A-Za-z0-9]{48}(?![A-Za-z0-9])` | negative-lookahead to avoid double-match |
| OpenAI project key | `sk-proj-[A-Za-z0-9_-]{40,200}` | **v1.2 widened from 40+ to 40–200** |
| OpenAI service account | `sk-svcacct-[A-Za-z0-9_-]{40,200}` | |
| OpenAI None-prefixed | `sk-None-[A-Za-z0-9]{20,}` | **new in v1.2** |
| Anthropic API | `sk-ant-api[0-9]{2}-[A-Za-z0-9_-]{48,}` | **v1.2 broadened version digits** |
| Anthropic Admin | `sk-ant-admin[0-9]{2}-[A-Za-z0-9_-]{40,}` | |
| Anthropic OAuth | `sk-ant-oat[0-9]{2}-[A-Za-z0-9_-]{40,}` | **new in v1.2** |
| Google API | `AIza[0-9A-Za-z_-]{35}` | |
| Hugging Face | `hf_[A-Za-z0-9]{34,40}` | **new in v1.2** |
| DeepSeek | `(?i)deepseek.{0,40}['"](sk-)?[A-Za-z0-9]{40,}['"]` | **new in v1.2** — contextual |

#### Source-control / package registries

| Provider | Pattern | Notes |
|---|---|---|
| GitHub PAT (classic) | `ghp_[A-Za-z0-9]{36,251}` | |
| GitHub fine-grained PAT | `github_pat_[A-Za-z0-9_]{82,}` | |
| GitHub OAuth | `gho_[A-Za-z0-9]{36,255}` | |
| GitHub app (server) | `ghs_[A-Za-z0-9]{36,255}` | |
| GitHub app (user-to-server) | `ghu_[A-Za-z0-9]{36,255}` | |
| GitHub refresh | `ghr_[A-Za-z0-9]{36,255}` | **new in v1.2** |
| GitLab PAT | `glpat-[A-Za-z0-9_-]{20,}` | |
| npm token | `npm_[A-Za-z0-9]{36}` | |
| PyPI token | `pypi-AgEIcHlwaS5vcmc[A-Za-z0-9_-]+` | |

#### Payment / messaging / mail

| Provider | Pattern | Notes |
|---|---|---|
| Stripe live/test (secret) | `sk_(test\|live)_[0-9a-zA-Z]{24,}` | |
| Stripe restricted | `rk_(test\|live)_[0-9a-zA-Z]{24,}` | **new in v1.2** |
| Stripe publishable (still sensitive) | `pk_(test\|live)_[0-9a-zA-Z]{24,}` | |
| Stripe webhook secret | `whsec_[A-Za-z0-9+/=]{32,64}` | |
| Twilio account SID | `AC[a-f0-9]{32}` | |
| Twilio API key SID | `SK[a-f0-9]{32}` | |
| SendGrid | `SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}` | |
| Mailgun | `key-[a-f0-9]{32}` | |
| Slack bot/user/app/refresh/external | `xox[baprseh]-[0-9]{10,13}-[0-9A-Za-z-]{20,}` | **v1.2 broadened token-type chars** |
| Slack webhook | `(?i)https://hooks\.slack\.com/services/[A-Za-z0-9/]+` | case-insensitive |
| Discord bot token | `[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}` | |

#### Infrastructure

| Provider | Pattern | Notes |
|---|---|---|
| DigitalOcean | `dop_v1_[a-f0-9]{64}` | |
| Cloudflare API token | `[A-Za-z0-9_-]{40}` only when within 30 chars of `cloudflare` keyword | contextual to reduce false positives |
| Heroku API key (UUID) | UUID format only when within 30 chars of `heroku` keyword | contextual |

#### Generic

| Pattern type | Pattern | Notes |
|---|---|---|
| Private key header | `-----BEGIN .+ PRIVATE KEY-----` | |
| JWT (often a secret; may be a fixture) | `eyJ[A-Za-z0-9_=-]+\.eyJ[A-Za-z0-9_=-]+\.[A-Za-z0-9_=-]+` | flag with context — many JWTs are public fixtures |
| Generic env-style assignment (any case) | `(?i)[A-Z_][A-Z0-9_]*(API_KEY\|SECRET\|TOKEN\|PASSWORD\|PASSWD\|ACCESS_KEY\|PRIV(ATE)?_KEY)\s*[:=]\s*['"][^'"\s]{12,}['"]` | minimum 12 chars to reduce noise |
| DB URL with credentials | `(?i)(postgres\|postgresql\|mysql\|mariadb\|mongodb\|redis\|mssql\|oracle\|couchdb)://[^:\s]+:[^@\s]+@` | |

Report: file path, line number, **redacted** match (see redaction rule below), severity **CRITICAL**.

**Redaction rule (mandatory, strengthened in v1.2):**

| Match length | Redaction format | Rationale |
|---|---|---|
| 1–15 chars | `[REDACTED-{type}-len{N}]` | Never expose any characters of short secrets — too brute-forceable |
| 16–39 chars | `[REDACTED-{type}-len{N}]` | Same — even 8 exposed chars narrows brute-force on 32-char secrets to feasibility |
| 40+ chars | `{first2}****{last2} (len {N})` | Long keys can afford 4 chars without enabling brute-force |
| Always: private keys | `[REDACTED-PRIVATE-KEY]` | Never any chars |
| Always: JWTs | redact each segment separately; format `eyJ...****....****...` with length per segment | |

v1.1 used `first4****last4` for all matches. **That was wrong for short high-entropy keys** — a 32-char API key with 8 chars exposed has 24 chars unknown = 24 × log2(62) ≈ 143 bits of entropy hidden, which sounds safe but if the key prefix narrows the alphabet, brute-force becomes feasible against known endpoints. v1.2's full-redaction-for-short-keys closes this.

### 2. PII scan

Patterns:

| Concern | Regex | Notes |
|---|---|---|
| Personal email (excluding `example.com`, `noreply.*`, `*.test`, `localhost`, `local`) | `[a-zA-Z0-9._%+-]+@(?!example\.com\|noreply\.\|.+\.test\|localhost)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` | |
| US phone | `\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}` | |
| International phone (E.164) | `\+\d{1,3}[-.\s]?\d{4,14}` | |
| SSN (dashed) | `\d{3}-\d{2}-\d{4}` | |
| SSN (spaced) | `\d{3}\s\d{2}\s\d{4}` | |
| Non-RFC1918 IPv4 (excluding `127.`, `0.`, `255.255.255.255`) | `(?!10\.\|127\.\|0\.\|255\.255\.255\.255)(?!192\.168\.)(?!172\.(1[6-9]\|2[0-9]\|3[01])\.)((25[0-5]\|2[0-4][0-9]\|[01]?[0-9][0-9]?)\.){3}(25[0-5]\|2[0-4][0-9]\|[01]?[0-9][0-9]?)` | |

Report: file path, line number, **redacted** match (same redaction rule as Stage 1), severity **HIGH** for SSN / international phone in production code; **MEDIUM** for personal email or US phone.

### 3. Internal references

| Concern | Regex |
|---|---|
| Home dir paths | `/(home\|Users)/[a-z][a-z0-9_-]+` |
| Windows user paths | `C:\Users\[A-Za-z][A-Za-z0-9_-]+` |
| RFC1918 IPs | `(10\.\|172\.(1[6-9]\|2[0-9]\|3[01])\.\|192\.168\.)((25[0-5]\|2[0-4][0-9]\|[01]?[0-9][0-9]?)\.?){2}` |
| Internal hostnames | `\w+\.(local\|lan\|internal\|corp\|home)(?![a-z])` |
| `.ssh/` paths | `~/.ssh\|\.ssh/(id_\|known_hosts\|config)` |
| Cloud metadata | `169\.254\.169\.254` (AWS) or `metadata\.google\.internal` (GCP) |
| Personal social handles | manual review (regex too noisy) |

Report: file path, line number, severity **LOW** (unless the value is in a secret-like context, in which case escalate to **MEDIUM**).

### 4. Dangerous files

Confirm absence of:

#### Credential files (CRITICAL if present)
- `.env`, `.env.local`, `.env.production`, `.env.development`, `.env.staging`, `.envrc` (direnv)
- `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.jks`
- `id_rsa`, `id_dsa`, `id_ecdsa`, `id_ed25519` (and `.pub` for completeness)
- `*.kdbx`, `*.kdb` (KeePass)
- `.aws/credentials`, `.aws/config`
- `.gnupg/*`, `.ssh/known_hosts`
- `.npmrc` containing `_authToken=`
- `.pypirc` containing `password =`
- `.netrc`
- `.config/gh/*`, `.config/hub`
- `.terraformrc` containing `credentials`, `*.tfvars` (often contains secrets)
- `.kube/config`, `.docker/config.json`
- `secrets.yaml`, `secrets.json`, `secrets.env`, `*.secret*`
- `*.sops.yaml` (sops files — encrypted but signal a secret-management tool in use)
- `*.age` (age-encrypted, same)
- `ansible-vault*` (often misconfigured)

#### MCP config files (CRITICAL if leaking — new in v1.2)
GitGuardian: **24,008 unique secrets leaked through MCP configs in 2025.**
- `.cursor/mcp.json`
- `claude_desktop_config.json` (any path)
- `.vscode/mcp.json`
- `.config/Claude/claude_desktop_config.json`
- `~/.config/claude*/`
- `mcp.json` at any depth
- `mcp_servers.json`, `mcp_config.json`

For each MCP config found: scan its contents for env-var values that look like secrets (env-style assignments, base64 envelopes ≥40 chars, JWTs). MCP configs are particularly dangerous because they're text-readable and travel with developer dotfiles.

#### Build / cache files (LOW if present)
- `build/`, `dist/`, `out/`, `target/`, `.next/cache/`, `.nuxt/`, `coverage/`
- `node_modules/.cache/`, `.pytest_cache/`, `.tox/`, `__pycache__/`
- `*.sqlite`, `*.db`, `*.sqlite3` — flag for manual review; SQLite blobs can contain anything

#### Housekeeping (LOW if present)
- `.DS_Store`, `Thumbs.db`, `desktop.ini`

Report: which files are present, with severity per category above.

### 5. `.env.example` completeness

If `.env.example` exists, verify every variable referenced in source is documented. The check must be language-agnostic and cover all source directories:

```
# Find all source directories (exclude docs/test/vendor)
src_files="$(git ls-files | grep -v -E '^(docs/|test/|tests/|spec/|fixtures/|node_modules/|vendor/|\.git/)')"

# Patterns by language
ref_patterns='process\.env\.([A-Z_][A-Z0-9_]*)
process\.env\[['"]([A-Z_][A-Z0-9_]*)['"]\]
os\.environ\[['"]([A-Z_][A-Z0-9_]*)['"]\]
os\.environ\.get\(['"]([A-Z_][A-Z0-9_]*)['"]
os\.getenv\(['"]([A-Z_][A-Z0-9_]*)['"]
ENV\[['"]([A-Z_][A-Z0-9_]*)['"]\]
System\.getenv\(['"]([A-Z_][A-Z0-9_]*)['"]
env::var\(['"]([A-Z_][A-Z0-9_]*)['"]
getenv\(['"]([A-Z_][A-Z0-9_]*)['"]
\$\{?([A-Z_][A-Z0-9_]*)(?::-)?\}?'

referenced="$(echo "$src_files" | xargs -d'
' rg --no-heading --no-line-number -o "$ref_patterns" | extract_capture | sort -u)"
documented="$(grep -E '^[A-Z_][A-Z0-9_]*=' .env.example | sed 's/=.*//' | sort -u)"

missing="$(comm -23 <(echo "$referenced") <(echo "$documented"))"
clutter="$(comm -13 <(echo "$referenced") <(echo "$documented"))"
```

Report: variables referenced but undocumented (severity **MEDIUM**). Also report unused vars in `.env.example` as **LOW** (clutter).

**Also flag:** `os.getenv("X", "hardcoded_default_with_secret_shape")` — a default that looks like a credential is the credential, not just a fallback.

### 6. Git history review

Walk full history with pattern matching, not just specific extensions. Plus walk **unreachable** objects, **reflog**, and **`.gitattributes` filters** (new in v1.2):

```bash
# All current secret patterns aggregated
secret_patterns='AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|gh[psour]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{82,}|sk-(proj|svcacct|None)-[A-Za-z0-9_-]+|sk-ant-(api|admin|oat)[0-9]{2}-[A-Za-z0-9_-]+|sk_(test|live)_[0-9a-zA-Z]{24,}|rk_(test|live)_[0-9a-zA-Z]{24,}|whsec_[A-Za-z0-9+/=]{32,}|AIza[0-9A-Za-z_-]{35}|hf_[A-Za-z0-9]{34,}|npm_[A-Za-z0-9]{36}|pypi-AgEIcHlwaS5vcmc[A-Za-z0-9_-]+|dop_v1_[a-f0-9]{64}|glpat-[A-Za-z0-9_-]{20,}|xox[baprseh]-[0-9]{10,13}-[0-9A-Za-z-]{20,}|-----BEGIN .+ PRIVATE KEY-----'

# (a) Walk reachable history
git log --all --full-history -p | rg -E "$secret_patterns" --color=never

# (b) Walk UNREACHABLE objects (new in v1.2)
# Force-pushed branches, orphan refs, and deleted branches retain blobs for 90 days
git fsck --unreachable --no-reflogs 2>/dev/null | grep blob | awk '{print $3}' | \
  while read sha; do
    content="$(git show "$sha" 2>/dev/null)"
    echo "$content" | rg -E "$secret_patterns" --color=never -l
  done

# (c) Walk reflog
git reflog show --all | awk '{print $1}' | sort -u | \
  while read sha; do
    git show "$sha" 2>/dev/null | rg -E "$secret_patterns" --color=never -l
  done

# (d) Audit .gitattributes for filter= clean/smudge directives (new in v1.2)
# A custom filter is a persistence vector for hidden code execution
for f in .gitattributes .git/info/attributes; do
  [ -f "$f" ] && grep -E '(filter|diff|merge)\s*=\s*\S' "$f"
done

# (e) Large-repo fallback: limit to date-bounded
since="$(date -d '2 years ago' +%Y-%m-%d)"
git log --all --full-history --since="$since" -p | rg -E "$secret_patterns" --color=never
```

For each match: severity **CRITICAL**. The credential is permanently in history and may have been compromised. **Rotation required.** History rewrite (e.g., `git filter-repo`) is a separate operation; this scanner does not perform it.

**For `.gitattributes` filter findings:** severity **HIGH**. A custom clean/smudge filter is a credential-injection or code-execution channel; even if currently benign, the maintenance burden is real.

### 7. Modern threat surface (new in v1.2)

This stage is the v1.2 expansion. Each sub-stage addresses a specific class of credential exposure that the original 6 stages missed.

#### 7.1 Decode-then-rescan

Run all Stage 1 patterns against base64- and hex-decoded forms of long strings. tj-actions exposed secrets as double-base64 in CI logs; many CI configs base64-wrap service account JSONs for env-var transport.

```bash
# Find candidate base64 strings (≥40 chars, base64 alphabet, no spaces)
candidates="$(rg --no-heading --no-line-number -oE '[A-Za-z0-9+/]{40,}={0,2}')"

# Decode and re-scan
echo "$candidates" | while read s; do
  decoded="$(echo "$s" | base64 -d 2>/dev/null)" || continue
  echo "$decoded" | rg -E "$secret_patterns" && \
    echo "BASE64-WRAPPED LEAK at: $s"
done

# Same for hex
rg --no-heading --no-line-number -oE '[0-9a-fA-F]{64,}' | while read s; do
  decoded="$(echo "$s" | xxd -r -p 2>/dev/null)" || continue
  echo "$decoded" | rg -E "$secret_patterns"
done
```

For each match: severity **CRITICAL** (the credential is in the repo; the encoding is just camouflage).

#### 7.2 Unicode hygiene (Trojan Source defense — CVE-2021-42694 family)

Reject source files containing:

- **Bidi controls**: U+202A, U+202B, U+202C, U+202D, U+202E, U+2066, U+2067, U+2068, U+2069
- **Zero-width characters**: U+200B (ZWSP), U+200C (ZWNJ), U+200D (ZWJ), U+2060 (WJ), U+FEFF (BOM in middle of file)
- **Confusables**: any mixed-script identifier per Unicode TR39 (e.g., Cyrillic `а` masquerading as Latin `a`)

```bash
# Bidi + zero-width detector
for f in $(git ls-files); do
  if [ -f "$f" ] && file "$f" | grep -q text; then
    # PCRE for the Unicode codepoint ranges
    if perl -ne 'exit 1 if /[ {202A}- {202E} {2066}- {2069} {200B}- {200D} {2060} {FEFF}]/' "$f" 2>/dev/null; then :
    else
      echo "UNICODE-HAZARD: $f contains Bidi or zero-width chars"
    fi
  fi
done
```

For each match in source code or `SKILL.md`/`README.md`: severity **HIGH**. In a SKILL.md, this is a prompt-injection vector (text the agent reads might not match what a human reviewer sees).

#### 7.3 MCP config scanning

Already covered by Stage 4's MCP file list — but Stage 7.3 also scans the *contents* of any MCP config for credential shapes, treating the JSON values as plain text and running Stage 1 patterns. Severity **CRITICAL** for any match.

```bash
mcp_configs="$(find . -type f \( -name 'mcp.json' -o -name 'claude_desktop_config.json' -o -name 'mcp_servers.json' \) 2>/dev/null)"
for cfg in $mcp_configs; do
  rg -E "$secret_patterns" "$cfg" && echo "MCP-CONFIG-LEAK: $cfg"
done
```

#### 7.4 GitHub Actions workflow lint

For repos with `.github/workflows/`:

- **Mutable tag references**: flag any `uses: org/action@v1` or `@main`. Pin to 40-hex SHA. Severity **MEDIUM** (per CVE-2025-30066 tj-actions, retroactive tag re-pointing is real).
- **`pull_request_target` + PR-controlled checkout**: flag any workflow with `on.pull_request_target` that also runs `actions/checkout` with `ref: ${{ github.event.pull_request.head.sha }}` or similar PR-controlled ref. Severity **HIGH** (pwn-request class).
- **Secrets in shell strings**: flag `${{ secrets.* }}` interpolated directly into `run:` shell blocks. Severity **MEDIUM** (CI log redaction is best-effort).
- **`workflow_run` chained from untrusted source**: flag any workflow triggered by `workflow_run` that downloads artifacts from the triggering run. Severity **HIGH**.

```bash
for wf in .github/workflows/*.yml .github/workflows/*.yaml; do
  [ -f "$wf" ] || continue
  # Mutable tag check
  grep -nE 'uses:\s*[^@]+@(v?[0-9]|main|master|HEAD)' "$wf" | \
    grep -v '#.*pinned' && echo "MUTABLE-TAG: $wf"
  # pull_request_target + checkout PR head
  if grep -q 'pull_request_target' "$wf" && grep -qE 'github\.event\.pull_request\.head\.(sha|ref)' "$wf"; then
    echo "PWN-REQUEST-RISK: $wf"
  fi
  # Secret in run: block
  awk '/run:/,/^[^ ]/' "$wf" | grep -E '\$\{\{\s*secrets\.' && \
    echo "SECRET-IN-RUN: $wf"
done
```

#### 7.5 Compromised-package SBOM check (Shai-Hulud family)

Compare each entry in `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` / `requirements.txt` / `Pipfile.lock` / `Cargo.lock` against a maintained blocklist of compromised package@version tuples. **The blocklist is the consumer's responsibility to maintain** — point at:

- Microsoft Defender team's published Shai-Hulud list (updated through May 2026 per their advisory)
- Sysdig's Shai-Hulud tracker
- Datadog Security Labs blocklists
- npm's `npm audit` for known-compromised packages

For each match: severity **CRITICAL** (the package is known-compromised; the credentials it could have stolen during install must be considered exposed).

This skill does not ship the blocklist — that would go stale. The skill ships the *check shape*; the user/org maintains the list.

#### 7.6 Pre-install / install-time script audit

For npm: flag any package whose `package.json` has `preinstall`, `install`, or `postinstall` scripts that:

- Reach the network (`curl`, `wget`, `fetch`, `http`)
- Write to `.github/workflows/` (Shai-Hulud's persistence mechanism)
- Write to `~/.npmrc`, `~/.config/`, `~/.ssh/`, or shell rc files
- Invoke `bash`, `sh`, `eval`, or `node -e`
- Reference `process.env` for harvest

For Python: same shape on `setup.py` / `pyproject.toml` build hooks.

Severity **HIGH** to **CRITICAL** based on what's done.

#### 7.7 SKILL.md / README static lint (prompt-injection vector)

Per Snyk ToxicSkills (Feb 2026): **36% of ClawHub agent skills contained prompt-injection content.** For any `.claude/skills/**/SKILL.md`, `.claude/agents/**.md`, `README.md`, or `CLAUDE.md` in the repo, flag:

- Override phrases: `ignore previous instructions`, `you are now`, `new task:`, `system override`, `developer mode`, `DAN`, `jailbreak`
- Outbound exfil URLs: `webhook.site`, `requestbin.*`, `pipedream.net`, `*.ngrok.io`, `discord.com/api/webhooks`, `*.beeceptor.com`
- Env-var harvest in prose: references to `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `AWS_*`, `GITHUB_TOKEN`, `~/.aws/credentials`, `~/.npmrc`, `~/.cursor/mcp.json` in document body
- Markdown image tags with data-exfil URLs: `![](https://x.com/log?d=...)`
- Tool definitions with broad `allowed-tools: ["*"]` or `Bash(*)` or `Write(*)`
- Hidden-instruction indicators: zero-width chars in body, Bidi controls, HTML comments containing instructions
- Multi-language repetition of the same instruction (classic jailbreak amplifier)
- Calls to install or update other skills mid-execution

Severity per match: **HIGH** (override phrases, exfil URLs, env-var harvest, broad tool scope, hidden chars), **MEDIUM** (multi-language repetition, install-other-skill calls).

This sub-stage is the heaviest single addition in v1.2. Future versions may split it out as a dedicated `prompt-injection-lint` skill.

#### 7.8 Lookalike-domain detection in URLs

For URLs in `README.md`, `SKILL.md`, `CLAUDE.md`, `CONTRIBUTING.md`, and any `.github/` workflow file, run Levenshtein distance ≤ 2 against:

- `npmjs.com` (catches `npnjs.com`, `npmjs.help`)
- `pypi.org` (catches `pypi.com`, `pypi-org.com`)
- `github.com` (catches `github.io.com`, `github-com.io`)
- `anthropic.com`, `claude.ai`
- `openai.com`
- `huggingface.co`

Severity **HIGH** (eslint-config-prettier, debug/chalk all entered via lookalike-domain phishing).

#### 7.9 Trufflehog/gitleaks invocation context check

If the repo's source code or build scripts contain a runtime invocation of `trufflehog`, `gitleaks`, or `detect-secrets` outside `.github/workflows/` or a documented CI context: severity **HIGH**. Per Semgrep (Sept 2025), Shai-Hulud variants embedded trufflehog calls in malicious npm packages to harvest secrets locally on the developer's machine.

## Output format

Materialize `SANITIZATION_REPORT.md` via the agent's own `Write` tool. **Recommended location:** `.scan-reports/sanitization-<YYYY-MM-DD>.md`, with `.scan-reports/` in `.gitignore`. **Never commit** a report containing CRITICAL or HIGH findings.

Template:

```
# Sanitization Report — <repo-name>

**Date:** YYYY-MM-DD
**Scanned by:** opensource-sanitizer v1.2.0
**Verdict:** PASS / PASS WITH WARNINGS (low/medium only) / PASS WITH ACCEPTED RISK (HIGH/MEDIUM accepted) / FAIL

## Summary

| Severity | Count |
|---|---|
| CRITICAL | N |
| HIGH | N |
| MEDIUM | N |
| LOW | N |

## Findings by stage

### Stage 1: Secrets

#### CRITICAL

| File | Line | Provider | Match (redacted) | Length | Remediation |
|---|---|---|---|---|---|
| src/config.py | 42 | AWS access key | `[REDACTED-AWS-len20]` | 20 | Remove; rotate in AWS; rewrite git history with `git filter-repo` |
| .cursor/mcp.json | 8 | Anthropic OAuth | `[REDACTED-ANTHROPIC-OAT-len64]` | 64 | Remove; rotate via OAuth re-issue; never commit MCP configs with real values |

### Stage 2: PII / Stage 3: Internal refs / Stage 4: Dangerous files / Stage 5: .env.example / Stage 6: Git history / Stage 7: Modern threat surface

(same shape; one section per stage)

## Acceptance log (HIGH/MEDIUM only)

For any HIGH or MEDIUM finding the team chose not to remediate before publication, document the rationale:

| Finding | Severity | Acceptance rationale | Approved by | Date |
|---|---|---|---|---|
| ... | HIGH | ... | ... | ... |

## Recommendations

[Ordered list of remediation steps the author must take before publication.]

## Out-of-scope notes

[Anything the scanner cannot evaluate, flagged for human review.]
```

## Verdict rules

- **PASS** — zero CRITICAL, zero HIGH, zero MEDIUM findings.
- **PASS WITH WARNINGS** — zero CRITICAL, zero HIGH; any MEDIUM or LOW findings (publication may proceed; warnings should be addressed).
- **PASS WITH ACCEPTED RISK** — zero CRITICAL; one or more HIGH or MEDIUM findings explicitly documented in the **Acceptance log** with rationale and approval. Publication proceeds only with explicit approval.
- **FAIL** — any single CRITICAL finding **OR** any HIGH finding without acceptance documentation.

A FAIL is final. Do not attempt to ship until the finding is removed (or, for git-history credentials, **rotated AND the history rewritten**).

**There is no "low-severity exception for critical findings."** If a future PR adds one, reject it as a backdoor pattern (Grok red-team finding #3).

## Patterns to refuse

- *"These are old credentials, they don't work anymore."* — Rotate them anyway. The next person to inherit the credential pattern won't know that.
- *"It's just a personal email; it's already public."* — Make the call about exposure explicit; document in the Acceptance log if shipping anyway.
- *"We can fix the .env after the push."* — No. Fix first.
- *"PASS WITH WARNINGS is fine for our HIGH findings."* — No. Use PASS WITH ACCEPTED RISK with an Acceptance log entry. Don't downgrade verdicts.
- *"The scanner missed nothing — we ran it."* — A single scanner is not sufficient. Run a second-opinion vendor scanner (TruffleHog, Gitleaks, GitGuardian) before considering the repo clean.
- *"We don't need workflow lint — we only use trusted actions."* — tj-actions/changed-files was trusted before March 14, 2025. Pin to SHA anyway. (CVE-2025-30066.)
- *"Shai-Hulud was patched, we're fine."* — Variants are still active as of May 2026. Maintain the SBOM blocklist.
- *"Our skill doesn't have `allowed-tools: *`."* — Broad tool scope wasn't the only ToxicSkills issue. Run Stage 7.7 on every SKILL.md.
- *"The Inspiration links in this skill have been there forever."* — Verify them at every audit. External resources can be retargeted.
- *"This worked example is just documentation."* — A worked example with imperative shell commands in a SKILL.md is also a prompt the agent may execute. Treat as live code.

## Backdoor defenses (new in v1.2)

If you maintain this skill, refuse PRs that:

1. Add a regex pattern that matches an obviously benign string (e.g., any 16-digit number). **Alert fatigue is an attack.** Grok-identified #1.
2. Weaken the redaction format (e.g., exposing more chars). v1.2's redaction matrix is calibrated; tightening only. Grok-identified #2.
3. Add a new verdict tier softer than PASS WITH ACCEPTED RISK. Grok-identified #3.
4. Add or replace links in the Inspiration section without verifying the destination. Grok-identified #4.
5. Add a worked example with imperative shell instructions (vs. quoted code samples). Grok-identified #5 / Microsoft prompts-as-shells May 2026.
6. Add a "whitelist" or "skip" mechanism for any pattern. Grok-identified #6.
7. Add debug/verbose output that includes unredacted matches even in rare conditions. Grok-identified #7.
8. Add an external library dependency (`requests`, `boto3`, etc.) to "validate" findings. The scan must run with the declared `allowed-tools` only. Grok-identified #8.
9. Add a "performance optimization" that skips file types or directories. Grok-identified #9.
10. Add a "temporary bypass" or "testing mode" flag. Grok-identified #10.

Reject these in PR review. Document the rejection in the PR comments so the pattern is visible to future maintainers.

## Validation checklist

- [ ] All seven stages were run
- [ ] `SANITIZATION_REPORT.md` was written to `.scan-reports/` (or equivalent gitignored location)
- [ ] Verdict is explicit (PASS / PASS WITH WARNINGS / PASS WITH ACCEPTED RISK / FAIL)
- [ ] All matches in the report use v1.2 redaction (`[REDACTED-{type}-len{N}]` for ≤39 chars, `first2****last2 (len N)` for ≥40 chars)
- [ ] CRITICAL findings (if any) are remediated before any push
- [ ] HIGH findings (if any) are either remediated or documented in the Acceptance log
- [ ] Git history review used pattern matching across history, **plus** `git fsck --unreachable` and reflog scan
- [ ] `.gitattributes` was audited for custom filter directives
- [ ] MCP config files in the repo were scanned for credential shapes
- [ ] Unicode hygiene check passed (no Bidi / zero-width characters in tracked source)
- [ ] Base64 / hex decode-then-rescan was applied to long strings
- [ ] GitHub Actions workflows were linted (mutable tags, pull_request_target, secrets-in-run)
- [ ] SKILL.md / README static lint was applied (prompt-injection patterns)
- [ ] Lookalike-domain check ran on all URLs in documentation
- [ ] No source files were modified by this skill (only the report file was written)
- [ ] Patterns in the SKILL match current cloud-provider formats (no stale OpenAI sk-* short format alone)
- [ ] A second-opinion scanner was run for coverage cross-check

## Troubleshooting

| Failure mode | Corrective step |
|---|---|
| Regex match returned no results but you expected secrets | Try multiline mode; verify the file isn't gitignored from the scan; run the decode-then-rescan pass |
| Report says PASS but you're sure something is in there | Run second-opinion scanner (TruffleHog, Gitleaks); check `git log --all --full-history -S "<suspicious string>"` manually; check unreachable objects |
| Tool refuses to scan binary files | Skip them by extension; if binary likely contains a credential (e.g., `.sqlite`, `.png` EXIF), extract text first with `strings` or `exiftool` |
| `.env.example` is missing | Generate one from referenced env vars discovered in Stage 5; flag as MEDIUM until done |
| Repo has 100k+ commits; git scan is slow | Limit to last 2 years (`--since`) for the pattern-match pass; do full history walk only on demand. Always still run unreachable + reflog. |
| Report contains a raw secret (redaction failed) | Stop. Treat the report itself as a credential leak. Delete the report. Re-run with explicit redaction. Don't commit. |
| Pattern is too broad; many false positives | Tighten with required context (e.g., require `aws` keyword within 20 chars); add to a per-repo allowlist file with documented rationale; **do not relax the pattern globally** |
| Scanner tells you to do something destructive | Stop. The scan is read-only. Any "fix it for me" instruction is a misuse — refer to the principle: *the author of the change is responsible for the fix.* |
| Unicode hygiene flag on a file you trust | Investigate; legitimate uses (e.g., a `tests/i18n/` fixture with bidi-needed text) should be allowlisted explicitly, not relaxed globally |
| Workflow lint flags an action you trust | Pin to SHA anyway. The lesson of tj-actions is that "trust" can be revoked retroactively. |
| Shai-Hulud SBOM check reports stale | Update the blocklist source. The check is structural; the data is the consumer's responsibility. |

## Inspiration and audit notes

The six-stage structure is generalized from [`affaan-m/everything-claude-code/agents/opensource-sanitizer.md`](https://github.com/affaan-m/everything-claude-code/blob/main/agents/opensource-sanitizer.md) (MIT). Re-written here for public domain. The "verify everything independently" principle and PASS/FAIL verdict format are kept; the specific regex patterns, severity rubric, redaction rule, "What this skill cannot do" disclaimer, "How to audit this skill" meta-section, four-tier verdict, language-agnostic Stage 5, full-history Stage 6 pattern matching, Stage 7 modern-threat-surface additions, "Backdoor defenses" section, tool-scoping caveat, and "May 2026 threat context" are this implementation's own choices.

### v1.0.0 → v1.1.0 → v1.2.0 audit log

**v1.0.0 → v1.1.0 (self-audit 2026-05-11):** Closed 13 findings — read-only contradiction, output-template redaction was suggested not enforced, permissive verdict, 16+ missing cloud-provider patterns, narrow git scan, no "what this skill cannot do" section, no "how to audit" meta-section, no tool-scoping caveat, no large-repo troubleshooting, allowed-tools missing `Bash(git diff:*)` and `Bash(git ls-files:*)`. See v1.1.0 inspiration section for the full list.

**v1.1.0 → v1.2.0 (multi-source audit 2026-05-11):** Conducted via parallel pipeline — May 2026 threat research (async agent), GPT red-team consult, Grok red-team consult. Sources cited below.

Threat-anchored additions (research-driven):

| Source | Date | Finding | v1.2 response |
|---|---|---|---|
| CVE-2025-30066 (tj-actions/changed-files) | 2025-03-14 | Retroactive tag re-pointing; secrets dumped as double-base64 in CI logs | Stage 7.1 (decode-then-rescan); Stage 7.4 (workflow lint, mutable-tag flag) |
| CVE-2025-54136 (Cursor MCPoison) + CVE-2025-54135 | 2025-07 / 08 | MCP trust bound to name, not config | Stage 4 + Stage 7.3 (MCP config scan) |
| Shai-Hulud worm v1 / v2 / v3 | 2025-09 / 11 / 2026-04 | npm self-replicating; harvests secrets; uses trufflehog offensively | Stage 7.5 (SBOM blocklist check); Stage 7.6 (pre-install audit); Stage 7.9 (local trufflehog invocation) |
| eslint-config-prettier hijack | 2025-07-18 | npnjs.com phishing | Stage 7.8 (lookalike-domain detection) |
| Snyk ToxicSkills | 2026-02 | 36% of ClawHub skills had prompt injection | Stage 7.7 (SKILL.md / README static lint) |
| Anthropic Git MCP CVE-2025-68143/4/5 | 2026-01 | Prompt injection via README in MCP server | Stage 7.7 + paired skill recommendation |
| GitGuardian: 24,008 MCP-config secrets | 2026-04-14 | MCP configs leaking | Stage 4 (MCP files) + Stage 7.3 (config content scan) |
| Trojan Source / CVE-2021-42694 | 2021-11 (still relevant) | Bidi + zero-width Unicode hides code | Stage 7.2 (Unicode hygiene) |
| Microsoft "prompts as shells" | 2026-05-07 | RCE in AI agent frameworks via fetched docs | Stage 7.7 + Backdoor-defenses section |
| GitHub secret scanning pattern updates | 2026-03-10 | 28 new detectors | Stage 1 pattern roster sync (sk-proj, sk-ant-oat, ASIA, ghr_, hf_, rk_, etc.) |

Pattern-table additions (16+ new entries):

- `ASIA[0-9A-Z]{16}` (AWS STS / Identity Center)
- `sk-ant-oat[0-9]{2}-` (Anthropic OAuth)
- `sk-ant-api[0-9]{2}-` (broadened version digits)
- `sk-ant-admin[0-9]{2}-` (broadened version digits)
- `sk-None-` (legacy OpenAI)
- `ghr_` (GitHub refresh)
- `rk_(test|live)_` (Stripe restricted)
- `hf_` (Hugging Face)
- DeepSeek contextual
- GCP service account base64-wrapped
- DB URL: added `redis://`, `mssql://`, `mariadb://`, `oracle://`, `couchdb://`
- Slack: broadened token-type chars to include refresh (xoxe-)
- Cloudflare / Heroku: contextual rather than greedy

Redaction strengthened: v1.1 used `first4****last4` for everything. v1.2 fully redacts ≤39-char matches as `[REDACTED-{type}-len{N}]` and uses `first2****last2 (len N)` only for ≥40-char matches. Rationale: 8 exposed chars on a 32-char key reveals 25% of entropy.

Stages added:

- **Stage 7.1: Decode-then-rescan** — base64 (≥40 chars), hex (≥64 chars), URL-encoded
- **Stage 7.2: Unicode hygiene** — Bidi controls, zero-width chars, confusables
- **Stage 7.3: MCP config content scan** — scan inside .cursor/mcp.json etc.
- **Stage 7.4: GitHub Actions workflow lint** — mutable tags, pull_request_target, secrets-in-run, workflow_run
- **Stage 7.5: Compromised-package SBOM check** — Shai-Hulud family
- **Stage 7.6: Pre-install script audit** — npm preinstall/postinstall hooks
- **Stage 7.7: SKILL.md / README static lint** — prompt-injection patterns
- **Stage 7.8: Lookalike-domain detection** — Levenshtein vs known infrastructure domains
- **Stage 7.9: Local trufflehog/gitleaks invocation context** — Semgrep 2025 finding

Stage 6 (git history) expanded with unreachable objects (`git fsck --unreachable`), reflog scan, and `.gitattributes` filter audit.

Stage 4 expanded with `.envrc`, `*.tfvars`, `*.sops.yaml`, `*.age`, ansible-vault files, plus the new MCP config file list.

Backdoor-defenses section added: 10 specific PR patterns to refuse, derived from Grok red-team. Each one with attribution.

**Sources (May 2025 – May 2026):**

- [GitHub changelog: pattern updates Mar 2026](https://github.blog/changelog/2026-03-10-secret-scanning-pattern-updates-march-2026/)
- [GitHub changelog: fine-grained PATs GA 2025-03-18](https://github.blog/changelog/2025-03-18-fine-grained-pats-are-now-generally-available/)
- [CISA: tj-actions/changed-files CVE-2025-30066](https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-tj-actionschanged-files-cve-2025-30066-and-reviewdogaction)
- [Wiz: tj-actions analysis](https://www.wiz.io/blog/github-action-tj-actions-changed-files-supply-chain-attack-cve-2025-30066)
- [Krebs: Shai-Hulud v1](https://krebsonsecurity.com/2025/09/self-replicating-worm-hits-180-software-packages/)
- [Sysdig: Shai-Hulud](https://www.sysdig.com/blog/shai-hulud-the-novel-self-replicating-worm-infecting-hundreds-of-npm-packages)
- [Datadog: Shai-Hulud 2.0](https://securitylabs.datadoghq.com/articles/shai-hulud-2.0-npm-worm/)
- [Microsoft: Shai-Hulud 2.0 guidance](https://www.microsoft.com/en-us/security/blog/2025/12/09/shai-hulud-2-0-guidance-for-detecting-investigating-and-defending-against-the-supply-chain-attack/)
- [Microsoft: prompts as shells 2026-05-07](https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks/)
- [Upwind: debug/chalk attack](https://www.upwind.io/feed/npm-supply-chain-attack-massive-compromise-of-debug-chalk-and-16-other-packages)
- [OPSWAT: eslint-config-prettier](https://www.opswat.com/blog/recent-eslint-hack-raises-software-supply-chain-concerns-to-the-next-level)
- [Semgrep: malicious trufflehog-using packages](https://semgrep.dev/blog/2025/security-advisory-npm-packages-using-secret-scanning-tools-to-steal-credentials/)
- [Check Point: MCPoison](https://research.checkpoint.com/2025/cursor-vulnerability-mcpoison/)
- [Tenable: CVE-2025-54135/54136 FAQ](https://www.tenable.com/blog/faq-cve-2025-54135-cve-2025-54136-vulnerabilities-in-cursor-curxecute-mcpoison)
- [Hacker News: Anthropic MCP RCE](https://thehackernews.com/2026/04/anthropic-mcp-design-vulnerability.html)
- [Snyk: ToxicSkills](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/)
- [GitGuardian: State of Secrets Sprawl 2026](https://thehackernews.com/2026/03/the-state-of-secrets-sprawl-2026-9.html)
- [GitGuardian: 29M leaks 2025 / MCP configs](https://www.helpnetsecurity.com/2026/04/14/gitguardian-ai-agents-credentials-leak/)
- [Trojan Source / CVE-2021-42694](https://en.wikipedia.org/wiki/Trojan_Source)
- [AquilaX: git history as credential store](https://aquilax.ai/blog/secrets-git-history-rotation)
- [arxiv 2601.17548: prompt injection on agentic coding assistants](https://arxiv.org/html/2601.17548v1)
- [Hugging Face: security tokens](https://huggingface.co/docs/hub/en/security-tokens)
- [DataStudios: OpenAI auth 2025](https://www.datastudios.org/post/openai-authentication-in-2025-api-keys-service-accounts-and-secure-token-flows-for-developers-and)
- [TokenMix: Anthropic key guide 2026](https://tokenmix.ai/blog/anthropic-api-key-generate-secure-rotate-2026)

The audit was performed in response to operating principle #6 (audit security tools harder) combined with the user observation that *security tools are the best place to hide malicious code*. Applied: research-anchored hardening, multi-source red-team (GPT challenge + Grok backdoor-design + autonomous research agent), backdoor-defense section with PR-rejection patterns, redaction strengthened against entropy leakage.
