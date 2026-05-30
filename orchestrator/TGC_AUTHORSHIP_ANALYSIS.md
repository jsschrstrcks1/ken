# The Gospel Coalition (TGC) Authorship Analysis

## TGC: A Multi-Author Ecosystem

**The Gospel Coalition is not a single preacher — it's a curated platform with 512 unique contributors.**

### TGC Statistics

| Metric | Value |
|--------|-------|
| **Total files** | 6,061 |
| **Unique authors** | 512 |
| **Average per author** | 11.8 articles |
| **Total words** | 4.69M |

### Top TGC Contributors (50+ articles each)

**Prolific Voices (100+ articles):**
1. Dick Lucas — 1,566 articles (25.8% of TGC)
2. Kent Hughes — 677 articles (11.2%)
3. D. A. Carson — 462 articles (7.6%)
4. Sinclair Ferguson — 296 articles (4.9%)
5. Steve Brown — 228 articles (3.8%)
6. Michael Haykin — 158 articles
7. Richard Coekin — 133 articles
8. Michael Horton — 129 articles
9. R. C. Sproul — 127 articles
10. Daniel Akin — 118 articles
11. Joel Beeke — 117 articles
12. Tom Schreiner — 104 articles
13. Phil Ryken — 104 articles
14. Iain Murray — 100 articles
15. Jerry Bridges — 100 articles

**Major Contributors (50-99 articles):**
16. John Frame — 77 articles
17. Carl Trueman — 72 articles
18. John Murray — 65 articles
19. Gerald Bray — 65 articles
20. Wayne Grudem — 62 articles
21. Sean Michael Lucas — 58 articles
22. RTS (Reformed Theological Seminary) — 58 articles
23. Paul Tripp — 57 articles
24. David Wells — 55 articles
25. G. K. Beale — 53 articles

**Plus 487 more with 1-50 articles each**

---

## TGC LoRA Strategy: Two Approaches

### Option A: Single TGC LoRA (Current)
- **Data:** All 6,061 articles, 4.69M words
- **Voice:** "Gospel Coalition consensus" (512 authors blended)
- **Result:** Reflects evangelical breadth, reformed-leaning
- **Strength:** Captures institutional voice + theological diversity
- **Weakness:** Individual voices diluted (Dick Lucas = 25% of corpus)

### Option B: Individual TGC Contributors as Separate LoRAs
- **Data:** Extract each author's articles from TGC separately
- **Voice:** Pure individual voices (Dick Lucas, Kent Hughes, D.A. Carson, etc.)
- **Result:** 512 potential individual LoRAs from TGC alone
- **Strength:** Preserves individual theological voice + overlap
- **Weakness:** Many would be very small (1-2 articles each)

### Option C: Tiered Approach (Recommended)
- **Tier 1 (100+ articles):** Individual LoRAs
  - Dick Lucas (1,566)
  - Kent Hughes (677)
  - D. A. Carson (462)
  - Sinclair Ferguson (296)
  - Steve Brown (228)
  
- **Tier 2 (20-99 articles):** Candidate for extraction (15-20 authors)
  
- **Tier 3 (1-19 articles):** Keep in TGC consensus LoRA

---

## Cross-Archive Representation

### Authors Who Appear in TGC + Archive

| Author | In TGC | In Archive | Total Words |
|--------|--------|-----------|-------------|
| **R.C. Sproul** | 127 | 548 | 0.49M + TGC |
| **Daniel Akin** | 118 | 1,200 | 2.09M + TGC |
| **Albert Mohler** | 36 | 3,449 | 12.49M + TGC |
| **John Frame** | 77 | — | TGC only |
| **D. A. Carson** | 462 | — | TGC only |
| **Dick Lucas** | 1,566 | — | TGC dominant voice |

---

## TftG (Together for the Gospel): Minimal Archive

**Status:** Only 24 podcast episode files

**Hosts found:**
- H. B. Charles, Jr. (Pastor to Pastor podcast)
- T. J. Tims (Pastor to Pastor podcast)

**Size:** 24 files, ~510 words (stubs only)

**Status:** Placeholder, awaiting expansion

---

## Recommendation: TGC LoRA Strategy

### Keep TGC as Single Consensus LoRA
- **Rationale:**
  1. **Institutional identity matters** — TGC's brand IS "gospel consensus"
  2. **Overlap already captured:** Authors like Mohler, Akin, Sproul appear separately too
  3. **Editorial curation:** TGC editorial process = part of the voice
  4. **Debate advantage:** TGC LoRA vs. Individual LoRAs = healthy theological tension

### Future: Extract Top 5-10 if Needed
- If you want pure Dick Lucas, Kent Hughes, D.A. Carson voices
- Can extract their TGC articles and combine with external sources
- But TGC consensus LoRA remains valuable as "evangelical reformed consensus"

---

## Implications for Your LoRA Ecosystem

### Current Plan (Recommended)
- **TGC LoRA:** Single consensus voice (6,061 articles, 4.69M words)
- **Individual LoRAs:** Already separate (Mohler, Akin, Sproul, etc.)
- **Debate mode:** Ken vs. Mohler vs. TGC (3-way theological conversation)

### Alternative: High-Granularity
- **512 potential LoRAs from TGC alone**
- **Complex routing:** Which author for this query?
- **Diminishing returns:** 500+ LoRAs with 1-2 articles each

---

## Final Answer

**How many authors in TGC? 512 unique contributors**

**How many in TftG? 2 hosts (minimal archive)**

**Recommendation: Keep TGC as one LoRA (consensus voice) + maintain individual separates**

---

_Soli Deo Gloria._
