# Manatee Creek Data Redesign — Completion Plan (Orchestrator Side)

**Source thread:** session `01VbjUkAAxGLw6DP22izNYsZ` (Mar–Apr 2026)
**Branch:** `claude/manatee-creek-redesign-plan-ZuzsE`
**Companion plan (data side):** `manateecreeksheep/MANATEE_CREEK_REDESIGN_PLAN.md`

---

## Why this plan exists in ken

The thread touched two repos. `manateecreeksheep` owns the flock data;
`ken` owns the orchestrator, the `google-sheets-migration` skill, and
the cognitive memory store. This file covers only the ken-side work —
see the companion plan for the full context.

---

## What the thread left in ken

| Artifact | State |
|---|---|
| `.claude/skills/google-sheets-migration/migration.gs` (v2) | 572 lines, orchestra-reviewed, single-read architecture, sub-sheet checkpoints, 23 breeds matched, 200s time guard |
| `.claude/skills/google-sheets-migration/HANDOFF.md` | Dated 2026-03-29: "Paste into new sheet's Apps Script, run migrateAll()". **Still live.** |
| `orchestrator/adapters/` | All 5 adapters keyed (GPT, Gemini, Grok, Perplexity, You.com) |
| `orchestrator/env_seed.py` | Updated with all 5 keys including Perplexity and You.com |

Spreadsheet IDs:
- **Source (old 113 tabs):** `1Rt6N0yD6DPWZmiPH1I2RAB3K0a-qsMWVfJH661tw4gk`
- **Destination (new 26 tabs):** `1EQ5bOZL5Xmzu_7VvaMHTHWIwHPJqDKTJY_MMPduKrJU`

---

## Loose ends

### K1. `migration.gs` has never been run
The script was written but the user has never pasted it into the
destination sheet's Apps Script editor and clicked `migrateAll`. Every
record it would recover (old lambing years, pre-2026 medical, weight
timeseries, historical costs, original sire/dam lookups) is still
trapped in the 113-tab sheet — nearly a month since the HANDOFF was
written.

### K2. Cognitive memory is empty for the sheep domain
```
$ python3 orchestrator/memory_ops.py tree
{}
```
The thread made many durable decisions (selection hierarchy, pipeline
v3, hard lessons) — none of them are encoded. Next session starts blind.

### K3. Post-migration QC plan exists only in HANDOFF.md
HANDOFF lists three QC consults:
- `/consult gpt "verify these breed percentages all sum to 100%"`
- `/consult perplexity "NSIP registry data for Katahdin ram OAV 2223"`
- `/consult youdotcom "Manatee Creek sheep farm Florida breeding program"`

These are not wired to any script, are not automated, and will be
forgotten if HANDOFF.md gets deleted before they run.

---

## Plan

### Phase K1 — Pre-flight the migration
Before the user runs `migrateAll()`, verify the environment is sane.

1. Open the destination sheet
   (`1EQ5bOZL5Xmzu_7VvaMHTHWIwHPJqDKTJY_MMPduKrJU`) and confirm the 26
   tabs exist with their expected headers.
2. Open the source sheet and confirm the 113-tab structure matches what
   `migration.gs` expects — specifically: `KNOWN_BREEDS` list covers every
   breed name that appears in the 69 animal sheets; column headers match
   the header-detection logic.
3. Run `migration.gs` against a **copy** of the destination sheet first
   if the owner has any reservation — Apps Script has no undo.
4. Document any source-sheet quirks discovered during pre-flight in a
   new section of `SKILL.md`.

**Exit:** pre-flight checklist committed; any `KNOWN_BREEDS` gaps fixed
in `migration.gs`.

### Phase K2 — Run the migration
User-driven step.

1. Paste `migration.gs` into destination Apps Script editor.
2. Run `migrateAll()`.
3. If timeout, run `migrateResume()` — script will pick up from
   `PropertiesService` checkpoint at the exact animal index.
4. Check the auto-created "Migration Log" tab for errors.
5. Spot-check: pull 5 random animals from Master Flock List and diff
   against old sheet's corresponding animal tab. Zero drift.

**Exit:** Migration Log tab shows all phases complete; spot-check passes.

### Phase K3 — Post-migration QC (wires the HANDOFF's plan)
Automate the three consults so they don't vanish with HANDOFF.md.

1. Add `.claude/skills/google-sheets-migration/qc.sh` that runs the three
   `/consult` calls with current data from the destination sheet.
2. Output each consult's response to
   `.claude/skills/google-sheets-migration/qc_results/YYYY-MM-DD_<model>.md`.
3. Human review each report; any contradiction fixes the sheet (source
   of truth wins) or the data (if sheet wrong).

**Exit:** `qc.sh` runs cleanly; three reports committed with reviewer's
notes.

### Phase K4 — Encode thread's durable decisions in cognitive memory
Closes K2. This is the only phase that affects ken's long-term value —
without it, the next session rebuilds context from commits.

Minimum protected memory set (encode against `--domain sheep`, mark
`--protected` on every one):

```bash
cd /home/user/ken
python3 orchestrator/memory_ops.py encode sheep decision \
  "Selection hierarchy: FAMACHA/FEC > Hair (observed, not bred) > Breed > Meat. Performance beats pedigree. Codified in breeding_policy v2.0." \
  --tags breeding,policy,selection --protected

python3 orchestrator/memory_ops.py encode sheep fact \
  "Kelsier (Katahdin ram) is the gold standard sire — most parasite resistant animal observed on the property. Serendipity White Ram Twin (MC2606) is his best son." \
  --tags breeding,rams,katahdin --protected

python3 orchestrator/memory_ops.py encode sheep fact \
  "Hard lesson: St Croix and Barbados Blackbelly lineages DIED of parasites on this property despite reputation. Reject in favor of Katahdin/Awassi crosses." \
  --tags breeding,hard-lesson,parasites --protected

python3 orchestrator/memory_ops.py encode sheep fact \
  "Hard lesson: Dorper is parasite-vulnerable despite hair coat. Windlestone Dorper line especially. Hair coat and parasite resistance are INDEPENDENT traits." \
  --tags breeding,hard-lesson,dorper --protected

python3 orchestrator/memory_ops.py encode sheep pattern \
  "Pipeline v3: closed 7-pen geographic loop. Pen 3 (intake) -> Tree Fort -> Pen 4 -> Pen 5 -> Pen 6 -> Pen 1 -> Pen 2 (elite). West side (1,2) = late/elite stages, most secure shelter. Awassi outside loop in Goose Pen." \
  --tags breeding,pipeline,pens --protected

python3 orchestrator/memory_ops.py encode sheep decision \
  "Tag convention (adopted Feb 2026): MC26xx green tags, rams in LEFT ear, ewes in RIGHT ear. MC2601-2620 assigned. Predecessor tags (0033, 00110, etc.) still valid until animal replaced." \
  --tags tagging,convention --protected

python3 orchestrator/memory_ops.py encode sheep insight \
  "Spring 2026 drought rule: drought = lowest parasite pressure. Animals scoring FAMACHA 4-5 during drought are failing under minimum pressure -- the strongest cull signal possible. Do not defer these culls to 'wait and see'." \
  --tags famacha,culling,drought --protected
```

After encoding, link related memories:
```bash
# selection hierarchy ↔ pipeline v3 (hierarchy IS the stage criteria)
# hard lesson Dorper ↔ hard lesson St Croix/BBB (both reject-based)
# drought rule ↔ selection hierarchy (drought amplifies hierarchy's signal)
```

**Exit:** `memory_ops.py tree --domain sheep` shows ≥7 protected
memories; `recall "selection hierarchy" --domain sheep` returns the
right memory first.

### Phase K5 — Delete the HANDOFF
Once Phases K1–K4 complete, delete
`.claude/skills/google-sheets-migration/HANDOFF.md` per the handoff
protocol in `CLAUDE.md`: "Delete the handoff when the work is fully
complete."

---

## Execution order

```
K1 (pre-flight) ──► K2 (run migration) ──► K3 (post-migration QC) ──► K5 (delete HANDOFF)
                                                                           ▲
K4 (memory encoding) ──────────────────────────────────────────────────────┘
```

K4 is independent and can run any time; doing it before K5 means the
lessons are preserved even if the HANDOFF is deleted.

---

## Out of scope

- Expanding the export-to-26-tabs pipeline in `manateecreeksheep` — see
  data-side plan Phase 3.
- Wiring the Google Sheets MCP sync — see data-side plan Phase 4.
- Running new multi-LLM investigations. Four reports already exist in
  `manateecreeksheep/data/investigations/` and are plenty.

---

## What "done" looks like (ken side)

1. `migration.gs` has been run against the destination sheet; Migration
   Log tab shows all phases complete.
2. Three QC consults ran; reports committed to
   `.claude/skills/google-sheets-migration/qc_results/`.
3. `HANDOFF.md` deleted.
4. Cognitive memory `tree --domain sheep` shows ≥7 protected memories
   covering selection hierarchy, Kelsier, St Croix/BBB lesson, Dorper
   lesson, pipeline v3, tag convention, drought rule.
5. A memory of this redesign itself, linking to the companion plan:
   ```bash
   python3 orchestrator/memory_ops.py encode sheep decision \
     "Manatee Creek data redesign (session 01VbjUkAAxGLw6DP22izNYsZ) complete. Historical migration run, export pipeline covers 26 tabs, cognitive memory seeded. JSON is the single source of truth going forward." \
     --tags redesign,completion --protected
   ```
