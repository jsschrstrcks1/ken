# External Repository Security Scan — Kestrel

**Repo.** `https://github.com/John-MiracleWorker/Kestrel`
**Commit pinned.** `d49708df0cee2076e6bf4bbe45dd8bb8c8fa1e74` (2026-05-17 15:09:38 -0400, "Add ORACLE shadow routing and replay eval")
**Scan date.** 2026-05-17
**Scanner.** AgentShield (`ecc-agentshield`) + manual grep / hex pass per §4 of `research/github-concepts-import-plan.md`
**Source.** Facebook redirect (`l.facebook.com/l.php?u=...`), stripped to direct GitHub URL before fetch
**Code in scope.** Python source 14,774 lines across 41 modules in `src/nested_memvid_agent/`, plus `scripts/`, `tests/`, `web/`, `docs/`, CI, Dockerfile
**Code executed during scan.** None of Kestrel's. Only `git clone --depth 1 --no-tags --single-branch --filter=blob:none` and read-only file inspection. AgentShield ran via `npx -y` (the scanner the user's `security-scan` skill is built around).

---

## TL;DR

**No worms found.** No injected invisible characters, no `.pth` files, no `litellm`/`langchain` import surface, no env-var harvesting, no exfiltration endpoints, no `curl | sh`, no install-time execution. AgentShield grade **A (100/100)**, though that's a clean-by-absence pass — Kestrel ships no `.claude/` config for AgentShield to scrutinize. The substantive audit is the manual pass below.

Of the verification gates in §4 of the import plan, Kestrel **passes 5 of 6 directly** and one (4.1, pinned hashes) is a yellow flag rather than a fail. **Safe to read deeply and lift concepts from.** Not safe to `pip install` until the user makes an active choice and pins versions.

---

## §4 Gate-by-gate

### §4.1 No floating-tag installs — **YELLOW**

`pyproject.toml` uses floating lower bounds throughout: `memvid-sdk>=2.0`, `openai>=1.0`, `anthropic>=0.39`, `google-genai>=0.3`, `fastapi>=0.110`, `mcp>=1.0`, etc. This is standard Python ecosystem hygiene and matches what most projects do — but it is exactly the LiteLLM-March-2026 surface. If `memvid-sdk@2.x` ever goes rogue, anyone who has run `pip install nested-memvid-agent[memvid]` since then pulls the compromised version.

GitHub Actions also use major-tag pins (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/setup-node@v4`) rather than commit-SHA pins. Same class of risk, lower severity since GitHub itself signs releases.

**Mitigation if importing concepts.** Generate a hash-locked `requirements.txt` from the specific versions known to work, and only `pip install --require-hashes -r` against that lockfile. Do not run the bare `make install` / `make install-dev` / `make install-memvid` targets in their current form.

### §4.2 AgentShield clean — **PASS (by absence)**

```
Date:    2026-05-17T19:12:34.054Z
Target:  /tmp/kestrel-scan/Kestrel
Grade:   A (100/100)
Files scanned: 0
Findings: 0 critical, 0 high, 0 medium, 0 low, 0 info
```

Zero files scanned because there is no `.claude/`, `CLAUDE.md`, `settings.json`, `mcp.json`, `hooks/`, or `agents/*.md` for AgentShield to read. That is itself a positive — cloning Kestrel will not silently pick up a hostile Claude Code configuration into your tree.

### §4.3 No install-time execution — **PASS**

- No `setup.py` (uses `pyproject.toml` + `setuptools.build_meta`).
- No `.pth` files anywhere in the tree (`find . -name '*.pth' -not -path './.git/*'` returns empty).
- `src/nested_memvid_agent/__init__.py` is import-only — relative imports of `ContextCompiler`, `LayeredMemorySystem`, `MemoryHit/Layer/Record`, `RetrievalQuery`, plus `__all__`. No network, no subprocess, no file I/O, no `os.environ` reads.
- No `__init__.py` side effects in submodules either (spot-checked via the suspicious-pattern grep).
- Dockerfile is multi-stage, non-root (`USER kestrel`), `python:3.11-slim` base, no `curl | sh`, no untrusted `ADD` from URLs.

### §4.4 MINJA red-team for memory — **N/A** (no import yet)

Not applicable until a memory concept is actually lifted. When §3.2 of the import plan is implemented, the test still needs to be written against the resulting memory layer.

### §4.5 SRPO worm-survival check — **N/A** (no cross-context plumbing imported yet)

Same — applies when concepts are imported, not to upstream scan.

### §4.6 Skill provenance — **PASS** (matches the recommendation)

Kestrel's own `plugin_manager.py` independently arrives at the policy §3.13 of the plan recommends:

- Plugin URLs enforced HTTPS-only and `github.com/owner/repo`-shaped (line 319: `if parsed.scheme != "https": raise PluginError(...)`).
- Plugin install is `git fetch --depth 1` to a controlled directory — **no `pip install`** of plugin code.
- Plugin manifests carry SHA pins (`_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")`).
- Removal is `shutil.rmtree(install_path)`, not a side-effecting uninstall hook.

If concepts are lifted from Kestrel, this is the most directly transplantable.

---

## What the manual pass actually found

### Positives — strong security hygiene signals

1. **Every `subprocess.run` call is annotated** with `# nosec B603` and `# noqa: S603` plus a one-line justification ("fixed executable and argument vector," "list argv only, no shell," "fixed read-only git commands," etc.). Subprocess callsites in `cli.py`, `worker_isolation.py`, `skill_manager.py`, `plugin_manager.py`, `codex_cli_provider.py`, `command_tools.py`, `process_tools.py`, `git_tools.py`. All argv-form, no `shell=True`. The author runs bandit and has documented every finding it could raise.
2. **Active secret-redaction layer** in `event_log.py`:
   - `sk-[A-Za-z0-9_-]{12,}` (OpenAI / Anthropic)
   - `(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{12,}` (GitHub tokens)
   - `xox[baprs]-[A-Za-z0-9-]{12,}` (Slack)
   - `Bearer\s+[A-Za-z0-9._~+/=-]{12,}`
   - `api_key|token|password|authorization` key-value patterns
   - `-----BEGIN ... PRIVATE KEY-----` blocks
   
   The "hardcoded secrets" hits in `tests/test_event_log.py` and `tests/test_full_agent_runtime.py` are obvious test fixtures verifying the redaction actually works.
3. **`net_safety.py`** explicitly enforces `https://`-only URLs. The only `urlopen` callsites are in `channels/adapters.py` (Telegram bot — declared multi-channel architecture) and `tools/web_tools.py` (DuckDuckGo HTML search). No surprise endpoints.
4. **`secret_broker.py`** is a vault-shaped design: `vault_path`, public API returns metadata only, raw value only via explicit `resolve()`, fingerprint-salted public payload, allowed env names is an explicit set rather than blanket `os.environ` access. **No `dict(os.environ)`-shaped harvest patterns exist anywhere in the codebase.**
5. **Web dev server binds 127.0.0.1 only** (`web/package.json` scripts: `dev = vite --host 127.0.0.1`). React 19, Vite 7, axe-core for accessibility testing, jsdom for DOM testing. No `litellm`-shaped npm packages, no risky dev deps.
6. **CI workflow** has no `secrets.*` references. Tests run with `--provider mock`. There is no path by which a malicious PR can exfiltrate credentials through CI.
7. **One CI workflow** (`.github/workflows/ci.yml`), small attack surface.
8. **`AGENTS.md` is 19 lines of plain build directives.** WebFetch's preview model kept refusing to read it (treated it as prompt-injection bait); the actual content is the Codex build briefing — non-negotiables like "Use Memvid v2 `.mv2` files only," "Mock backend keeps tests deterministic," "No policy memory writes from a single ordinary event," "Every memory promotion needs evidence, provenance, confidence, and validation status." Consistent with the pitch's claims and clean.
9. **Zero invisible Unicode** in any of README.md / AGENTS.md / PROJECT_MANIFEST.md / docs/CODEX_FULL_AGENT_HANDOFF_PROMPT.md (zero hits for zero-width / BiDi / Tag-character codepoints).
10. **Convergent design.** The pitch's "exact-call approval gates," "memory promotion needs evidence," and "block unchanged retries" are present in the code, not just the README. The author has clearly implemented the security model they're pitching, not just described it.

### Yellow flags — worth knowing, none disqualifying

1. **Floating dependency bounds** — see §4.1.
2. **`plugin_manager.py:_run_git` accepts arbitrary `ref`** in `git fetch --depth 1 origin <ref>`. The `ref` is the git refspec the plugin manifest provides. Git fetch with attacker-controlled refspecs can do refspec-shaped weirdness (e.g., fetching into unexpected refs). Low severity in practice because the fetch target directory is controlled and the result is just a ref pointer, but worth a defensive narrowing: validate `ref` matches `_SHA_RE` or a tag/branch-name pattern before passing it to `git fetch`.
3. **`channels/manager.py:314-315`** uses `__import__("nacl.signing", ...)` and `__import__("nacl.exceptions", ...)`. This is deliberate lazy import of the libsodium Ed25519 signing module (signature verification on inbound channel messages). Not malicious, just unusual style. Static-analysis-unfriendly; worth a comment in code explaining why it's `__import__` rather than top-of-file.
4. **`tools/web_tools.py:102`** does plain DuckDuckGo HTML scraping with a regex. Fine for a research tool, but the parsed `href` values become URLs the agent might follow. If used in an autonomous loop, this is a Morris-II propagation path. The `net_safety.py` https-only check is the gate, but the agent shouldn't auto-follow scraped links without explicit allow-listing.
5. **`worker_isolation.py:49`** runs subprocesses for skill/plugin isolation. The comment says "fixed executable with argument vector" — verified by inspection. Worth re-reading whenever the skill execution surface is touched.

### Negatives — what I looked for and didn't find

None of these are present in the codebase:

- No `litellm`, no `langchain`, no `chromadb` (the three highest-risk dependency adoptions from the threat model)
- No `os.environ.copy()`, `dict(os.environ)`, or wholesale env-var enumeration
- No `eval(`, no `exec(` (the matches in the grep are all `compiler.compile(objective=...)` — the codebase's own context compiler)
- No `pickle.load`, `marshal.load` (the deserialization-RCE class)
- No `base64.b64decode` followed by `exec` (the standard payload-staging pattern)
- No suspicious URLs — only DuckDuckGo, Telegram bot API, OpenRouter, and a `mock.kestrel.local` test placeholder
- No `.pth` files
- No `setup.py`
- No `postinstall` npm hook in `web/package.json`
- No `.dockerignore` exclusions hiding sensitive files (it's clean)
- No `.env` checked in (only `.env.example`)
- No reference to known-bad PyPI packages from the TeamPCP campaign

---

## Recommendation

**Safe to read deeply. Safe to lift concepts from.** Specifically:

- The plugin-install model in `plugin_manager.py` is more conservative than §3.13 recommended and can be cited as a reference implementation.
- The secret-redaction regex set in `event_log.py` is directly liftable for ken's `cognitive-memory` skill.
- The `# nosec`/`# noqa` discipline is a reviewable pattern worth adopting on any ken / open-claw-stuff Python that uses subprocess.

**Not yet safe to `pip install`** in its current form because of §4.1. If you decide to run Kestrel locally for evaluation, generate a hash-locked `requirements.txt` first and install only that, and run it inside a container with no host network for credentials.

**Pitch vs. code.** The marketing-drift in the README flagged in the prompt-evaluation round is real and the code is still substantively better-engineered than the pitch's manifesto rhetoric suggests. The pitch oversells; the code under-claims. That's the unusual direction for a "vibe coding" repo — most go the other way.

---

## Scan reproduction

```bash
mkdir -p /tmp/kestrel-scan && cd /tmp/kestrel-scan
git clone --depth 1 --no-tags --single-branch --filter=blob:none \
  https://github.com/John-MiracleWorker/Kestrel.git
cd Kestrel
# Pinned to d49708df0cee2076e6bf4bbe45dd8bb8c8fa1e74
npx -y ecc-agentshield scan --path . --min-severity info --format markdown
```

Plus the four grep passes documented in the bash blocks above (invisible-char scan; suspicious-pattern scan over `src/` and `scripts/`; URL/secret/.pth scan; web/npm dep + `.claude` presence check).
