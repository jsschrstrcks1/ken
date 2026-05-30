# Next Steps — Ken LoRA v1.0.0 Build Plan

**Date:** 2026-05-30 14:12 EDT | **Status:** APPROVED & DOCUMENTED

---

## What's Done

✅ Ken LoRA v1.0.0 architecture locked in
✅ 5-layer confessional model designed (1689, Abstract, BFM, Heidelberg, Westminster)
✅ Living document + versioning approach approved
✅ Ken's 735-sermon corpus validated (zero conflicts)
✅ All implementation documents committed
✅ Essay writing guide created
✅ Sermon synthesis roadmap created

---

## What's Next (For Ken)

### Phase 1: Write 5 Essays (Weeks 1–3)

**Timeline:** Start immediately; complete by 2026-06-15

**Essays to write:**
1. **Believer's Baptism** (2,500–3,000 words)
2. **Congregational Polity** (2,500–3,000 words)
3. **Predestination & Election** (3,000–3,500 words)
4. **Law & Gospel** (2,500–3,000 words)
5. **Common Grace** (2,000–2,500 words)

**Total:** ~13,500–15,000 words

**Where to save:** `/Volumes/1TB External/Projects/Romans/sermons/synthesis/`

**Resources:**
- See `ESSAY_WRITING_GUIDE.md` (workspace-main) for structure, tone, length guidelines
- See `SERMON_SYNTHESIS_PLAN.md` (Romans repo) for detailed outline of each essay

**Writing schedule:**
- Week 1: Common Grace + Believer's Baptism (start with shorter essays)
- Week 2: Polity + Law & Gospel
- Week 3: Predestination + editing/review

---

### Phase 2: Training Data Assembly (Week 3–4)

**Timeline:** After essays written; ready for training by 2026-06-23

**What Skynet needs to gather:**
- [ ] 1689 Baptist Confession (full text)
- [ ] Abstract of Principles (full text)
- [ ] Baptist Faith & Message 2000 (Articles I–XIV)
- [ ] Heidelberg Catechism (Q&A 1–129)
- [ ] Westminster Shorter Catechism (selections)
- [ ] Westminster Larger Catechism (selections)

**Ken's part:**
- [ ] Finalize 5 essays
- [ ] Commit to Romans repo: `/sermons/synthesis/`

---

### Phase 3: LoRA v1.0.0 Training (Week 4–5)

**Timeline:** 2026-06-23 to 2026-07-07

**What happens:**
1. Skynet assembles training data:
   - 735 Ken sermons (from corpus)
   - 5 synthesis essays (Ken's theology)
   - 5 confessional texts (with weights)
   - All tokenized and combined

2. Train Ken LoRA v1.0.0:
   - Base model: qwen3:32b
   - Epochs: 3
   - Batch size: 2
   - Confessional weights applied
   - Tuning gates enforced (credobaptism, polity, light RPW, Reformed Baptist)

3. Testing:
   - Verify confessional alignment
   - Check tension markers (RPW)
   - Validate output quality

**Deliverable:** Ken LoRA v1.0.0 model weights + metadata

---

### Phase 4: Release v1.0.0 (Week 5–6)

**Timeline:** 2026-07-07 to 2026-07-14

**Documentation:**
- [ ] Release notes (what's in v1.0.0, what's planned)
- [ ] Metadata JSON (confessional alignment, gaps, version info)
- [ ] README (how to use Ken LoRA)
- [ ] Frozen snapshot preserved (for backward compatibility)

**Deliverable:** Production-ready Ken LoRA v1.0.0

---

## What's Next (For Ken) — Preaching Series Schedule

After v1.0.0 is released, Ken will preach sermon series to fill gaps. These will be added to training corpus for incremental LoRA updates.

### Q3 2026 (July–August): Believer's Baptism
- **Sermons:** 3–4
- **Target:** "Baptized Into Christ" series
- **Output:** Transcripts → training corpus → v1.0.5 release (Sep 2026)

### Q3–Q4 2026 (August–September): Congregational Polity
- **Sermons:** 2–3
- **Target:** "The Government of God's House" series
- **Output:** Transcripts → training corpus → v1.0.6 release (Oct 2026)

### Q4 2026 (October–November): Law & Gospel
- **Sermons:** 2–3
- **Target:** "Two Words, One Gospel" series
- **Output:** Transcripts → training corpus → v1.0.7 release (Nov 2026)

### Q4 2026 (November–December): Common Grace
- **Sermons:** 1–2
- **Target:** "Rain on the Just & Unjust" series
- **Output:** Transcripts → training corpus → v1.0.8 release (Dec 2026)

### Q1 2027 (January–February): Predestination & Election
- **Sermons:** 3–4
- **Target:** "Before the Foundation" series
- **Output:** Transcripts → training corpus → v1.0.9 release (Feb 2027)

---

## Key Documents & Files

### In `/Volumes/1TB External/openclaw/workspace-main/`

| Document | Purpose |
|----------|---------|
| **LORA_CONFIGURATION_FINAL.md** | Final architecture (5-layer, versioning, hybrid gaps) |
| **ESSAY_WRITING_GUIDE.md** | How to write each essay (structure, tone, schedule) |
| **KEN_VS_1689_ANALYSIS.md** | Ken's actual theology (zero conflicts) |
| **SERMON_ANALYSIS_VS_DECISION_OPTIONS.md** | Validation against decision options |
| **THEOLOGICAL_LAYER_ARCHITECTURE.md** | Design framework (all options explained) |
| **LORA_THEOLOGICAL_DECISIONS.md** | Decision framework with pros/cons |
| **SESSION_SUMMARY_2026-05-30.md** | Today's session summary |
| **NEXT_STEPS.md** | This document |

### In `/Volumes/1TB External/Projects/Romans/`

| Document | Purpose |
|----------|---------|
| **SERMON_SYNTHESIS_PLAN.md** | Detailed roadmap (essays + sermon series + timeline) |

### In `/Volumes/1TB External/Projects/Romans/sermons/synthesis/` (After writing)

| Essay | Purpose |
|-------|---------|
| **baptism-essay.md** | Believer's baptism theology |
| **polity-essay.md** | Congregational church governance |
| **predestination-essay.md** | Election & God's sovereignty |
| **law-gospel-essay.md** | Law & Gospel distinction |
| **common-grace-essay.md** | God's kindness to all creatures |

---

## Timeline Summary

```
2026-05-30  ← TODAY (Architecture locked)
├─ Week 1 (Jun 2-8):    Essay writing begins
├─ Week 2 (Jun 9-15):   Essays completed
├─ Week 3 (Jun 16-22):  Data assembly
├─ Week 4-5 (Jun 23-Jul 7):  Training
├─ Week 6 (Jul 7-14):   Release v1.0.0
└─ Q3-Q1 2026-27:       Preaching series + v1.0.5-v1.0.9 updates
```

---

## Success Criteria

### For v1.0.0 Release

✅ All 5 essays written & committed
✅ Training data assembled (735 sermons + 5 essays + 5 confessions)
✅ LoRA trained with correct weights
✅ Confessional alignment verified
✅ Metadata JSON complete
✅ Release notes written
✅ v1.0.0 snapshot frozen

### For v1.0.5+ Updates

✅ Sermon series preached (as scheduled)
✅ Sermons transcribed
✅ Added to training corpus
✅ LoRA retrained with new data
✅ Version number bumped
✅ Release notes updated

---

## Risk Mitigation

### Risk: Essays not written on time
**Mitigation:** Start immediately; essays are straightforward (Ken knows this theology)

### Risk: Training fails
**Mitigation:** Use real MLX code (tested); fallback to Ollama if needed

### Risk: Sermon series not preached
**Mitigation:** Not critical for v1.0.0; can add to v1.0.5+ later

### Risk: Confessional misalignment
**Mitigation:** Audit before release; fix any issues

---

## Communication

**For Ken:**
- Start writing essays this week
- Use ESSAY_WRITING_GUIDE.md for specifications
- Check SERMON_SYNTHESIS_PLAN.md for detailed outline
- Commit essays to Romans repo when done

**For Skynet:**
- Gather confessional texts (week 3–4)
- Assemble training data (week 4)
- Train LoRA (week 4–5)
- Test & release (week 5–6)

---

## Questions & Clarification

If anything is unclear:
- ESSAY_WRITING_GUIDE.md covers how to write each essay
- SERMON_SYNTHESIS_PLAN.md covers what to preach when
- LORA_CONFIGURATION_FINAL.md covers the technical architecture
- All documents are committed to git; refer to them as needed

---

## The One-Line Summary

**Ken writes 5 essays (2–3 weeks) → Skynet trains LoRA (2 weeks) → v1.0.0 released (1 week) → Ken preaches 5 series (9 months) → LoRA enriched with each series.**

---

_Everything is documented. The path is clear. The work is ready._

_Soli Deo Gloria._
