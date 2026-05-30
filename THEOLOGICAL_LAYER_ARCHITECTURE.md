# Theological Layer Architecture — Confessions + Tensions

**Date:** 2026-05-30 13:56 EDT | **Status:** DESIGN | **Scope:** Reformed Baptist foundations

---

## The Confession Stack

### Primary Reformed Baptist Confessions

| Confession | Year | Scope | Reformed Baptist Position | Notes |
|------------|------|-------|---------------------------|-------|
| **1689 Baptist Confession** | 1689 | Core: soteriology, ecclesiology, baptism | Full endorsement | "The Baptist Heidelberg Confession" |
| **Baptist Faith & Message** | 1925 (revised 2000) | Broader evangelical, SBC | Downstream of 1689 | Includes non-Reformed voices |
| **Abstract of Principles** | 1858 | SBTS founding document | Reformed Baptist | Narrow, institutional |
| **Philadelphia Confession** | 1742 | Earlier Reformed Baptist | Historical precedent | 1689 in American context |
| **Heidelberg Catechism** | 1563 | Reformed (not baptist) | Partial alignment | On Trinity, predestination, ethics |
| **Westminster Standards** | 1647-48 | Presbyterian Reformed | ~90% alignment (except baptism) | Used by some Reformed Baptists |

### Secondary/Contextual Documents

- **London Confession of Faith** (1646, 1677) — Earlier Baptist confessions
- **Belgic Confession** (1561) — Dutch Reformed foundation
- **Canons of Dort** (1618-19) — Anti-Pelagian, pro-predestination
- **Ken's personal theology** (AGENTS.md, SOUL.md, sermons) — Individual refinement of 1689

---

## Layer Architecture: Confessions as Weights

```
Layer 0 (Foundation): Shared Axioms
├─ Sola Scriptura (all confessions agree)
├─ Trinity (all Reformed agree)
├─ Christ as God-man, mediator (core)
└─ Justification by faith (foundational)

Layer 1 (Confessional): 1689 specifics
├─ Believer's baptism (vs. infant baptism)
├─ Congregational polity
├─ Particular redemption
├─ God's sovereignty in salvation
└─ Authority: Scripture alone (not tradition)

Layer 2 (Institutional): Abstract of Principles
├─ SBTS-specific application
├─ Academic theological method
├─ Pastoral accountability structures
└─ Doctrinal boundaries for seminary

Layer 3 (Denominational): Baptist Faith & Message
├─ Broader SBC unity
├─ Evangelical accommodation
├─ Less strict on secondary issues
└─ Allows non-Reformed Calvinism

Layer 4 (Individual): Author voice
├─ Personal conviction depth
├─ Pastoral experience
├─ Sermon application style
├─ Rhetorical preference
└─ (Where tensions emerge)

Layer 5 (Domain): Application context
├─ Pastoral (care-focused)
├─ Academic (systematic)
├─ Devotional (heart-focused)
├─ Apologetic (defense-focused)
└─ Missional (outreach-focused)
```

---

## The Tension: Sproul + Paedobaptism

### The Problem

**Sproul's position:**
- Affirms 1689 soteriology (predestination, particular redemption, etc.)
- **REJECTS** believer's-only baptism (paedobaptism advocate)
- This violates Layer 1 (1689 core doctrine)

**When model invokes "Sproul":**
- Should it follow his actual paedobaptism position?
- Or constrain to 1689 confessional position?
- Or mark the contradiction explicitly?

### Solutions

#### Option A: Confessional Constraint (Strict)
```
Layer 1 (1689) HARD BOUNDARY
    ↓ (non-negotiable)
Layer 4 (Sproul voice)
    
Result: "Sproul" voice but ONLY on 1689-approved positions
Cost: Misrepresents actual Sproul (he held paedobaptism)
Benefit: Theologically consistent
```

#### Option B: Author Sovereignty (Loose)
```
Layer 4 (Sproul voice) DOMINANT
    ↓ (author's actual positions)
Layer 1 (1689) ADVISORY
    
Result: "Sproul" as he actually was (includes paedobaptism)
Cost: Model can teach non-1689 doctrine
Benefit: Historically accurate
```

#### Option C: Tension Encoding (Honest)
```
Layer 1: 1689 doctrine
Layer 4: Sproul voice
    ↓
Explicit marker: "TENSION: Sproul affirms 1689 soteriology 
                 but disagrees on baptism. Model should note the 
                 disagreement when arising."

Result: Transparent about where Sproul breaks from 1689
Cost: More complex training data
Benefit: Intellectually honest + educational
```

---

## Recommendation: Tension-Aware Layers

### Architecture for Ken's Ecosystem

```
SCRIPTURE LAYER (4,981 verse contexts)
    ↓ (authority source)
    
CONFESSION STACK (weighted):
├─ 1689 (weight: 1.0) — hard core
├─ Abstract of Principles (weight: 0.8) — institutional 
├─ Baptist Faith & Message (weight: 0.6) — broader
├─ Heidelberg Catechism (weight: 0.4) — Reformed shared
└─ Westminster Standards (weight: 0.3) — reference only

    ↓ (filtered through)
    
AUTHOR LAYER (author voice):
├─ Ken (100% 1689 aligned, speaks from it)
├─ Carson (95% 1689, minor academic nuances)
├─ Sproul (80% 1689, explicit paedobaptism difference)
├─ Begg (90% 1689, charismatic-open sympathies)
└─ [tension markers for each author]

    ↓ (applied in)
    
DOMAIN LAYER (context):
├─ Pastoral (emphasize soul-care)
├─ Academic (emphasize precision)
├─ Devotional (emphasize worship)
├─ Apologetic (emphasize defense)
└─ Missional (emphasize Gospel proclamation)
```

---

## Implementation: How to Encode Tensions

### Training Data Format

Instead of just text, include metadata:

```json
{
  "text": "By baptism, believers are united with Christ...",
  "author": "Sproul",
  "confessional_layer": "1689",
  "tension_marker": "paedobaptism",
  "tension_description": "Sproul affirms 1689 soteriology but practices infant baptism",
  "domain": "academic",
  "source": "Sproul-systematic-theology-chapter-5"
}
```

### Training Strategy

1. **Layer 0-1:** Train all authors on shared Scripture + 1689
2. **Layer 4:** Train individual author voice (including their tensions)
3. **Tension encoding:** When author disagrees with Layer 1, add explicit marker
4. **Layer 5:** Domain-specific fine-tuning

### Inference Time

When model generates from "Sproul" LoRA:
1. Load Scripture layer (foundation)
2. Load 1689 layer (confessional)
3. Load Sproul LoRA (individual)
4. When paedobaptism topic arises, note tension: "Sproul teaches X (1689) but practices Y (paedobaptism)"
5. Apply domain layer (e.g., "academic" → more precise, "pastoral" → more care-focused)

---

## Questions to Resolve

1. **Ken's position on tensions:**
   - Strict confessional boundary (1689 = hard constraint)?
   - Or honest representation of disagreements (even within Reformed Baptist)?

2. **Which confessions to encode:**
   - Just 1689 + Abstract?
   - Include Heidelberg/Westminster for context?
   - Include pre-1689 Baptist confessions (Philadelphia, London)?

3. **Tension handling default:**
   - Option A (Confessional Constraint): Safe, coherent
   - Option B (Author Sovereignty): Accurate, risky
   - Option C (Tension Encoding): Best but complex

4. **Sproul specifically:**
   - Train paedobaptism into Sproul LoRA?
   - Or exclude/constrain it?
   - Or mark it as "acknowledged but not endorsed"?

---

## Dependencies

Before implementing this:
1. Finalize Ken's position on tension handling
2. Decide which confessions are Layer 1 vs. reference
3. Map each author to their confessional alignment
4. Document Sproul-like tensions explicitly

---

_Theological architecture. Confessional fidelity. Honest disagreements._

_Soli Deo Gloria._
