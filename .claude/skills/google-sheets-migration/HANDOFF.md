# Handoff — Google Sheets Migration Skill v2

## Session State (2026-03-29)

### What Was Done
1. Orchestra review identified 11 bugs in v1 script
2. Rewrote migration.gs v2 with all fixes:
   - Dynamic column detection via header matching (not hardcoded indices)
   - Single-read architecture: each animal sheet read ONCE, identity+lambing+medical extracted in one pass
   - Sub-sheet checkpoint: saves `animalIdx` so resume continues from exact sheet
   - 8-12 breed support: scans rows 1-24 matching against KNOWN_BREEDS list (23 breeds including spelling variants)
   - Lambing loop index advances correctly (inner while loop, no re-processing)
   - FAMACHA column detected by header matching, not assumed col C
   - Missing phases added: Pedigree, 2022 30-day weights
   - Time guard at 3m20s (200s), very aggressive
3. Factored new adapters (Perplexity, You.com) into post-migration QC plan
4. GPT orchestra round confirmed architecture, suggested preprocessing breed columns
5. Committed and pushed to ken branch

### Post-Migration QC Plan (uses new adapters)
After script runs successfully:
- `/consult gpt "verify these breed percentages all sum to 100%: [exported data]"` — math check
- `/consult perplexity "NSIP registry data for Katahdin ram OAV 2223"` — verify Kelsier's data against public records
- `/consult youdotcom "Manatee Creek sheep farm Florida breeding program"` — verify any public references

### Spreadsheet IDs
- **Source:** `1Rt6N0yD6DPWZmiPH1I2RAB3K0a-qsMWVfJH661tw4gk`
- **Dest:** `1EQ5bOZL5Xmzu_7VvaMHTHWIwHPJqDKTJY_MMPduKrJU`

### How to Resume
1. User pastes migration.gs into new sheet's Apps Script editor
2. Run `migrateAll()`
3. If timeout: `migrateResume()`
4. Check Migration Log tab
5. Run QC consults with orchestra adapters
