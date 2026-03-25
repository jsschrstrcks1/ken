---
name: cross-repo-health
description: "One-command health check across all 9 repositories. Checks content freshness, link integrity, validation status, memory health, and git status."
version: 1.0.0
---

# Cross-Repo Health Dashboard

> One command. Nine repos. Full picture.

## Purpose

Runs a health check across all 9 repositories and produces a summary dashboard. Catches problems before they compound.

## When to Fire

- On `/health` command
- When asking "how are the repos doing" or "what needs attention"
- At session start in the ken repo

## Repositories

| Repo | Path | Domain |
|------|------|--------|
| Romans | /home/user/Romans | Sermons |
| ken | /home/user/ken | Hub |
| Allrecipes | /home/user/Allrecipes | Recipe aggregator |
| flickersofmajesty | /home/user/flickersofmajesty | Photography |
| Grandmasrecipes | /home/user/Grandmasrecipes | Recipes |
| Grannysrecipes | /home/user/Grannysrecipes | Recipes |
| InTheWake | /home/user/InTheWake | Cruise planning |
| manateecreeksheep | /home/user/manateecreeksheep | Sheep flock |
| MomsRecipes | /home/user/MomsRecipes | Recipes |

## Health Checks Per Repo

1. **Git status** — uncommitted changes, unpushed commits
2. **Memory health** — `python3 /home/user/ken/orchestrator/memory_ops.py tree --domain <domain>`
3. **Skills count** — how many skills deployed
4. **Content freshness** — any HTML files with last-reviewed >90 days (where applicable)
5. **Validation** — run validate-recipes.py or validate_flock.py if available

## Dashboard Format

```
## Cross-Repo Health — [date]

| Repo | Git | Memory | Skills | Freshness | Validation | Status |
|------|-----|--------|--------|-----------|-----------|--------|
| Romans | clean | 12 active | 12 | n/a | n/a | ✅ |
| ken | clean | 3 active | 7 | n/a | n/a | ✅ |
| Allrecipes | 2 modified | 0 | 13 | n/a | n/a | ⚠️ |
| flickersofmajesty | clean | 5 active | 19 | 1 stale | n/a | ⚠️ |
| Grandmasrecipes | clean | 8 active | 15 | 0 stale | ✅ pass | ✅ |
| InTheWake | 3 untracked | 15 active | 16 | 12 stale | n/a | ⚠️ |
| manateecreeksheep | clean | 4 active | 10 | n/a | 2 warnings | ⚠️ |
| ...

### Action Items
1. [repo]: [what needs attention]
2. [repo]: [what needs attention]
```

## Quick Check Commands

```bash
# Git status across all repos
for repo in Romans ken Allrecipes flickersofmajesty Grandmasrecipes Grannysrecipes InTheWake manateecreeksheep MomsRecipes; do
  echo "=== $repo ===" && cd /home/user/$repo && git status -s
done

# Memory health across all domains
python3 /home/user/ken/orchestrator/memory_ops.py stats
```

---

*Soli Deo Gloria* — Faithful stewardship means knowing the state of your flocks.
