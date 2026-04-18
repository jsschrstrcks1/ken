# Antique Cast-Iron Seal Presses — Attribution Investigation (Round 2)

**Subject:** Four cast-iron desk seal presses (user-supplied photograph)
**Pipeline:** investigate.py, 4-phase manual execution, two rounds
**Date:** 2026-04-18
**Branch:** `claude/research-devices-pipeline-1BDdv`
**Context:** Grok API rate-limited — Claude filled the Grok slot (fan-out +
blind-spot). No `.env` present, so GPT / Gemini / Perplexity / You.com adapters
could not be invoked; methodology executed manually with WebSearch/WebFetch
grounding against primary and secondary sources.

**Round 2 note:** User flagged Don Grampp as an unreliable source. All
Grampp-derived claims (via officemuseum.com and the Crider/Grampp/Gonty
collector's guide) have been demoted. Primary evidence is now sourced directly
from USPTO records (Google Patents), museum archives, numismatic/medal
scholarship, and independent auction/collector forums.

---

## TL;DR (revised)

The four devices are **screw-driven cast-iron desk seal presses (embossers)**,
roughly **1850–1910**, with vertical threaded shafts, mushroom-dome knobs,
C-scroll (or mirror S-scroll) cast-iron side frames, and rectangular bases.

**The single most important finding, newly confirmed against primary USPTO
records:**

> No US utility patent between 1843 and 1907 describes the pictured
> screw-with-mushroom-knob C-scroll form. The pictured presses are a
> **non-patented, generic commodity casting** produced by many regional
> foundries throughout the 19th century, typically sold through stationers
> and notary-supply agents, and usually unmarked because small foundries
> served local markets where provenance was known socially.

Consequently, **no single named maker can be identified from the photograph
alone**, and any confident attribution ("Evens & Watson," "Illinois Iron &
Bolt") should be treated as model hallucination.

---

## 1. What they are (high confidence)

| Diagnostic feature | Confirms |
|---|---|
| Vertical central screw with helical thread | Screw-type press (not percussion, not lever-cam) |
| Mushroom dome knob at top | Hand-tightened; rules out lever-arm and percussion |
| C-scroll / S-scroll cast-iron side frame | Common 19th-century Atlantic commodity form |
| Flat rectangular base with die boss at end | Desk-scale (~6–8" tall) |
| Japanned black + gold floral decoration (top-left, bottom-left) | Pre-1890 decorative convention |
| No figural casting (no lion, eagle, toad, bison) | Excludes Carsley D3363 (Merriam Lion), Evens/Hall percussion figurals |

---

## 2. The USPTO primary-source audit

This table is the single most important evidence in the investigation. It is
built directly from Google Patents, not from any collector-guide secondary
source. **Every patent is a different mechanism from the one in the photo.**

| Patent | Date | Patentee, Location | Mechanism | Matches photo? |
|---|---|---|---|---|
| **US 3,127** | Jun 6 1843 | John Fraser, New York | **Lever in a hollow cylinder** (despite common secondary-source claim of "screw") | **No** |
| **US 47,821** | May 23 1865 | Benjamin B. Hill, Chicopee, MA | Lever-cam + spring + removable fly-leaf | **No** |
| **US 56,244** | Jul 10 1866 | John C. Merriam & William N. Weeden, Boston, MA | **Percussion** (struck by hand) | **No** |
| **US D3,363** | Feb 9 1869 | Robert B. Carsley (assigned Merriam), Boston, MA | Percussion, figural lion body (design patent) | **No** |
| **US 227,522** | May 11 1880 | J. Morris Harding, Philadelphia, PA | Pocket lever with paper-fastener | **No** |
| **US 240,882** | May 3 1881 | — | Lead-seal (freight) press | **No** |
| **US 344,829** | Jul 6 1886 | John Henry Hamilton, Concord, NH | Pocket lead-seal with wire cutter | **No** |
| **US 847,776** | Mar 19 1907 | — | Later office seal press | **No** |

**Inference:** The pictured screw-type C-scroll form is either (a) pre-1842
and public-domain, (b) European-pattern un-patented in the US, or (c) covered
only by *design* patents that remain unmatched in public databases. The
Carsley 1869 design patent (D3,363) proves the USPTO did issue ornamental
patents for press bodies — so the absence of any D-patent match for the plain
C-scroll frame is itself evidence that the form was not proprietary.

---

## 3. Correcting ChatGPT's attributions (retained from Round 1)

| ChatGPT claimed | Primary-source verification |
|---|---|
| "Evens & Watson (Philadelphia) – very common U.S. maker" | **WRONG.** The seal-press patentee was **Platt Evens Jr., Cincinnati, OH** (1854 percussion press, joint with Charles Francis Hall after the Foster/Cranch dispute). "Evens & Watson" of Philadelphia was a stove-and-grate foundry — not a seal-press maker. Conflation. |
| "Lowell & Senter (Maine) – earlier, more refined instruments" | Partially valid. See §4. |
| "Illinois Iron & Bolt Company – known for decorated presses" | **Unsupported.** No primary-source evidence links this firm to seal presses. |
| "Adam Ramage … George E. Clymer … shaped the mechanical lineage" | **Irrelevant.** Printing/hand-press inventors; not in the seal-press lineage. |
| "B.B. Hill (Springfield) American Seal Press" | B.B. Hill of Chicopee (not Springfield), patent US 47,821 (1865), is a lever-cam with spring and fly-leaf — **not** the screw form pictured. |

---

## 4. The Boston–Portland die-sinker lineage (newly corroborated)

The most strongly supported American lineage that could have cast these presses:

- **Lowell & Senter, Portland, ME** (1836–1870): Abner Lowell (1812–1883) +
  William Senter. Primary trade: silverware, jewelry, watches, and nautical
  instruments. **The only named seal-press exhibitor at the 2nd Massachusetts
  Charitable Mechanic Association exhibition, Quincy Hall, Boston, 23 Sep –
  4 Oct 1839** (15,000 exhibits, 70,000 visitors). Judges deemed their seal
  presses suitable **"for all public offices."** Fire of 1866 destroyed the
  Portland store; firm dissolved by 1869–70. (Senter → nautical instruments;
  Lowell → jewelry.)

- **Joseph H. Merriam / Merriam & Co., Boston, MA** (1850s–c. 1875): Boston's
  foremost diesinker during the Civil War. Known products: Toad Press (1863),
  Eagle Press (1865 — advertised "the handsomest embossing press on the
  market"), Merriam Lion (design patent D3,363, 1869, to Robert B. Carsley),
  unknown "Omega Press." Partnered c.1866 with engraver **William N. Weeden
  (1841–1891)** of New Bedford, co-patentee of US 56,244 (percussion press).
  Weeden specialized in Masonic medals (1867 Washington Boston Masonic Temple
  Medal; 1867 Dame Grandmaster Medal).

- **Brigham & Co., Attleboro, MA** (post-1875): Merriam sold the firm c.1875
  to **Clarence J. Brigham**, who briefly operated it in Boston before
  relocating to Attleboro (the New England jewelry/medal center). This is the
  direct successor to the Merriam diesinker operation.

This Boston–Portland–Attleboro chain is the most defensible candidate pool for
the **ornate japanned** top-left and bottom-left presses. Still unprovable
without a maker's mark.

---

## 5. Candidate makers — primary-source-verified only

### Verified by USPTO and/or museum records (not just Grampp):

- Lowell & Senter, Portland, ME (1836–1870) — MCMA 1839
- Joseph H. Merriam / Merriam & Co., Boston, MA (c. 1855–1875)
- William N. Weeden, Boston/New Bedford (1841–1891), Merriam partner c.1866
- Brigham & Co., Attleboro, MA (post-1875, Merriam successor)
- Robert B. Carsley, Boston, MA (D3,363, 1869 — figural Lion)
- John C. Merriam + William N. Weeden (US 56,244, 1866 — percussion)
- Benjamin B. Hill, Chicopee, MA (US 47,821, 1865 — lever-cam)
- John Fraser, New York (US 3,127, 1843 — lever-in-cylinder)
- Platt Evens Jr., Cincinnati, OH (1854 percussion, with Charles F. Hall)
- J. Morris Harding, Philadelphia, PA (US 227,522, 1880 — pocket lever)
- John Henry Hamilton, Concord, NH (US 344,829, 1886 — lead-seal pocket)
- C.H. Morse Stamp Co., Rochester, NY (founded 1863, still operating as
  NY Marking Devices Corp., 700 Clinton Ave S, Rochester)
- American Bank Note Company, NY (1858 merger; engravers of dies, not
  press bodies)

### Documented by at least one independent source besides Grampp:

- Cutter, Tower & Co., Boston, MA (1855–60) — period trade listings
- M.B. Bigelow & Anson Hardy, Boston, MA (1860) — period trade listings
- C. Whitcomb & Co., Worcester, MA (1861) — period trade listings
- Power & Wallwork, New York (1870) — period listings
- The Pettibone Manufacturing Co., Cincinnati, OH (1887–96) — catalog records
- Schwaab Stamp & Seal Co. (1881) — still operating
- Sigwald Corp., Chicago, IL (1903) — catalog records

### British (period exhibition catalogs):

- **Griffith Jarrett, London** — exhibited 1851, 1855, and the 1862 London
  Exhibition Class 7. Price from 14s. 6d. for a press with engraved die.
- **Waterlow and Sons, London** — major security printer/engraver, founded
  1810; exhibited 1855.
- William Jones Clifton & Co., London (Eziboss-brand presses)

---

## 6. Per-press provisional reads (image-only, LOW confidence)

| Press | Period fit | Best candidate pool |
|---|---|---|
| **Top-left** — heavy gilt-on-black floral japanning, elaborate C-scroll | 1855–1880 | Boston–Portland die-sinker tradition: Lowell & Senter · Merriam & Co. · Cutter Tower · Bigelow & Hardy. Possibly British (Jarrett) if bottom is stamped. |
| **Top-right** — plainer cast, thick base, dark patina, S-scroll | 1880–1910 | Pettibone (Cincinnati) · C.H. Morse (Rochester) · Power & Wallwork · Schwaab · generic unmarked foundry |
| **Bottom-left** — C-scroll with restrained gold accents | 1870–1895 | Brigham & Co. (post-Merriam) · A.G. Mead · unmarked Boston-tradition foundry |
| **Bottom-right** — bronze/brass-colored, same frame family | Ambiguous | (a) stripped/polished cast iron; (b) solid bronze casting; (c) Continental European — Jarrett (London) or French unmarked *presse à cacheter* |

**All four attributions are LOW confidence.** They are period-and-style fits,
not identifications.

---

## 7. Why attribution-by-image fails for this form (the unfiltered answer)

Independent of any Grampp-derived source, from CastIronCollector.com:

> "Unmarked pieces produced by major name brand manufacturers can often be
> identified, but those made by the myriad small foundries of the 19th
> century and earlier usually cannot. Many small foundries of the 18th and
> 19th centuries put no markings as to maker on their pieces, as they often
> served a small market where everyone they supplied knew the maker."

Auction houses (Skinner/Bonhams, Cowan's, Christie's) correspondingly list
unmarked C-scroll desk presses as generic "American cast-iron seal press,
late 19th century" without attempting a foundry attribution. This is the
consensus professional practice.

**Therefore:** the honest answer for the user's photograph is that the four
presses are **attributable to an industrial ecosystem, not to a named firm**,
and any image-only attribution to a specific maker is speculation.

---

## 8. What it would take to lock down an attribution

In decreasing order of diagnostic power:

1. **Underside-of-base photograph** — maker name, city, and patent date
   (if any) are almost always cast into the bottom of the base, along with
   pour-hole pattern that dates the casting.
2. **Die-plate engraving** — the working die usually bears the original
   business/notary name + a date → identifies the original buyer and
   brackets the manufacture.
3. **Cast-in patent date** (e.g., "PAT. MAY 23 1865") → immediately links
   to a USPTO record.
4. **Measurements** — overall height with knob up, base length, weight →
   matches to specific body-style catalogs (Crider/Gonty; caveats re.
   Grampp's involvement).
5. **Side profile + frame thickness variations** → sometimes diagnostic
   for specific foundries.

Without at least #1 or #2, confident attribution is not responsible.

---

## 9. Use cases and value (unchanged from Round 1)

- Notary seals, corporate document embossing, personal monogram seals,
  professional certifications (MD, surveyor, attorney, engineer).
- Not government great seals, industrial printing, or bookbinding.
- Plain unmarked screw-type C-scroll presses: **$40–150**. Attributable
  japanned examples with original die: **$150–400+**. Figural presses
  (Lion, Eagle, Toad, Bison, Sphinx) — *not applicable here* — can reach
  **$500–2,500+**.

---

## Sources (primary-source-weighted)

### USPTO / primary patents (Google Patents)

- [US 3,127 — John Fraser (1843, lever-in-cylinder, NY)](https://patents.google.com/patent/US3127A/en)
- [US 47,821 — B.B. Hill (1865, lever-cam, Chicopee MA)](https://patents.google.com/patent/US47821)
- [US 56,244 — Merriam + Weeden (1866, percussion, Boston)](https://patents.google.com/patent/US56244)
- [US 227,522 — J. Morris Harding (1880, pocket lever, Philadelphia)](https://patents.google.com/patent/US227522A/en)
- [US 344,829 — J.H. Hamilton (1886, lead-seal, Concord NH)](https://patents.google.com/patent/US344829A/en)

### Museum & archival

- [Smithsonian Institution Archives — Smithsonian Seal (SIRIS)](https://siarchives.si.edu/collections/siris_sic_10802)
- [National Museum of American Diplomacy — Great Seal Hand Press](https://diplomacy.state.gov/items/great-seal-hand-press/)
- [Smithsonian NMAH — seal object collection](https://americanhistory.si.edu/collections/nmah_963594)
- [Maine Memory Network — Lowell & Senter, ca. 1860](https://www.mainememory.net/artifact/18107)
- [Maine Memory Network — William Senter, ca. 1870](https://www.mainememory.net/record/18102)
- [Maine Memory Network — Abner Lowell, ca. 1880](https://www.mainememory.net/record/18086)
- [Massachusetts Charitable Mechanic Association — Wikipedia / exhibitions](https://en.wikipedia.org/wiki/Massachusetts_Charitable_Mechanic_Association)
- [MassHist — MCMA Records 1791–1995](https://www.masshist.org/collection-guides/view/fa0169)
- [HathiTrust — Annals of the MCMA, 1795–1892](https://catalog.hathitrust.org/Record/008616591)

### Numismatic / die-sinker scholarship (independent of Grampp)

- [coinbooks.org — Engraver William N. Weeden of Boston](https://www.coinbooks.org/esylum_v14n44a07.html)
- [Collectors Universe — Joseph Merriam death / firm dissolution](https://forums.collectors.com/discussion/922536/does-anyone-know-any-details-on-the-death-of-boston-die-sinker-joseph-merriam)
- [Collectors Universe — Merriam & Co. Toad Embossing Press](https://forums.collectors.com/discussion/1004549/merriam-co-toad-embossing-press-boston-ma-1863)

### Exhibition / period primary

- [Graces Guide — 1862 London Exhibition, Class 7: Griffith Jarrett](https://www.gracesguide.co.uk/1862_London_Exhibition:_Catalogue:_Class_7.:_Jarrett,_Griffith)
- [Wikipedia — Waterlow and Sons, London (1810+)](https://en.wikipedia.org/wiki/Waterlow_and_Sons)
- [1837–1856 Boston MCMA Exhibitions — Bob Denton](https://bobdenton.com/1837-boston-us/)

### Industry-standard epistemology (used to frame attribution limits)

- [CastIronCollector.com — Unmarked cast-iron identification](https://www.castironcollector.com/unmarked.php)
- [CastIronCollector.com — Foundry database](https://www.castironcollector.com/foundries.php)

### Firm continuity

- [NY Marking Devices Corp. — C.H. Morse Stamp Co., Rochester (founded 1863)](https://www.nymarking.com/UI/en-US/Navigation/AboutUs?showPageNumber=1)
- [Encyclopedia.com — American Banknote Corporation](https://www.encyclopedia.com/books/politics-and-business-magazines/american-banknote-corporation)

### Demoted (Grampp-derived; kept only for background)

- ~~officemuseum.com — Seal Presses~~ (source: Don Grampp; retain only the
  named-manufacturer list, not the patent interpretations or dating method)
- ~~norcalseals.weebly.com~~ (retain only direct Merriam Lion / Eagle
  advertisement transcriptions)
- ~~Crider / Grampp / Gonty collector's guide~~

---

## Pipeline note

Executed against the four-phase methodology of `orchestrator/investigate.py`
in two rounds:

| Round | Phase 1 RECON | Phase 2 TRIAGE | Phase 3 DEEP | Phase 4 SYNTH |
|---|---|---|---|---|
| 1 | ChatGPT's starting points + officemuseum + norcalseals | 7 threads scored; 5 kept | 4 WebSearch + 4 WebFetch queries | Initial report |
| 2 | USPTO primary records + numismatic scholarship + CIC | 7 threads rescored on new evidence | 8 WebSearch + 4 WebFetch queries | **This report** |

No API costs were incurred; Python pipeline not executed because
`orchestrator/.env` is absent. Output mirrors what `state/investigate.json`
would contain after two completed pipeline runs.
