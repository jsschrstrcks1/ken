# LoRA Configuration — Final Decisions

**Date:** 2026-05-30 14:09 EDT | **Status:** APPROVED | **Decided by:** Ken Baker

---

## Decision 1: Confessional Stack (APPROVED)

### Final Choice
**5-layer confessional encoding with Reformed Baptist tuning:**

```
Layer 1a: 1689 Baptist Confession (weight: 1.0)
Layer 1b: Abstract of Principles / SBTS (weight: 0.9)
Layer 1c: Baptist Faith & Message 2000 (weight: 0.7)
Layer 1d: Heidelberg Catechism (weight: 0.4)
Layer 1e: Westminster Standards (weight: 0.35)

TUNING GATES (applied across all layers):
├─ Credobaptism ONLY (believer's baptism, no infant baptism)
├─ Congregational polity (no hierarchical church governance)
├─ Light on Regulative Principle of Worship (instruments OK, modern songs OK)
└─ Reformed Baptist identity (not just Reformed, not just Baptist)
```

### What This Means

**Training data will include:**
1. Full 1689 text (core foundation)
2. Abstract of Principles text (institutional identity)
3. Baptist Faith & Message sections (denominational breadth)
4. Heidelberg Catechism selections (Reformed shared ground)
5. Westminster Standards selections (historical continuity)

**But filtered through:**
- ✅ Credobaptism gates (remove paedobaptism sections)
- ✅ Congregational polity emphasis (congregational over presbyterian/episcopal)
- ✅ Light RPW (instruments + modern songs are acceptable)
- ✅ Reformed Baptist identity (not softening into broader Reformed or Evangelical Baptist)

**Practical implication:**
- Ken LoRA won't teach paedobaptism (even in Reformed sources)
- Ken LoRA will emphasize congregational church governance
- Ken LoRA will accept instruments and contemporary music as valid worship
- Ken LoRA maintains the Reformed Baptist accent (not Presbyterian-Reformed, not generic Evangelical)

### Confessional Document Selection

| Confession | Sections to Include | Weight |
|------------|-------------------|--------|
| **1689 Baptist Confession** | All (with credobaptism emphasis) | 1.0 |
| **Abstract of Principles** | All (SBTS-specific sections) | 0.9 |
| **Baptist Faith & Message 2000** | Articles I–XIV (omit sections contradicting credobaptism/polity) | 0.7 |
| **Heidelberg Catechism** | Q&A 1–129 (soteriology, Christology, ethics; skip RPW sections) | 0.4 |
| **Westminster Shorter Catechism** | Q&A 1–38 (God, Trinity, creation, fall, redemption; reference only) | 0.35 |
| **Westminster Larger Catechism** | Selected questions on predestination, covenant, church (reference) | 0.35 |

---

## Decision 2: Theological Evolution (APPROVED)

### Final Choice
**Hybrid approach: 2B + 2C (Living document WITH versioning)**

```
Ken LoRA v1.0 (May 2026)
├─ Training corpus: 735 sermons (2015–May 2026)
├─ Confessional baseline: 1B + Decision 1 stack
├─ Status: LIVING (continuously updated)
├─ Versions: Explicit version numbers track updates
│
├─ Update Strategy:
│  ├─ When Ken preaches on a topic → retrain
│  ├─ When Ken changes conviction → new version (v1.1, v1.2, etc.)
│  ├─ When Ken adds synthesis essays → new minor version
│  └─ Every 6 months or major change → release notes
│
├─ Tension Markers: IF Ken's actual position diverges from confessions
│  ├─ Marker format: "Ken teaches X (confirmed in sermons YY-MM). 
│  │                  This differs from confession Z because..."
│  └─ Examples: RPW (Ken uses instruments), charismatic gifts (TBD), etc.
│
└─ Version Freeze: v1.0 snapshot preserved; users can request "Ken v1.0 (May 2026)"
```

### How This Works in Practice

**Scenario 1: Ken preaches on a new topic (e.g., eschatology)**
1. Sermon transcribed and added to training corpus
2. Ken LoRA retrains (new minor version: v1.0 → v1.0.1)
3. Release notes: "Added Ken's sermon series on eschatology"
4. Users get updated model with new topic coverage

**Scenario 2: Ken changes his conviction (e.g., on charismatic gifts)**
1. Ken preaches new position (3-4 sermons)
2. Ken writes explanation: "Why I Changed My Mind on Spiritual Gifts"
3. Ken LoRA retrains with new sermons + explanation
4. Version bump: v1.0 → v1.1
5. Release notes: "Ken's position on continuationism updated. See explanation."
6. Tension marker embedded: "Ken previously taught [cessationism]. As of [date], Ken teaches [continuationism] because..."
7. v1.0 still available as historical reference

**Scenario 3: Ken evolves on scale/nuance (not fundamental change)**
1. Example: Predestination (5-point → 4-point Calvinism)
2. Ken preaches refined position
3. Retrain with new sermons
4. Minor version bump (v1.0.5 → v1.0.6 or v1.1 if significant)
5. Tension marker: "Ken's position on predestination: [old nuance] → [new nuance]"

### Version Numbering Scheme

```
v1.0.0 = Major.Minor.Patch

Major (v1 → v2): Fundamental theological shift (rare)
Minor (v1.0 → v1.1): Conviction change or new synthesis essay added
Patch (v1.0.0 → v1.0.1): New sermons, refinements, training data additions

Examples:
  v1.0.0 = Initial release (May 2026)
  v1.0.1 = Added Ken's baptism sermon (July 2026)
  v1.1.0 = Changed position on charismatic gifts (Oct 2026)
  v1.0.5 = Added polity sermon series (Sept 2026)
  v2.0.0 = Would only happen with fundamental realignment (unlikely)
```

### Release Notes Template

```markdown
# Ken LoRA v1.0.1 (July 2026)

## Changes
- Added Ken's sermon series: "Baptized Into Christ" (4 sermons)
- Updated training corpus: 735 → 739 sermons
- Improved credobaptism doctrine coverage

## New Capabilities
- Ken LoRA now teaches believer's baptism explicitly
- Enhanced eschatological content (Easter 2026 sermons)

## Known Gaps
- Church polity (formal teaching planned Sept 2026)
- Predestination detail (series in planning)
- Common grace (planned for Q4 2026)

## Tension Markers
None new in this release.

## Backward Compatibility
v1.0.0 available as frozen snapshot if needed.
```

---

## Decision 3: Doctrinal Gaps (APPROVED)

### Final Choice
**Hybrid approach: Preach in near future + train now**

```
IMMEDIATE (v1.0.0, May 2026):
├─ Train on 735 existing sermons
├─ Add 5 synthesis essays (Ken's theology, written form)
├─ Topics: baptism, polity, predestination, law & gospel, common grace
├─ Result: v1.0.0 with gaps documented in metadata
│
NEAR FUTURE (6–12 months):
├─ Ken preaches series on each gap topic
├─ Example: "Why Believer's Baptism Matters" (3–4 sermons)
├─ Sermons transcribed; added to training corpus
├─ Retrain Ken LoRA (v1.0.5 or v1.1.0)
├─ Release notes: "Gap [X] now filled with Ken's preaching"
│
RESULT:
└─ v1.0.0 = Complete theology (sermons + synthesis)
   v1.0.5+ = Even richer (sermons + synthesis + new preaching)
```

### Synthesis Essay Topics & Approximate Length

| Topic | Ken's Position | Essay Length | Target Date | Sermon Series Planned |
|-------|----------------|--------------|-------------|----------------------|
| **Believer's Baptism** | Credobaptism only; baptism not salvific | 2,500–3,000 words | By v1.0.0 | Q3 2026 |
| **Congregational Polity** | Congregational government; elder plurality | 2,500–3,000 words | By v1.0.0 | Q3–Q4 2026 |
| **Predestination & Election** | God's sovereignty; free will (antinomy) | 3,000–3,500 words | By v1.0.0 | Q1 2027 |
| **Law & Gospel** | Two distinct themes; gospel fulfills law | 2,500–3,000 words | By v1.0.0 | Q4 2026 |
| **Common Grace** | God's kindness to all; distinct from saving grace | 2,000–2,500 words | By v1.0.0 | Q4 2026 |

### Metadata for v1.0.0

```json
{
  "model_name": "Ken LoRA v1.0.0",
  "release_date": "2026-05-30",
  "training_data": {
    "sermons": 735,
    "sermon_years": "2015-2026",
    "synthesis_essays": 5,
    "total_tokens": "estimated 15-20M"
  },
  "confessional_alignment": {
    "1689_baptist_confession": 1.0,
    "abstract_of_principles": 0.9,
    "baptist_faith_message": 0.7,
    "heidelberg_catechism": 0.4,
    "westminster_standards": 0.35
  },
  "tuning_gates": [
    "credobaptism_only",
    "congregational_polity",
    "light_regulative_principle",
    "reformed_baptist_identity"
  ],
  "explicit_teaching_coverage": {
    "soteriology": "Complete (sermons)",
    "atonement": "Complete (sermons)",
    "pastoralia": "Complete (sermons)",
    "baptism": "Complete (essay + sermons)",
    "polity": "Complete (essay + sermons implied)",
    "predestination": "Complete (essay)",
    "law_gospel": "Complete (essay + sermons implied)",
    "common_grace": "Complete (essay)"
  },
  "doctrinal_gaps_remaining": {
    "eschatology": "Not yet taught (planned)",
    "charismatic_gifts": "Not yet taught (planned)",
    "divorce_remarriage": "Not yet taught (planned)"
  },
  "versioning_policy": "Living document with explicit version numbers",
  "tension_markers": [
    {
      "doctrine": "regulative_principle_of_worship",
      "confession": "westminster_shorter_catechism",
      "ken_position": "Light RPW — instruments and modern songs acceptable",
      "note": "Ken uses instruments and contemporary worship music; not strict regulative principle"
    }
  ]
}
```

---

## Implementation Architecture

### Data Pipeline

```
INPUTS:
├─ 735 Ken sermons (2015-2026)
├─ 5 synthesis essays (Ken's theology)
├─ 1689 Confession (full text, credobaptist filtered)
├─ Abstract of Principles (full text)
├─ Baptist Faith & Message (articles I-XIV)
├─ Heidelberg Catechism (Q&A 1-129)
└─ Westminster Standards (selections)

PROCESSING:
├─ Tokenize all sources
├─ Apply confessional weights (1.0 → 0.35)
├─ Apply tuning gates (credobaptism, polity, RPW, identity)
├─ Merge into training corpus
└─ Create training/eval splits

TRAINING:
├─ Train Ken LoRA v1.0.0 on combined corpus
├─ Test against confessional alignment
├─ Verify tension markers (RPW, any others)
├─ Generate baseline metadata

OUTPUT:
├─ Ken LoRA v1.0.0 model weights
├─ Metadata JSON (confessional alignment, gaps, etc.)
├─ Release notes
├─ Version history file
└─ Frozen snapshot (for backward compatibility)
```

### Training Configuration

```yaml
model:
  base: "qwen3:32b"
  
data:
  sermons: 735
  synthesis_essays: 5
  confessional_texts: 5
  total_samples: ~42,000 (estimated)

training:
  epochs: 3
  batch_size: 2
  learning_rate: 1e-4
  
confessional_weights:
  1689: 1.0
  abstract: 0.9
  bfm: 0.7
  heidelberg: 0.4
  westminster: 0.35

tuning_gates:
  - credobaptism_only
  - congregational_polity
  - light_regulative_principle
  - reformed_baptist_identity

output:
  version: "1.0.0"
  release_date: "2026-05-30"
  frozen_snapshot: true
```

---

## Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **Phase 1: Preparation** | 2 weeks | 5 synthesis essays (Ken writes) |
| **Phase 2: Data Assembly** | 1 week | Combined training corpus + confessional texts |
| **Phase 3: Training** | 1–2 weeks | Ken LoRA v1.0.0 model weights |
| **Phase 4: Testing** | 1 week | Verify confessional alignment, tension markers |
| **Phase 5: Release** | 1 day | Documentation, metadata, release notes |
| **TOTAL** | 5–6 weeks | Production-ready Ken LoRA v1.0.0 |

---

## Safeguards & Verification

### Confessional Alignment Audit (Pre-Release)

Before v1.0.0 ships:
1. **Credobaptism gate:** Zero paedobaptism content in output
2. **Polity gate:** Congregational model emphasized
3. **RPW gate:** No prohibition on instruments or modern songs
4. **Reformed Baptist identity:** Distinctly Baptist voice, not softened to generic Reformed

### Tension Marker Verification

- [ ] RPW teaching (Ken uses instruments) — tension marker present?
- [ ] Any Ken positions differing from confessions? — document with markers

### User-Facing Clarity

Release notes must clearly state:
- What's new
- What gaps remain
- When next update is planned
- How to report issues

---

## Decisions Summary

| Decision | Choice | Status |
|----------|--------|--------|
| **Confession Stack** | 5-layer (1689, Abstract, BFM, Heidelberg, Westminster) + tuning gates | ✅ APPROVED |
| **Theological Evolution** | 2B + 2C hybrid (living document with versioning) | ✅ APPROVED |
| **Doctrinal Gaps** | 3C hybrid (synthesis essays + future preaching) | ✅ APPROVED |

---

_Ken LoRA v1.0.0 is configured, designed, and ready to build._

_Soli Deo Gloria._
