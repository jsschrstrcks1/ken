# LoRA Training Queue — Revised (48.3M Words Archive Found)

**Archive Audit Result:** 20,577 sermons, 48.3M words across 30 preachers/sources

---

## Queue Strategy: Highest-Impact First

### Tier 1: Ken-Expanded (Launch Immediately)
- **Data:** 40% Ken (7,861) + 60% archive (11,791)
- **Total:** 19,651 samples
- **Training:** m4max qwen3:32b, ~4-5 hrs
- **Validation:** Cite-or-flag, drift detection, era stability
- **Why first:** Operator-critical, foundational for downstream LoRAs
- **Deployment:** m4max + Claude Opus persona

### Tier 2: Al Mohler (Highest Archive Value)
- **Data:** 3,449 files, 12.5M words (25.8% of archive)
- **Samples:** ~6,250 samples (12.5M words ÷ 2k-token avg)
- **Training:** m4max, ~4 hrs
- **Validation:** Same gates
- **Why second:** Largest single corpus, Reformed Baptist theological depth
- **Deployment:** m4max + Claude Sonnet persona ("Mohler: careful exegesis, cultural engagement")

### Tier 3: Alistair Begg (Second Largest)
- **Data:** 3,064 files, 8.5M words (17.5%)
- **Samples:** ~4,250 samples
- **Training:** m4max, ~3.5 hrs
- **Validation:** Same gates
- **Why third:** Pure Reformed Baptist, accessible expository style
- **Deployment:** m4max + Claude Haiku persona (cost-efficient for inference)

### Tier 4: John MacArthur (Dispensational Balance)
- **Data:** 769 files, 7.1M words (14.6%)
- **Samples:** ~3,550 samples
- **Training:** m3pro (fallback if m4max busy), ~5 hrs
- **Validation:** Same gates
- **Why fourth:** Different theological framework (dispensational), substantial corpus
- **Deployment:** m3pro or m4max + Claude Sonnet persona

### Tier 5: Conrad Mbewe (African Voice)
- **Data:** 1,160 files, 5.6M words (11.5%)
- **Samples:** ~2,800 samples
- **Training:** m3pro, ~3.5 hrs
- **Validation:** Same gates + cultural-register stability check
- **Why fifth:** Non-Western voice, Global South theological perspective
- **Deployment:** m3pro + Claude Opus persona ("Mbewe: African Reformed, global missions focus")

### Tier 6: Jeff Noblit (Reformed Baptist Specific)
- **Data:** 728 files, 4.9M words (10.1%)
- **Samples:** ~2,450 samples
- **Training:** m3pro, ~3 hrs
- **Validation:** Same gates
- **Why sixth:** Deep Reformed Baptist theology (Founders Ministries)
- **Deployment:** m3pro + Claude Haiku persona

### Tier 7-15: Remaining (Parallel Queue)
| Rank | Preacher | Files | Words | Est. Training |
|------|----------|-------|-------|---|
| 7 | TGC (Consensus) | 6,061 | 4.7M | 3 hrs |
| 8 | Danny Akin | 1,200 | 2.1M | 1.5 hrs |
| 9 | R.C. Sproul | 548 | 0.49M | 30 min |
| 10 | NOBTS Chapel | 384 | 1.5M | 1 hr |
| 11 | Paul Washer | 183 | 0.21M | 15 min |
| 12 | SEBTS Chapel | 59 | 0.29M | 15 min |
| 13 | Spurgeon (8 items) | 8 | 0.12M | 10 min |
| 14 | Tom Ascol | 1,757 | 0.10M | 10 min |
| 15 | Others (8×) | 2,000+ | ~2M | ~2 hrs total |

---

## Execution Plan: Cluster-Parallel

### Phase 1: Ken-Expanded (Days 1-2)
- **Start:** Now (m4max)
- **Duration:** ~5.5 hrs (training + validation)
- **Parallel:** Fetch/prep Spurgeon corpus OR run Tier 7 (TGC) prep

### Phase 2: Mohler (Day 2)
- **Start:** After Ken validation passes
- **Duration:** ~4 hrs
- **Parallel:** Begg prep

### Phase 3: Begg (Day 2-3)
- **Start:** After Mohler validation passes
- **Duration:** ~3.5 hrs
- **Parallel:** MacArthur prep

### Phase 4-6: MacArthur, Mbewe, Noblit (Days 3-4)
- **Parallelization:** m4max + m3pro + homeserve (3 concurrent trainers)
- **Duration per trainer:** ~3-5 hrs each
- **Total:** ~12 hrs of wall-clock time (3 nodes × 4 hrs)

### Phase 7+: Remaining Preachers (Days 4-5)
- **Parallelization:** All 3 nodes + fallback to homeserve qwen3:8b
- **Duration:** ~2 days to clear queue

---

## Total Timeline

| Phase | LoRAs | Wall-Clock | Node(s) |
|-------|-------|-----------|---------|
| 1 | Ken | 5.5 hrs | m4max |
| 2 | Mohler | 4 hrs | m4max |
| 3 | Begg | 3.5 hrs | m4max |
| 4-6 | MacArthur, Mbewe, Noblit | ~4 hrs (parallel 3×) | m4max, m3pro, homeserve |
| 7+ | TGC, Akin, Sproul, rest | ~2 hrs (parallel 3×) | All nodes |
| **Total** | **15 LoRAs** | **~19 hrs** | **Cluster** |

(With sequential training on m4max alone: ~42 hrs)

---

## Validation Gates: Applied to Every LoRA

1. **Cite-or-Flag:** Every generated quote must resolve to indexed corpus chunk
2. **Substring Match:** Quote ⊆ chunk (detect hallucination)
3. **Drift Detection:** 20 paraphrases, LoRA flags ≥18/20 as out-of-envelope
4. **Register Stability:** Pre/mid/post era (e.g., Ken via Romans 1-8, 9-11, 12-16)
5. **Pass Threshold:** ≥85% pass rate across all gates for deployment

---

## Closed-Weight Personas (Fallback + Debate)

Each LoRA has a companion Claude persona for:
- **Fallback:** If open-weight LoRA unavailable
- **Debate mode:** Both respond, compare positions
- **API routing:** Smart selection based on request complexity

| LoRA | Persona | Model | Style |
|------|---------|-------|-------|
| Ken | Ken (operator) | Claude Opus 4.8 | Exegesis + theological care |
| Mohler | Careful exegesis, cultural engagement | Claude Sonnet 4.6 | Intellectual rigor + Reformed precision |
| Begg | Expository accessibility | Claude Haiku 4.5 | Clear teaching + practical application |
| MacArthur | Dispensational depth | Claude Sonnet 4.6 | Systematic theology + biblical structure |
| Mbewe | African Reformed, global missions | Claude Opus 4.8 | Contextual theology + cross-cultural wisdom |
| Noblit | Reformed Baptist theology | Claude Haiku 4.5 | Denominational clarity + ecclesiology |
| TGC | Evangelical consensus | Claude Sonnet 4.6 | Broad appeal + theological diversity |
| Others | Author-specific | Auto-selected | Fitted to available models |

---

## Deployment Topology

```
User Query
    ↓
Smart Router
    ↓
    ├─→ Simple request? → Haiku adapter (fast, cheap)
    ├─→ Complex request? → Sonnet adapter (balanced)
    ├─→ Frontier reasoning? → Opus adapter OR Claude API
    ├─→ Debate mode? → Both (adapter vs. Claude persona)
    └─→ LoRA down? → Fallback to closed-weight persona
```

---

## Next Steps (Ken's Input Needed)

1. **Approve Tier 1-3 queue?** (Ken → Mohler → Begg)
2. **Parallel training on cluster?** (All 3 nodes simultaneously)
3. **Spurgeon corpus:** Fetch/prep in parallel or defer?
4. **Model access:** Confirm m4max qwen3:32b available for training?

---

_44.5M words. 20,577 sermons. 30 preachers/sources. Cluster ready._

_Soli Deo Gloria._
