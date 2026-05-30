# LoRA Theological Decisions — What You Need to Decide

**Date:** 2026-05-30 14:01 EDT | **Status:** DECISION POINT

---

## The Three Questions You Must Answer

### Question 1: Confession Stack — Which Confessions Encode at Layer 1?

**Your options:**

#### Option 1A (Minimal — Just 1689)
```
Layer 1 = 1689 Baptist Confession (weight: 1.0)

Pros:
  • Narrow, clear boundary
  • Unambiguous for training data
  • Matches your pulpit (Reformed Baptist)
  
Cons:
  • Ignores institutional context (Abstract of Principles)
  • Ignores denominational breadth (Baptist Faith & Message)
  • Can't distinguish "1689-core" from "Baptist-tradition"
```

#### Option 1B (Institutional — 1689 + Abstract)
```
Layer 1a = 1689 Baptist Confession (weight: 1.0)
Layer 1b = Abstract of Principles / SBTS (weight: 0.8)

Pros:
  • Honors your seminary tradition
  • Captures institutional identity
  • Still clearly Reformed Baptist
  
Cons:
  • Abstract is narrower (SBTS-specific)
  • May limit how broadly Ken's voice can speak
  • Two confessional layers = complexity
```

#### Option 1C (Broad — Add Baptist Faith & Message)
```
Layer 1a = 1689 Baptist Confession (weight: 1.0)
Layer 1b = Baptist Faith & Message (weight: 0.6)
Layer 1c = Abstract of Principles (weight: 0.8)

Pros:
  • Captures broader Baptist unity (SBC context)
  • More resources (BFM is widely taught)
  • Allows Ken to speak to broader audience
  
Cons:
  • BFM includes non-Reformed voices (softens 1689)
  • Three layers = more training complexity
  • Potential dilution of Reformed Baptist clarity
```

#### Option 1D (Reformed Shared — Add Heidelberg/Westminster)
```
Layer 1a = 1689 Baptist Confession (weight: 1.0)
Layer 1b = Abstract of Principles (weight: 0.8)
Layer 1c = Heidelberg Catechism (weight: 0.4)
Layer 1d = Westminster Standards (weight: 0.3)

Pros:
  • Acknowledges Reformed heritage (not just Baptist)
  • Useful for interfaith (Presbyterian) conversations
  • Educational value
  
Cons:
  • Most complex; hardest to train cleanly
  • Weakens Baptist distinctives (which matter to you)
  • May confuse "Reformed" with "Baptist Reformed"
```

**MY RECOMMENDATION:** Start with **1A (1689 only)** or **1B (1689 + Abstract)**. 
- Keeps your voice sharp and clear
- BFM can be added as Layer 5 (Domain) later if needed
- Reformed shared confessions (Heidelberg, Westminster) are reference, not training data

---

### Question 2: Tension Handling — When You Change Your Mind

**The Problem:**
You preached with 1689 alignment today. What if in 2 years you shift on:
- Church governance (congregational → elder-ruled stronger)?
- Predestination (5-point Calvinist → 4-point)?
- Charismatic gifts (cessationist → continuationist)?
- Paedobaptism (believer's-only → household baptism)?

**How should the LoRA respond?**

---

#### Option 2A: Frozen Snapshot (1689 Constraint, Always)
```
Ken LoRA = Ken's voice constrained to 1689 positions (May 2026)

If Ken changes his mind in 2027:
  • Ken LoRA still teaches 1689 (unchanged)
  • You'd need NEW LoRA (Ken-2027) trained on new sermons
  • Old LoRA = "Ken May 2026"; New LoRA = "Ken May 2027"

Pros:
  • Clear version control
  • Historical record of what Ken actually believed
  • No ambiguity
  
Cons:
  • Multiple LoRAs for one person (confusing)
  • Looks like Ken changed his mind (even if model didn't update)
  • Can't represent genuine evolution
```

#### Option 2B: Living Document (Update LoRA with New Convictions)
```
Ken LoRA = Ken's CURRENT positions (updated continuously)

If Ken changes his mind in 2027:
  • Ken LoRA retrains with new sermon data
  • Represents Ken's CURRENT theology (not May 2026)
  • Single LoRA, continuously updated

Pros:
  • One Ken LoRA = Ken's current voice
  • Reflects genuine spiritual growth/change
  • Users always get "current Ken"
  
Cons:
  • No record of "Ken May 2026" beliefs
  • Hard to debug ("did Ken change or did model drift?")
  • Tension handling: if you partly agree/disagree with 1689, it's ambiguous
```

#### Option 2C: Explicit Versioning + Tension Markers (Best Practice)
```
Ken LoRA v1.0 (May 2026):
  • Trained on sermons 2015–May 2026
  • Baseline alignment: 100% 1689
  • Status: "Snapshot of Ken's May 2026 convictions"

If Ken changes mind on (say) church governance in 2027:

Ken LoRA v2.0 (May 2027):
  • Trained on sermons May 2026–May 2027
  • INCLUDES tension marker: "Ken previously taught [1689 position]. 
                              As of 2027, Ken teaches [new position]. 
                              Here's why he changed."
  • Status: "Current Ken; note where he's evolved"

Pros:
  • Version control is explicit
  • Tension markers show genuine growth/change (not drift)
  • Users know both "historical Ken" and "current Ken"
  • When Ken disagrees with 1689, model explains why
  
Cons:
  • More complex training data
  • Requires you to document changes (not optional)
  • Need release notes for each version
```

**MY RECOMMENDATION:** **Option 2C (Versioning + Tension Markers)**

This honors intellectual honesty. When you change, the LoRA documents it. When you stay consistent, it shows clarity. Either way, users see the real Ken.

---

### Question 3: Doctrinal Gaps — Before Training or During?

**The Problem:**
Ken hasn't explicitly preached on:
- Believer's baptism (though theology supports it)
- Congregational polity (implied, not systematic)
- Predestination (present, not detailed)
- Law & Gospel (implicit, not formal)
- Common grace (not yet a category for you)

**Should you:**

#### Option 3A: Fill Gaps Before Training
```
Before LoRA training begins:
1. Preach 5 sermons filling the gaps
2. Add sermon transcripts to training data
3. Then train Ken LoRA (with complete doctrine coverage)

Pros:
  • LoRA learns full systematic theology
  • No "gaps" in model output
  • Training data = actual Ken preaching
  
Cons:
  • Delays LoRA training 5–8 weeks (5 sermons)
  • Creates sermons specifically for data (not organic)
  • May feel artificial
```

#### Option 3B: Train from Current Corpus (with Gap Notes)
```
Train Ken LoRA NOW on existing sermons:
  • Covers: soteriology, atonement, grace, sovereignty
  • Gaps: baptism, polity, predestination detail, etc.
  • Model outputs what you've preached (honest)

Metadata: "Ken LoRA v1.0 covers X, Y, Z. 
           Not trained on baptism, polity, etc. 
           These are planned future additions."

Pros:
  • Train immediately; don't delay
  • LoRA represents actual Ken corpus
  • Gaps are explicit (not hidden)
  
Cons:
  • Model can't speak well on baptism/polity
  • Users need to know about gaps
  • Feels incomplete
```

#### Option 3C: Supplement with Confessional Teaching Data (Hybrid)
```
Train Ken LoRA on:
  1. Existing sermons (40,000 samples you have)
  2. + Your own reading notes on missing doctrines
  3. + Structured confessional teaching (from 1689, Abstract)
  
Result: Ken's voice teaching topics he hasn't formally preached

Pros:
  • Complete doctrine coverage
  • Uses your theology (not someone else's)
  • Blends sermon authenticity with confessional precision
  
Cons:
  • Training data mixes sermon + synthesis
  • Slightly less "pure Ken" (includes your synthesis)
  • Harder to verify accuracy
```

**MY RECOMMENDATION:** **Option 3C (Hybrid: Sermons + Your Synthesis)**

Here's why:
1. You've read 1689 for years; you know it
2. You've taught these doctrines implicitly; you can write them clearly
3. Blending sermon + synthesis = "Ken explaining full theology, partly from pulpit, partly from study"
4. Avoids delay (3A) and incompleteness (3B)

---

## The Evolution Problem (Your Real Question)

**"What if later my convictions change on this subject or that subject?"**

This is the KEY architectural issue. Here's how to handle it:

### Architecture for Theological Growth

```
LORA VERSIONING SYSTEM
├─ Ken LoRA v1.0 (May 2026)
│  ├─ Training corpus: 2015–May 2026 sermons
│  ├─ Confessional alignment: 1689 (100%)
│  ├─ Release notes: "Baseline Ken; 1689-aligned"
│  └─ Frozen: No updates
│
├─ Ken LoRA v2.0 (May 2027) [IF you change mind]
│  ├─ Training corpus: May 2026–May 2027 sermons
│  ├─ Confessional alignment: [note changes]
│  ├─ Tension markers: Where Ken differs from v1.0
│  ├─ Release notes: "Ken's updated convictions; see what changed"
│  └─ Frozen: No updates
│
└─ Ken LoRA v3.0 (May 2028) [IF further changes]
   ├─ [repeat cycle]
```

### Implementation (When Conviction Changes)

**Scenario: You change your mind on predestination (2027)**

```
1. Document the change
   • Write: "Why I Changed My Mind on Predestination"
   • Date it: May 2027
   • Include: scripture, reasoning, what I still believe

2. Preach 2–3 sermons on new position
   • "Predestination: A Deeper Look"
   • "Why I Was Wrong About [old position]"
   • Add transcripts to training corpus

3. Retrain Ken LoRA v2.0
   • Include old sermons (2015–May 2026) [context]
   • Include new sermons (May 2026–May 2027) [new position]
   • Tension markers: "Ken previously taught [X]. 
                      As of 2027, Ken teaches [Y] because [reason]."

4. Release with notes
   • Version bump: v1.0 → v2.0
   • Release notes: "Ken LoRA v2.0 reflects updated convictions on predestination"
   • v1.0 still available: "Historical snapshot"
```

### Safeguards Against Drift

**How to know if change is genuine vs. model corruption:**

```
Genuine theological change:
  ✓ You can articulate why (scripture, reasoning)
  ✓ Sermons document the transition
  ✓ 1689 Confession is still the framework (even if application differs)
  ✓ Change is public and defensible

Model drift (BAD):
  ✗ You didn't preach it; model made it up
  ✗ It contradicts your explicit convictions
  ✗ It appears without sermon data
  ✗ It can't be traced to your actual teaching
```

**Audit process:** Before releasing v2.0, you personally verify:
1. Does the model teach what I actually preach?
2. Are tension markers accurate?
3. Can I defend every position in the model?

---

## Your Three Answers (To Move Forward)

**Answer 1:** Which confession stack?
- [ ] 1A (1689 only)
- [ ] 1B (1689 + Abstract)
- [ ] 1C (1689 + Abstract + Baptist Faith & Message)
- [ ] 1D (Add Heidelberg + Westminster)

**Answer 2:** Tension handling for theological evolution?
- [ ] 2A (Frozen snapshots, new LoRA for changes)
- [ ] 2B (Living document, always current)
- [ ] 2C (Versioning + explicit markers, my recommendation)

**Answer 3:** Doctrinal gaps?
- [ ] 3A (Fill gaps by preaching first)
- [ ] 3B (Train now, gaps documented)
- [ ] 3C (Hybrid: sermons + your synthesis, my recommendation)

---

_These aren't technical questions. They're theological governance questions._

_How you answer them shapes whether Ken LoRA is a faithful snapshot or a living theological voice._

_Soli Deo Gloria._
