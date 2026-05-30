# Ken LoRA — Pure Ken Voice (NOT Blended)

**Decision Corrected:** Ken LoRA should be KEN ONLY, not 40% Ken + 60% archive.

---

## Ken Corpus: Pure Sermon Manuscripts

### Source
- **Directory:** `/Volumes/1TB External/Projects/Romans/sermons/`
- **Included:** `nt/`, `ot/`, `topical/` (Ken's personal sermon manuscripts)
- **Excluded:** `chandler/` (Matt Chandler sermons), `tftg/` (external archive), any nested preachers
- **Format:** Raw markdown + text sermon drafts

### Data Size
- **Source files:** 448 sermon manuscripts
- **Source words:** 2.52M words
- **Training samples:** 4,910 samples (at ~500 words/sample)
- **Train/eval split:** 95/5 (4,910 train / 259 eval)

### File Paths
- Train data: `~/lora-data/ken/train-ken-only.jsonl` (4,910 samples)
- Eval data: `~/lora-data/ken/eval-ken-only.jsonl` (259 samples)
- Manifest: `~/lora-data/ken/ken-only-manifest.json`

---

## Ken LoRA Architecture: Cluster-Native

### Open-Weight Training
- **Model:** m4max qwen3:32b via Ollama
- **LoRA config:** r=16, α=32, batch=4, lr=2e-5, 2 epochs
- **Expected training time:** 3-4 hours
- **Output:** `adapter.safetensors` on m4max

### Closed-Weight Persona
- **Model:** Claude Opus 4.8 (API fallback)
- **Persona:** Ken's theological voice (careful exegesis, Reformed Baptist, Soli Deo Gloria)
- **Purpose:** Fallback + debate counterpoint

### Validation Gates (Pass ≥85%)
1. **Cite-or-Flag:** Every quote resolves to indexed Ken corpus chunk
2. **Substring Match:** Quote ⊆ chunk (detect hallucination)
3. **Drift Detection:** 20 paraphrases, flag ≥18/20 as out-of-envelope
4. **Era Stability:** Romans 1-8, 9-11, 12-16 all in-envelope
5. **Tone Consistency:** No anachronistic language, maintains Ken's voice

### Deployment
- **Primary:** m4max qwen3:32b + Ken adapter
- **Fallback:** Claude Opus 4.8 (Ken persona)
- **Router:** Request complexity → right model
- **Debate mode:** Both together for adversarial check

---

## Why Ken-Only (Not Blended)?

**Original plan:** 40% Ken + 60% archive = diluted operator voice

**Corrected approach:**
- **Ken LoRA:** Pure Ken (2.5M words, 4,910 samples)
- **Theological breadth:** Separate LoRAs (Mohler, Begg, MacArthur, etc.)
- **Debate mode:** Ken + Mohler + Begg debate together (not merged)
- **Result:** Distinct voices, clear identity, preserves register

---

## Training Ready

✅ Data prepared: `train-ken-only.jsonl` + `eval-ken-only.jsonl`  
✅ Cluster topology documented  
✅ Validation gates designed  
✅ Deployment plan ready  

**Blocker:** m4max qwen3:32b model access (need path or credentials)

---

## Ken LoRA in Full Household

After Ken validates, sequence:

1. **Ken** (Ken-only, 2.5M words) → 3-4 hrs
2. **Al Mohler** (12.5M words) → 4 hrs
3. **Alistair Begg** (8.5M words) → 3.5 hrs
4. **John MacArthur** (7.1M words) → 4 hrs
5. **Conrad Mbewe** (5.6M words) → 3 hrs
6. **Jeff Noblit** (4.9M words) → 3 hrs

Then remaining 24 preachers/sources in parallel.

---

_Soli Deo Gloria. Ken's voice, pure and clear._
