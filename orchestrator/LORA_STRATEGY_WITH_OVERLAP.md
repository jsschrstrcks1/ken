# LoRA Strategy: Individual LoRAs with Intelligent Overlap

**Architecture Decision:**
- **One LoRA per individual author/entity** (not per collection)
- **Overlapping content is INCLUDED in both LoRAs** (e.g., MacArthur article in TGC appears in both)
- **Result:** Richer, multi-authored voice models instead of diluted blends

---

## Complete LoRA Inventory: 36 Potential Sources

### Active (With Text Content): 22 LoRAs

#### Tier 1: Flagship (>7M words)
1. **Al Mohler** | 3,449 files | 12.49M words | Reformed Baptist, apologetics
2. **Alistair Begg** | 3,064 files | 8.48M words | Reformed Baptist, expository
3. **John MacArthur** | 769 text files | 7.07M words | Dispensational, systematic

#### Tier 2: Major (4-6M words)
4. **Conrad Mbewe** | 1,160 files | 5.56M words | African Reformed, missions
5. **Jeff Noblit** | 728 files | 4.87M words | Reformed Baptist (Founders)
6. **The Gospel Coalition (TGC)** | 6,061 files | 4.69M words | Evangelical consensus (500+ contributors)

#### Tier 3: Substantial (1-3M words)
7. **Danny Akin** | 1,200 text files | 2.09M words | Southern Baptist, expository
8. **NOBTS Chapel** | 384 files | 1.50M words | New Orleans Baptist seminary chapel
9. **R.C. Sproul** | 548 text files | 0.49M words | Reformed (Ligonier)

#### Tier 4: Solid (< 1M words)
10. **SEBTS Chapel** | 59 files | 0.29M words | Southeastern Baptist seminary chapel
11. **Paul Washer** | 183 files | 0.21M words | Evangelical, missionary
12. **SBTS Chapel** | 37 files | 0.14M words | Southern Baptist seminary chapel
13. **Spurgeon** | 8 files | 0.12M words | Reformed, historic (19th c.)
14. **Tom Ascol** | 1,757 files (1,798 MP3s) | 0.10M words | Reformed Baptist, Founders
15. **Voddie Baucham** | 310 files | 5.2k words | Reformed, African-American
16. **Voddie Baucham (washer dir)** | 387 files | 0.10M words | (archive artifact)
17. **Monergism** | 399 text files | 91k words | Reformed aggregator
18. **G3 Ministries** | 10 files | 46k words | Reformed Baptist conference

#### Tier 5: Minimal/Metadata
19. **Illustrations** | 1 file | 885 words | Meta (illustration catalog)
20. **TftG (misc)** | 24 files | 510 words | Misc external
21. **G3** | 26 files | 357 words | Misc external
22. **Chandler** | 13 files | 272 words | External (archived separately)

### Planned/Placeholders: 14 More (To Be Filled)

| Name | Status | Expected |
|------|--------|----------|
| **David Platt** | Placeholder | TBD |
| **Mark Dever** | Placeholder | TBD |
| **Stephen Davey** | Placeholder | TBD |
| **Thabiti Anyabwile** | Placeholder | TBD |
| **John Frame** | Placeholder | TBD |
| **NOBTS Seminary** | Placeholder (chapel exists) | TBD |
| **SBTS Seminary** | Placeholder (chapel exists) | TBD |
| **SEBTS Seminary** | Placeholder (chapel + Panopto) | TBD |
| **Puritan Theological Seminary** | Placeholder | TBD |
| **Reformed Theological Seminary** | Placeholder | TBD |
| **Westminster Seminary** | Placeholder | TBD |
| **Forge Education** | Placeholder | TBD |
| **Founders Seminary** | Placeholder (Noblit/Ascol) | TBD |
| **SEBTS Chapel Panopto** | Placeholder (video metadata) | TBD |

---

## Overlap Strategy: Explicit Inclusion

### Example: MacArthur in Multiple LoRAs

**MacArthur corpus** (769 files, 7.07M words) appears in:
- ✅ **MacArthur LoRA** (individual author)
- ✅ **TGC LoRA** (MacArthur wrote for TGC, included there too)
- ✅ **Possible:** Ligonier connection? (if any cross-publication)

**Result:** MacArthur's voice strengthens BOTH LoRAs independently.

### Other Multi-LoRA Authors

- **Mohler:** Appears in Mohler LoRA + TGC (contributed)
- **Begg:** Appears in Begg LoRA + TGC + G3 (speaker/contributor)
- **Akin:** Appears in Akin LoRA + NOBTS (dean of chapel)
- **Mbewe:** Appears in Mbewe LoRA + possibly Ligonier (contributed)

### Seminary Data (Dual Use)

- **NOBTS Chapel:** Separate LoRA (speakers who preached there)
- **SEBTS Chapel:** Separate LoRA (speakers who preached there)
- **SBTS Chapel:** Separate LoRA (speakers who preached there)
- **Potential:** Videos from SEBTS Panopto → SEBTS Seminary LoRA

---

## LoRA Training Priority

### Phase 1: Immediate (Ken Only)
1. **Ken** (2.52M words, 448 files) → 3-4 hrs training

### Phase 2: High-Tier (Days 2-3, Cluster Parallel)
2. **Al Mohler** (12.49M)
3. **Alistair Begg** (8.48M)
4. **John MacArthur** (7.07M)
5. **Conrad Mbewe** (5.56M)
6. **Jeff Noblit** (4.87M)
7. **TGC** (4.69M)

*Train 3 simultaneously on m4max + m3pro + homeserve → ~4 hrs wall-clock for 6 LoRAs*

### Phase 3: Major (Days 3-4, Parallel)
8. **Danny Akin** (2.09M)
9. **NOBTS Chapel** (1.50M)
10. **R.C. Sproul** (0.49M)

### Phase 4: Solid (Days 4-5, Parallel)
11-18. Remaining tier 4 sources (~1M words total)

### Phase 5: Placeholders (As Data Arrives)
19-36. David Platt, Mark Dever, seminaries, Panopto videos, etc.

---

## Total Ecosystem

| Metric | Value |
|--------|-------|
| **Active LoRAs** | 22 |
| **Placeholder LoRAs** | 14 |
| **Total possible** | 36 |
| **Total active words** | 48.3M |
| **Total active files** | 21,025 |
| **Including Ken** | 23 active + 14 placeholders = **37 total** |

---

## Deployment Architecture

Each LoRA:
- ✅ **Open-weight:** Cluster-trained (m4max/m3pro/homeserve)
- ✅ **Closed-weight:** Claude persona (Opus/Sonnet/Haiku)
- ✅ **Overlap-aware:** Content shared with other LoRAs (no dedup)
- ✅ **Validation gates:** cite-or-flag, drift, era stability, register consistency
- ✅ **Debate mode:** Any combination can debate (e.g., MacArthur vs. TGC vs. Mohler)

---

## Next Steps

1. **Confirm 22 active LoRAs ready to train?**
2. **Approve overlap strategy?** (MacArthur in both MacArthur + TGC, etc.)
3. **Fill placeholders?** (David Platt, Mark Dever, etc. — where are they?)
4. **Model access:** m4max qwen3:32b path needed to start

---

_50.9 million words. 21,025 files. 23 active + 14 placeholders = 37 LoRAs possible._

_Soli Deo Gloria._
