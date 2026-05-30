# Complete LoRA Inventory — 23 Authors/Preachers, 50.9M Words

**Total theologian LoRA ecosystem ready for training:**
- **1 author:** Ken (personal sermons)
- **22 preachers/sources:** Archive (theological breadth)
- **50.9M words total** across 21,025 files

---

## Ken (1)

| Author | Files | Words | Type |
|--------|-------|-------|------|
| **Ken** | 448 | 2.52M | Personal sermon manuscripts (nt, ot, topical) |

---

## Archive Preachers (22)

### Tier 1: Flagship (>7M words each)
| Rank | Preacher | Files | Words | % | Theology |
|------|----------|-------|-------|---|----------|
| 1 | **Al Mohler** | 3,449 | 12.49M | 25.8% | Reformed Baptist, apologetics |
| 2 | **Alistair Begg** | 3,064 | 8.48M | 17.5% | Reformed Baptist, expository |
| 3 | **John MacArthur** | 769 | 7.07M | 14.6% | Dispensational, systematic |

### Tier 2: Major (4-6M words)
| Rank | Preacher | Files | Words | % | Theology |
|------|----------|-------|-------|---|----------|
| 4 | **Conrad Mbewe** | 1,160 | 5.56M | 11.5% | African Reformed, missions |
| 5 | **Jeff Noblit** | 728 | 4.87M | 10.1% | Reformed Baptist (Founders) |
| 6 | **TGC** | 6,061 | 4.69M | 9.7% | Evangelical consensus (500+ authors) |

### Tier 3: Substantial (1-3M words)
| Rank | Preacher | Files | Words | % | Theology |
|------|----------|-------|-------|---|----------|
| 7 | **Danny Akin** | 1,200 | 2.09M | 4.3% | Southern Baptist, expository |
| 8 | **NOBTS Chapel** | 384 | 1.50M | 3.1% | New Orleans Baptist seminary |

### Tier 4: Solid (0.5-1M words)
| Rank | Preacher | Files | Words | % | Theology |
|------|----------|-------|-------|---|----------|
| 9 | **R.C. Sproul** | 548 | 0.49M | 1.0% | Reformed (Ligonier) |

### Tier 5: Niche (< 0.5M words)
| Rank | Preacher | Files | Words | % | Theology |
|------|----------|-------|-------|---|----------|
| 10 | SEBTS Chapel | 59 | 0.29M | 0.6% | Southeastern Baptist seminary |
| 11 | Paul Washer | 183 | 0.21M | 0.4% | Evangelical, missionary |
| 12 | SBTS Chapel | 37 | 0.14M | 0.3% | Southern Baptist seminary |
| 13 | **Spurgeon** | 8 | 0.12M | 0.3% | Reformed, historic (19th c.) |
| 14 | Tom Ascol | 1,757 | 0.10M | 0.2% | Reformed Baptist (Founders) |
| 15 | Voddie Baucham | 387 | 0.10M | 0.2% | Reformed, African-American |
| 16 | Monergism | 399 | 0.09M | 0.2% | Reformed (aggregator) |
| 17 | G3 Ministries | 10 | 0.05M | 0.1% | Reformed Baptist conference |
| 18 | Illustrations | 1 | 0.001M | 0.0% | Meta (illustration catalog) |
| 19 | TftG (misc) | 24 | 0.001M | 0.0% | Misc external |
| 20 | G3 (misc) | 26 | 0.0004M | 0.0% | Misc external |
| 21 | Chandler (misc) | 13 | 0.0003M | 0.0% | External (not included in Ken LoRA) |

---

## LoRA Priority Queue (23 Total)

### Tier 1: Launch Immediately
1. **Ken** (2.52M words, 448 files) → ~3-4 hrs training

### Tier 2: High Priority (Days 2-3)
2. **Al Mohler** (12.49M words, 3,449 files) → ~4 hrs
3. **Alistair Begg** (8.48M words, 3,064 files) → ~3.5 hrs
4. **John MacArthur** (7.07M words, 769 files) → ~4 hrs

### Tier 3: Major Voices (Days 3-4)
5. **Conrad Mbewe** (5.56M words, 1,160 files) → ~3 hrs
6. **Jeff Noblit** (4.87M words, 728 files) → ~3 hrs
7. **TGC Consensus** (4.69M words, 6,061 files) → ~3 hrs

### Tier 4: Supporting Voices (Days 4-5)
8. **Danny Akin** (2.09M words, 1,200 files) → ~1.5 hrs
9. **NOBTS Chapel** (1.50M words, 384 files) → ~1 hr
10. **R.C. Sproul** (0.49M words, 548 files) → ~30 min

### Tier 5: Specialty/Niche (Days 5-6)
11-23. Remaining 13 sources (1.5M words total) → ~2 hrs

---

## Training Timeline

### Sequential (m4max alone)
- Ken + 22 preachers: **~35-40 hours**

### Parallel (3 nodes: m4max + m3pro + homeserve)
- Ken + 22 preachers: **~15-18 hours wall-clock**
- Can run 3 LoRAs simultaneously

---

## Each LoRA Includes

✅ **Open-weight training:** Cluster node (m4max/m3pro/homeserve)  
✅ **Closed-weight persona:** Claude (Opus/Sonnet/Haiku tier)  
✅ **Validation gates:** cite-or-flag, drift detection, era stability  
✅ **Deployment:** Smart router + debate mode capability  
✅ **Documentation:** Training log, validation report, adapter registry entry

---

## Ecosystem Statistics

| Metric | Value |
|--------|-------|
| Total authors/preachers | **23** |
| Total files | **21,025** |
| Total words | **50.9M** |
| Average preacher size | **2.2M words** |
| Largest (Mohler) | **12.5M words** |
| Smallest (Chandler) | **272 words** |
| Reformed Baptist representation | **7 major voices** |
| Global South representation | **Conrad Mbewe (African Reformed)** |
| Seminary chapel recordings | **3 (NOBTS, SBTS, SEBTS)** |
| Historic voices | **Spurgeon (19th c.), R.C. Sproul** |

---

## Theological Coverage

**Represented frameworks:**
- Reformed Baptist (Mohler, Begg, Noblit, Ascol)
- Evangelical Baptist (Akin, Danny Akin)
- Dispensational (MacArthur)
- Reformed Presbyterian (Sproul, Frame if added)
- African Reformed (Mbewe, Baucham)
- Missionary/Global (Washer, Mbewe)
- Evangelical Consensus (TGC — 500+ authors)

**Coverage gaps (could add if desired):**
- Lutheran/Reformed traditions (minimal)
- Pentecostal/Charismatic (minimal)
- Catholic/Orthodox (not represented)
- Liberal/Mainline Protestant (not in archive)

---

## Next Steps

1. **Approve Ken LoRA training?** (Ready now, 2.52M words, pure Ken voice)
2. **Sequence for remaining 22?** (Suggested: Mohler → Begg → MacArthur)
3. **Parallel training on cluster?** (All 3 nodes = 15-18 hrs total)
4. **Model access confirmation?** (m4max qwen3:32b path needed)

---

_50.9 million words. 21,025 sermons. 23 theologian voices. Cluster ready._

_Soli Deo Gloria._
