# Institutional Theological Content → LoRA Mapping

**How seminary chapels, Panopto recordings, and theological articles feed into LoRA training data**

---

## Seminary Chapel Services

### SEBTS Chapel → Multiple LoRAs

**SEBTS Chapel feeds (sebts.edu/chapel):**
- **Danny Akin** (President) → Danny Akin LoRA + SEBTS Chapel LoRA
- **Gregg Allison** (Faculty) → Gregg Allison candidate LoRA
- **Owen Strachan** (Faculty) → Owen Strachan candidate LoRA
- **Guest speakers** → Individual LoRAs (if speaker identified)

**Process:**
1. Discover chapel services (video + transcript)
2. Extract speaker name from metadata
3. Route to appropriate LoRA (Danny Akin gets chapel + archive sermons)
4. Include in SEBTS Chapel LoRA (institutional voice)

### SBTS Chapel → Multiple LoRAs

**SBTS Chapel feeds (sbts.edu/chapel):**
- **Albert Mohler** (President) → Al Mohler LoRA + SBTS Chapel LoRA
- **Tom Schreiner** (Faculty) → Tom Schreiner candidate LoRA
- **Jim Hamilton** (Faculty) → Jim Hamilton candidate LoRA
- **Guest speakers** → Individual LoRAs

### NOBTS Chapel → Multiple LoRAs

**NOBTS Chapel feeds (nobts.edu/chapel):**
- **Chuck Kelley** (President) → Chuck Kelley candidate LoRA
- **Tom Nettles** (Faculty) → Tom Nettles candidate LoRA
- **Other faculty & guests** → Individual LoRAs

---

## Panopto Lecture Recordings

### SEBTS Panopto (panopto.sebts.edu)

**Content:** Theology, biblical studies, ministry courses

**Speakers:** Faculty lectures (Danny Akin, Gregg Allison, Owen Strachan, others)

**LoRA Mapping:**
- Individual faculty lectures → Individual faculty LoRA
- Institutional systematic theology courses → SEBTS LoRA (consensus theological voice)
- Specialized topics → Subject-specific LoRAs if identifiable

### SBTS Panopto (panopto.sbts.edu)

**Content:** Courses in systematic theology, biblical exegesis, ministry

**Speakers:** SBTS faculty (Mohler, Schreiner, Hamilton, etc.)

### NOBTS Panopto (nobts.edu/panopto)

**Content:** Seminary courses, theological lectures

**Speakers:** NOBTS faculty and adjuncts

---

## Theological Articles & Publications

### SEBTS News & Articles (sebts.edu/news)

**Filter for theological content (NOT institutional announcements):**

**Theological keywords:**
- Theology, doctrine, exegesis, biblical studies
- Reformation, creeds, confessions
- Apologetics, ethics, ministry

**Exclude:** Campus news, events, fundraising, administrative

**Authors:** Faculty articles, guest contributions

**LoRA Mapping:**
- Article by Danny Akin → Danny Akin LoRA
- Article by Gregg Allison → Gregg Allison LoRA
- Institutional theological statement → SEBTS LoRA

### SBTS News & Articles (sbts.edu/news)

**Similar filtering to SEBTS**

**Known authors:** Mohler, Schreiner, Hamilton

### NOBTS News & Articles (nobts.edu/news)

**Similar theological filtering**

---

## Puritan Theological Seminary

### Content Sources

1. **Lectures (puritanseminary.org/lectures)**
   - Faculty lectures
   - Guest speakers
   - Symposium presentations

2. **Symposia (puritanseminary.org/symposia)**
   - Annual academic symposium recordings
   - Themed theological conferences
   - Multi-speaker presentations

3. **Articles (puritanseminary.org/articles)**
   - Theological publications
   - Faculty research
   - Educational resources

**Known Speakers:** Joel Beeke, Michael Barrett, others

**LoRA Mapping:**
- Joel Beeke lectures → Joel Beeke LoRA
- Institutional symposium → Puritan Seminary LoRA
- Faculty articles → Individual faculty LoRAs

---

## Reformed Theological Seminary (RTS)

### Content Sources

1. **Chapel Services (rts.edu/resources/chapel)**
   - Daily chapel recordings
   - Multi-campus services

2. **Lectures (rts.edu/resources/lectures)**
   - Faculty lectures
   - Guest speakers
   - Course recordings

3. **Publications (rts.edu/news)**
   - Theological articles
   - Faculty publications

**Known Faculty:** Sinclair Ferguson, Ligon Duncan, others

**LoRA Mapping:**
- Sinclair Ferguson chapel → Sinclair Ferguson LoRA + RTS LoRA
- Faculty lectures → Individual faculty LoRAs
- Institutional theological statements → RTS LoRA

---

## Westminster Seminary

### Content Sources

1. **Media Library (wts.edu/resources/media)**
   - Course lectures
   - Chapel services
   - Symposium recordings

2. **Publications (wts.edu/news)**
   - Theological articles
   - Faculty research
   - Academic papers

**LoRA Mapping:**
- Faculty lectures → Individual faculty LoRAs
- Institutional theological consensus → Westminster LoRA

---

## FORGE Education (forge.education)

### Content Sources

1. **Video Lectures (forge.education/videos)**
   - Theological education videos
   - Free resource platform
   - Missional theology focus

2. **Courses (forge.education/courses)**
   - Structured theological curriculum
   - Multi-speaker courses

**Speakers:** Various evangelical/Reformed educators

**LoRA Mapping:**
- Individual lecturer → Individual LoRA if established figure
- Course consensus → FORGE LoRA (platform voice)

---

## John Frame Resources

### Content Sources

1. **Personal Site (theoperspectives.org)**
   - Theological publications
   - Presuppositional apologetics
   - Systematic theology

2. **Westminster Seminary California (wscal.edu)**
   - John Frame lectures
   - Apologetics courses
   - Seminar recordings

3. **Publications**
   - Books (if available as text)
   - Academic papers
   - Online articles

**LoRA Mapping:**
- All John Frame content → John Frame LoRA
- His presence in other seminaries → Cross-referenced in those LoRAs

---

## LoRA Expansion: New Candidates from Institutions

### High Priority (50+ hours content)
1. **Tom Schreiner** (SBTS) — Systematic theology, NT exegesis
2. **Gregg Allison** (SEBTS) — Ecclesiology, soteriology
3. **Owen Strachan** (SEBTS) — Ethics, theology, cultural engagement
4. **Joel Beeke** (Puritan Seminary) — Puritanism, experiential theology
5. **Jim Hamilton** (SBTS) — Biblical theology, missions

### Medium Priority (20-50 hours content)
6. **Ligon Duncan** (RTS) — Reformed theology, leadership
7. **Michael Barrett** (Puritan) — Puritan theology
8. **Tom Nettles** (NOBTS) — Historical theology, Baptist heritage

### Emerging Candidates (5-20 hours content)
9. **Chuck Kelley** (NOBTS President)
10. **Various SEBTS/SBTS/NOBTS faculty**

---

## Institutional LoRAs (Consensus Voices)

These capture the theological voice of the institution, not individual faculty:

1. **SEBTS Institutional LoRA** (sebts.edu)
   - Chapel services, Panopto lectures, theological articles
   - Voice: Evangelical Baptist, practical theology, ministry focus
   - Training: ~500k-1M words (chapel + panopto mix)

2. **SBTS Institutional LoRA** (sbts.edu)
   - Similar to SEBTS
   - Voice: Southern Baptist, reformed tendencies
   - Training: ~500k-1M words

3. **NOBTS Institutional LoRA** (nobts.edu)
   - New Orleans Baptist seminary voice
   - Training: ~300k-500k words

4. **Puritan Seminary LoRA** (puritanseminary.org)
   - Puritan theology, experiential depth
   - Training: ~200k-300k words

5. **RTS Institutional LoRA** (rts.edu)
   - Reformed Presbyterian voice
   - Training: ~300k-500k words

6. **Westminster Seminary LoRA** (wts.edu)
   - Reformed Presbyterian, confessional
   - Training: ~200k-300k words

7. **FORGE LoRA** (forge.education)
   - Missional theology, global perspective
   - Training: ~100k-200k words

---

## Data Pipeline

```
Seminary Website
  ↓
Discovery (YouTube, RSS, Panopto, scraping)
  ↓
Metadata Extraction (speaker, date, title, institution)
  ↓
Deduplication (check against existing)
  ↓
Transcription (if audio/video → Whisper)
  ↓
Routing:
  ├→ Individual Faculty LoRA (if speaker identifiable)
  └→ Institutional LoRA (always)
  ↓
Training Data Prep (JSONL format)
  ↓
LoRA Training Queue
```

---

## Implementation Roadmap

### Phase 1: SEBTS + SBTS + NOBTS (Week 1)
- Chapel discovery (YouTube/direct)
- Panopto API integration (if available)
- Article scraping
- LoRA data prep

### Phase 2: Puritan + RTS + Westminster (Week 2)
- Lecture discovery
- Symposium recording extraction
- Article/publication scraping

### Phase 3: FORGE + John Frame (Week 3)
- Video platform scraping
- Personal site content extraction
- Publication index

### Phase 4: Individual Faculty LoRAs (Week 4+)
- Extract Tom Schreiner content
- Extract Gregg Allison content
- Extract Joel Beeke content
- Build individual LoRAs

---

## Success Metrics

- [ ] 50+ new sermons/month from seminaries
- [ ] 10+ new individual faculty LoRA candidates identified
- [ ] 7 institutional LoRAs trained
- [ ] <5% duplicate rate
- [ ] Zero duplicate content between institutional + individual LoRAs (proper routing)

---

_Soli Deo Gloria._
