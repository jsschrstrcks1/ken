# Handoff — Google Sheets Migration Skill

## Session State (2026-03-29)

### What Was Done
1. Explored both repos (ken + manateecreeksheep) thoroughly
2. Downloaded and parsed both Google Sheets via xlsx export:
   - **Old sheet** (113 tabs): `/home/user/old_sheet.xlsx`
   - **New sheet** (26 tabs): `/home/user/new_sheet.xlsx`
3. Extracted animal data to `/home/user/old_sheet_animal_data.json` (69 animals, 94 lamb records, 35 medical entries)
4. Extracted system data to `/home/user/old_sheet_system_data.json` (4.4 MB, 30 sheets)
5. Wrote SKILL.md describing the migration
6. Wrote migration.gs — the Apps Script with 8 phases, checkpoint/resume, 4-minute time guard
7. Added skill to skill-rules.json

### What Still Needs Doing
- **Test the Apps Script** — it has NOT been run yet. User needs to paste it into the new sheet's Apps Script editor and run `migrateAll()`
- **Verify data completeness** — after migration, compare row counts against source
- **Column mapping may need tuning** — the old sheet has inconsistent layouts across animal tabs (some use col B for breed %, others col C; lambing headers vary between "Birth Weight" and "Sire" as col B). The script handles both variants but edge cases may exist
- **FAMACHA scores** — currently extracted in the medical phase but not separately written to the "Famacha & FEC Trend" tab. The Health & Treatment Log gets them. A second pass could pivot that data into the trend sheet format.
- **Pen 1 (2024) has a trailing space** in its name in the source sheet. The skip list handles both with/without but verify.

### Key Architecture Decisions
- **No MCP server** — Google Sheets MCP requires GCP credentials the user doesn't have set up. Instead we use the xlsx export trick (`/export?format=xlsx`) via curl + openpyxl for analysis, and Apps Script for the actual write-back.
- **8 phases, not 1 big run** — Apps Script has 6-minute limit. Each phase saves a checkpoint to PropertiesService. Time guard at 4 minutes (aggressive).
- **Append-only writes** — script never overwrites existing data in the new sheet. Uses `findFirstEmptyRow_()` to find where to start writing.
- **Formula filtering** — `safeStr_()` skips cross-sheet formula references (`='Manatee Creek'!P5`) and `#REF!` values. Only real data migrates.
- **Prospective breeding sections skipped** — anything after "Prospective Breedings" header in animal sheets is formulas, not data.

### Files Created This Session
- `/home/user/ken/.claude/skills/google-sheets-migration/SKILL.md`
- `/home/user/ken/.claude/skills/google-sheets-migration/migration.gs`
- `/home/user/ken/.claude/skills/google-sheets-migration/HANDOFF.md` (this file)
- `/home/user/old_sheet.xlsx` (downloaded, not committed)
- `/home/user/new_sheet.xlsx` (downloaded, not committed)
- `/home/user/old_sheet_animal_data.json` (extracted, not committed)
- `/home/user/old_sheet_system_data.json` (extracted, not committed)

### Spreadsheet IDs
- **Source (old, 113 tabs):** `1Rt6N0yD6DPWZmiPH1I2RAB3K0a-qsMWVfJH661tw4gk`
- **Destination (new, 26 tabs):** `1EQ5bOZL5Xmzu_7VvaMHTHWIwHPJqDKTJY_MMPduKrJU`

### How to Resume
1. Read this file
2. If script hasn't been tested yet → user needs to paste migration.gs into Apps Script and run
3. If script ran but needs fixes → read the Migration Log tab in the new sheet, fix the phase that failed
4. If adding FAMACHA trend pivot → add Phase 3b that reads Health & Treatment Log and pivots into Famacha & FEC Trend format
