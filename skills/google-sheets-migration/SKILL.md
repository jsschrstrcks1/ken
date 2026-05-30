---
name: google-sheets-migration
description: Migrate real data from the old 113-tab Manatee Creek spreadsheet to the new 26-tab Flock Manager structure. Uses chunked execution with checkpoint/resume to survive Apps Script 6-minute timeout and Claude Code rate limits.
---

# Google Sheets Migration Skill

## Purpose

Migrate all **real data** (not prospective breeding formulas) from the old Manatee Creek spreadsheet (113 tabs) into the new Flock Manager 2025 structure (26 tabs). Zero data loss.

## Spreadsheet IDs

- **Source (old):** `1Rt6N0yD6DPWZmiPH1I2RAB3K0a-qsMWVfJH661tw4gk`
- **Destination (new):** `1EQ5bOZL5Xmzu_7VvaMHTHWIwHPJqDKTJY_MMPduKrJU`

## What Migrates (Real Data Only)

| Source Location | Destination Tab | Data |
|---|---|---|
| Individual animal sheets rows 1-24 | Master Flock List | Identity, breed %, DOB, sire, dam, weight, tag |
| Individual animal sheets lambing year blocks | Breeding Season Tracker | Lamb name, sire, birth date, birth weight, 30/60/90 day weights, ADG, keep/sell |
| Individual animal sheets "Medical" sections | Health & Treatment Log | Date, treatment, FAMACHA score |
| Individual animal sheets FAMACHA scores | Famacha & FEC Trend | Date-indexed FAMACHA scores per animal |
| Lamb Data tab | Weight History & ADG | Extension service lamb records with WDA, ADG, adjusted weights |
| On Property tab | Pen sheets (1-6, Tree Fort, Goose) | Current pen rosters |
| Costs tab | Costs & Financials | Price paid, income, date acquired/sold, breeder |
| Ewe Data / Ram Data tabs | Active Ewes / Active Rams | Registry with service sire, dam/sire IDs |
| Weights and Averages tab | Weight History & ADG | Running weight averages |

## What Does NOT Migrate

- Prospective breeding calculators (formula sections starting at "Prospective Breedings")
- Cross-sheet formula references (`='Manatee Creek'!P5`)
- Empty placeholder rows
- Duplicate pen configurations (old Pen 1, Pen 2 vs 2024 versions — only latest)
- Sheet84, Sheet87, Sheet79, Sheet81 (scratch tabs)

## Timeout Strategy

Apps Script has a **6-minute execution limit**. The migration uses chunked execution:

1. **Phase 1 — Animal Identity** (~2 min): Read all 69 animal sheets, extract identity + breed %. Write to Master Flock List.
2. **Phase 2 — Lambing Records** (~2 min): Re-read animal sheets, extract lambing year blocks. Write to Breeding Season Tracker + Weight History.
3. **Phase 3 — Medical/FAMACHA** (~1 min): Extract medical sections. Write to Health & Treatment Log + Famacha & FEC Trend.
4. **Phase 4 — System Tabs** (~1 min): Costs, On Property (pen rosters), Ewe/Ram Data, Weights.

Each phase saves a checkpoint to `PropertiesService`. If timeout hits, run `migrateResume()` to continue from the last completed phase.

## How to Use

1. Open the **new** spreadsheet in Google Sheets
2. Go to Extensions > Apps Script
3. Paste the contents of `migration.gs` (in this skill folder)
4. Click Run > `migrateAll`
5. Grant permissions when prompted
6. If it times out, click Run > `migrateResume`
7. Check the "Migration Log" tab in the new sheet for progress

## Rate Limit Recovery (Claude Code)

If Claude Code hits a rate limit while working on this skill:

1. Write current state to `/tmp/sheets-migration-checkpoint.txt`
2. State includes: which phase, which animal index, what's left
3. Resume command: "Read /tmp/sheets-migration-checkpoint.txt and continue"

## Careful-Not-Clever Rules

- Read each source sheet once, extract everything in one pass
- Never overwrite existing data in destination — append only
- Log every write operation to the Migration Log tab
- If a cell value looks like a formula (`=`), skip it — we want real data only
- Preserve original spellings in notes (Amure, Jerkface, etc.)
- Mark uncertain data with source reference
