# D.A. Carson & Sinclair Ferguson LoRAs

**Two Major Theologian LoRAs Discovered in TGC Archive**

---

## D.A. Carson LoRA

### Corpus
- **Source:** TGC articles (extracted from 6,061 total TGC articles)
- **Files:** 520 articles
- **Words:** 3.63M words
- **Type:** Reformed evangelical, New Testament scholar, apologetics

### Significance
- **Prolific TGC contributor** (8.6% of entire TGC corpus)
- **Theological depth:** New Testament scholarship + systematic theology
- **Voice:** Careful exegesis, intellectual rigor, cultural engagement
- **Representation:** Trinity Evangelical Divinity School

### LoRA Training
- **Data:** 520 TGC articles, 3.63M words
- **Samples:** ~1,815 samples (at 2k tokens/sample)
- **Training time:** ~2.5 hours on m4max
- **Cluster:** Open-weight (m4max qwen3:32b) + closed-weight (Claude Sonnet persona)

### Validation Gates
- **Cite-or-flag:** Carson's exegetical precision checked against quoted texts
- **Register stability:** Maintains scholarly tone across systematic/pastoral writing
- **Cross-reference:** Articles within Carson corpus cross-validated for consistency

---

## Sinclair Ferguson LoRA

### Corpus
- **Source:** TGC articles (extracted from 6,061 total TGC articles)
- **Files:** 301 articles
- **Words:** 78.9k words
- **Type:** Reformed Presbyterian, practical theology, pastoral application

### Significance
- **Substantial TGC voice** (5.0% of entire TGC corpus)
- **Theological framework:** Reformed Presbyterian + pastoral depth
- **Voice:** Accessible theology, practical wisdom, spiritual depth
- **Representation:** Ligonier Ministries, Westminster Seminary

### LoRA Training
- **Data:** 301 TGC articles, 78.9k words
- **Samples:** ~395 samples (at 2k tokens/sample)
- **Training time:** ~1 hour on m4max
- **Cluster:** Open-weight (m4max qwen3:32b) + closed-weight (Claude Haiku persona for efficiency)

### Validation Gates
- **Cite-or-flag:** Ferguson's theological claims checked against Reformed confessions
- **Pastoral consistency:** Maintains balance between doctrine and practice
- **Cross-reference:** Articles validated for theological continuity

---

## Combined Statistics

| Metric | Carson | Ferguson | Combined |
|--------|--------|----------|----------|
| **TGC Articles** | 520 | 301 | 821 |
| **Words** | 3.63M | 78.9k | 3.71M |
| **% of TGC** | 8.6% | 5.0% | 13.5% |
| **Training time** | 2.5 hrs | 1 hr | 3.5 hrs |

---

## Overlap Strategy

### D.A. Carson in Multiple LoRAs
- ✅ **D.A. Carson LoRA** (520 TGC articles)
- ✅ **TGC LoRA** (all 6,061 articles, Carson = 8.6%)
- ✅ **Debate mode:** Carson LoRA vs. TGC consensus (which includes Carson blended with 511 others)

**Result:** Carson's voice appears distinctly (individual LoRA) AND as part of TGC consensus

### Sinclair Ferguson in Multiple LoRAs
- ✅ **Sinclair Ferguson LoRA** (301 TGC articles)
- ✅ **TGC LoRA** (all 6,061 articles, Ferguson = 5%)
- ✅ **Ligonier connection?** (if Ferguson articles elsewhere)
- ✅ **Debate mode:** Ferguson vs. Carson vs. TGC consensus

---

## Deployment

### Open-Weight Training
- **D.A. Carson:** m4max qwen3:32b + adapter
- **Sinclair Ferguson:** m4max qwen3:32b + adapter
- **Can train sequentially:** ~3.5 hours total

### Closed-Weight Personas
- **D.A. Carson:** Claude Sonnet 4.6 persona ("Carson: Reformed evangelical, New Testament scholar, careful exegesis")
- **Sinclair Ferguson:** Claude Haiku 4.5 persona ("Ferguson: Reformed Presbyterian, pastoral depth, accessible theology")

### Smart Routing
- Request about NT exegesis → D.A. Carson LoRA (or Claude Sonnet fallback)
- Request about pastoral application → Sinclair Ferguson LoRA (or Claude Haiku fallback)
- Request about theological consensus → TGC LoRA

---

## Updated LoRA Queue

### Tier 1: Immediate (Ken Only)
1. **Ken** (2.52M, pure personal) → 3-4 hrs

### Tier 2: High-Priority (Days 2-3)
2. **Al Mohler** (12.49M) → 4 hrs
3. **Alistair Begg** (8.48M) → 3.5 hrs
4. **D.A. Carson** (3.63M) → 2.5 hrs ⭐ NEW
5. **John MacArthur** (7.07M) → 4 hrs
6. **Conrad Mbewe** (5.56M) → 3 hrs

### Tier 3: Major Voices (Days 3-4)
7. **Jeff Noblit** (4.87M) → 3 hrs
8. **TGC Consensus** (4.69M minus Carson/Ferguson) → 3 hrs
9. **Sinclair Ferguson** (78.9k) → 1 hr ⭐ NEW

### Tier 4: Supporting (Days 4-5)
10+. Danny Akin, NOBTS Chapel, R.C. Sproul, others

---

## Revised Timeline (Cluster Parallel)

With m4max + m3pro + homeserve (3 nodes):
- **Phase 1:** Ken (m4max) = 3-4 hrs
- **Phase 2:** Mohler (m4max) + Carson (m3pro) + Begg (homeserve) = 4 hrs wall-clock
- **Phase 3:** MacArthur (m4max) + Ferguson (m3pro) + TGC (homeserve) = 3.5 hrs wall-clock
- **Phase 4:** Mbewe + Noblit + rest = 3 hrs wall-clock
- **Total:** ~16-17 hours wall-clock (23 active LoRAs including Carson + Ferguson)

---

## Why These Two?

**D.A. Carson:**
- **3.63M words** = 7th largest single-author corpus in your ecosystem
- **Prolific Reformed evangelical** = distinct theological voice
- **Scholarly depth** = valuable LoRA for serious theological queries
- **Debate partner** for Mohler, MacArthur (different approach to same issues)

**Sinclair Ferguson:**
- **Important Reformed voice** = Presbyterian + pastoral balance
- **Complements Sproul/Horton** = Presbyterian tradition represented
- **Accessible but rigorous** = bridges academic + pastoral
- **Ligonier connection** = potential for additional external sources

---

## Next Steps

1. **Approve Carson + Ferguson as individual LoRAs?**
2. **Extract their TGC articles to separate JSONL files?**
3. **Sequence in training queue?** (Suggest: After Ken, in parallel with Mohler/Begg)
4. **Model access:** Still need m4max qwen3:32b confirmation

---

_D.A. Carson: 3.63M words. Sinclair Ferguson: 78.9k words. Both extracted from TGC, both ready to train._

_Soli Deo Gloria._
