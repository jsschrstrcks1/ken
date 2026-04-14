# InTheWake Admin Tooling

This directory contains admin tooling, historical audits, and development scripts for the `jsschrstrcks1/InTheWake` repository.

**Why it lives here:** The `ken` repository is the operational hub for cross-repository admin tooling. Nesting under `ken/admin/<repo-name>/` scales to additional repositories and keeps development-side assets out of the deployed website (which used to upload ~92MB of admin bloat to GitHub Pages on every deploy).

## Structure

| Directory | Purpose |
|---|---|
| `validators/`, `scripts/` | Active batch tools, validators, one-off utilities |
| `venue-research/` | LLM research output for cruise venue pages |
| `cabin-classifications/` | Cabin category data for stateroom-check tool |
| `source-materials/` | Authoring source documents (DOCX, PDF, RTF) |
| `archive/` | Historical audits, one-time fixers, superseded docs |
| `reports/` | Audit reports and analysis artifacts (non-HTML) |
| `hooks/`, `lib/`, `plans/` | Dev hooks, utility libraries, project plans |
| Top-level `.md` files | Analysis, planning, and evaluation documents |

## Staying in the InTheWake repo

These admin/ items remain in `InTheWake/admin/` because they're referenced at runtime by Claude Code sessions or served through `.htaccess` exceptions:

- `admin/claude/` — 18 files referenced by CLAUDE.md at session start
- `admin/UNFINISHED_TASKS.md`, `IN_PROGRESS_TASKS.md`, `COMPLETED_TASKS.md` — active task tracking
- `admin/CAREFUL.md`, `admin/CAREFUL_AUDIT_2026_03_27.md` — integrity guardrails
- `admin/reports/*.html` — user-facing reports served through `.htaccess`
- `admin/PORT_DISRUPTION_FACTORS_REFERENCE.md` — current research

## Developer workflow

Clone both repositories as siblings, e.g.:

```
~/code/
  InTheWake/
  ken/
```

Invoke admin tooling from the ken location:

```bash
cd ~/code/InTheWake
node ../ken/admin/inthewake/validators/validate.js
python3 ../ken/admin/inthewake/scripts/batch-validate-ships.js
```

Soli Deo Gloria.
