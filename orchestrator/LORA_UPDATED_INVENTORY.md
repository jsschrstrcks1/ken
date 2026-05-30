# Updated LoRA Inventory: Actual + Potential Sources

**Status:** Found 22 active sources in archive + 2 external collections + 14 potential placeholders

---

## Active Sources in Archive (22)

### Text Content: 48.3M Words

(See LORA_STRATEGY_WITH_OVERLAP.md for full list)

1. Al Mohler (12.49M)
2. Alistair Begg (8.48M)
3. John MacArthur (7.07M)
4. Conrad Mbewe (5.56M)
5. Jeff Noblit (4.87M)
6. TGC (4.69M)
7. Danny Akin (2.09M)
8. NOBTS Chapel (1.50M)
9. R.C. Sproul (0.49M)
10. SEBTS Chapel (0.29M)
11. Paul Washer (0.21M)
12. SBTS Chapel (0.14M)
13. Spurgeon (0.12M)
14. Tom Ascol (0.10M)
15. Voddie Baucham (0.005M)
16. Monergism (0.09M)
17. G3 Ministries (0.05M)
18. Illustrations (0.001M)
19. TftG (0.0005M)
20. G3 (0.0003M)
21. Chandler (0.0003M)
22. Washer (archive artifact, 0.10M)

---

## External Collections (Individual Transcripts)

### Stephen Davey (Collected Separately)
- **Source:** `/Projects/Romans/stephen-davey-transcripts/`
- **Files:** 149 sermon metadata files
- **Words:** ~9,600 words (stubs/metadata only — full transcripts need to be expanded)
- **Status:** Partial collection (sermon descriptions, not full texts)
- **Action:** Needs expansion to full sermon texts via TruthNetwork or other sources

### David Platt (Collected Separately)
- **Source:** `/Projects/Romans/david-platt-transcripts/`
- **Files:** 188 sermon files
- **Words:** ~7,400 words (stubs/metadata only — full transcripts need to be expanded)
- **Status:** Partial collection (from Logos.com, stored as stubs)
- **Action:** Needs expansion to full sermon texts via Logos.com API or re-harvest

---

## Placeholder Directories (Archive)

These directories exist but have NO TEXT (only metadata JSON files):

| Name | Status | Reason |
|------|--------|--------|
| David Platt | Placeholder | Stubs in `/Projects/Romans/david-platt-transcripts/` but empty in archive |
| Mark Dever | Placeholder | Mentioned in TGC, SEBTS Chapel, but no separate collection |
| Stephen Davey | Placeholder | Stubs in `/Projects/Romans/stephen-davey-transcripts/` but empty in archive |
| Thabiti Anyabwile | Placeholder | Directory exists, no content yet |
| John Frame | Placeholder | Mentioned (Puritan Theological Seminary founder), no content |
| NOBTS Seminary | Placeholder | Chapel has content, but seminary itself is empty |
| SBTS Seminary | Placeholder | Chapel has content, but seminary itself is empty |
| SEBTS Seminary | Placeholder | Chapel + Panopto metadata, but main seminary is empty |
| Puritan Theological Seminary | Placeholder | Expected, no content yet |
| Reformed Theological Seminary | Placeholder | Expected, no content yet |
| Westminster Seminary | Placeholder | Expected, no content yet |
| Forge Education | Placeholder | Expected, no content yet |
| Founders Seminary | Placeholder | Related to Noblit/Ascol, no separate content |
| SEBTS Chapel Panopto | Placeholder | Video metadata only, transcripts needed |

---

## Total LoRA Inventory

### Immediately Ready (22 Active)
- **Words:** 48.3M
- **Files:** 21,025
- **LoRAs:** Ken + 21 archive sources

### Expandable (2 Collections)
- **Stephen Davey:** 149 stub files → needs full text expansion
- **David Platt:** 188 stub files → needs full text expansion
- **Potential combined:** +2M words if fully harvested and expanded

### Potential (14 Placeholders)
- **Status:** Directories exist but empty
- **Action:** Need data harvesting (David Platt full transcripts, Mark Dever, Stephen Davey expansion, PANOPTO videos, seminary feeds, etc.)

---

## Revised Total

| Category | Count | Status |
|----------|-------|--------|
| **Active LoRAs** (ready now) | 22 | Ready to train |
| **Ken** (personal) | 1 | Ready to train |
| **Expandable** (need work) | 2 | Stubs exist, need expansion |
| **Placeholders** (future) | 14 | Empty, await data |
| **TOTAL POSSIBLE** | **39** | 23 ready + 2 pending + 14 future |

---

## Recommended Action Plan

### Phase 1: Immediate (Today)
✅ Train 22 active archive LoRAs + Ken (23 total)
- All data ready
- 48.3M words + 2.5M Ken
- Cluster training: 15-18 hours

### Phase 2: Short-term (Days 2-3)
🟡 Expand Stephen Davey + David Platt (2 LoRAs)
- Full harvest from TruthNetwork, Logos.com, YouTube
- Estimated: +2-3M words combined
- Training: +3 hours

### Phase 3: Medium-term (Days 4-7)
🟡 Harvest Mark Dever, PANOPTO videos, seminary feeds (8-10 LoRAs)
- Requires: YouTube, direct website scraping, video transcription
- Estimated: +5-10M words
- Training: +8-10 hours

### Phase 4: Long-term (Ongoing)
🟠 Build remaining placeholders (David Platt full, John Frame, others)
- As new data sources become available
- Estimated: +10-20M words over time

---

## Key Finding: Overlap is Already Happening

**Current archive already captures overlap:**
- **David Platt:** Appears in TGC (as contributor)
- **Mark Dever:** Appears in TGC + SEBTS Chapel
- **Danny Akin:** Appears in NOBTS Chapel (dean of chapel)
- **Stephen Davey:** Not in archive yet (separate collection)

**Implication:** When we train the archive now, we already get multi-source overlap. David Platt's voice will be in BOTH TGC LoRA AND (once expanded) David Platt LoRA.

---

## Next Steps (Ken's Decision)

1. **Train 23 active LoRAs immediately?** (Ken + 22 archive, 50.8M words total)
2. **Plan Phase 2?** (Expand Davey + Platt stubs to full transcripts)
3. **Which phase 3 sources are priority?** (Mark Dever? PANOPTO? Others?)
4. **Model access confirmation?** (m4max qwen3:32b ready?)

---

_50.8M words active. 39 LoRAs possible total. Cluster ready to train._

_Soli Deo Gloria._
