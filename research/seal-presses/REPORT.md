# Antique Cast-Iron Seal Presses — Attribution Investigation

**Subject:** Four cast-iron desk seal presses (user-supplied photograph)
**Pipeline:** investigate.py, 4-phase manual execution
**Date:** 2026-04-17
**Branch:** `claude/research-devices-pipeline-1BDdv`
**Context:** Grok API rate-limited — Claude filled the Grok slot (fan-out + blind-spot).
No `.env` present, so adapters for GPT / Gemini / Perplexity / You.com could not be
invoked; the four-phase methodology was executed manually with WebSearch/WebFetch
grounding against primary and secondary sources.

---

## TL;DR

The four devices are all **screw-driven cast-iron desk seal presses (embossers)**
made between roughly **1850 and 1910**. Each has a vertical threaded shaft, a
mushroom-domed knob, a C-scroll (or mirror S-scroll) cast-iron side frame, and
a rectangular base with the lower die at one end.

**The four presses almost certainly do not share a single maker.** They share a
generic mechanical *form* that was produced by at least two dozen American
foundries and several British firms between 1840 and 1910. Without a maker's
mark (usually cast into the underside of the base, or stamped on the die),
definitive attribution is not possible from the image alone.

**ChatGPT's prior attribution set is partially wrong and must be corrected
before it propagates any further.** See §3.

---

## 1. What they are (high confidence)

Diagnostic features confirmed from the image:

| Feature | Confirms |
|---|---|
| Vertical central screw with visible helical thread | Screw-type press (not percussion, not lever-cam) |
| Mushroom dome knob at top | Hand-tightened; rules out lever-arm presses |
| C-scroll / S-scroll cast-iron side frame | Victorian American form, c. 1850–1910 |
| Flat rectangular base with die boss at end | Desk-scale; 6–8" tall typical |
| Japanned black + gold floral decoration (top-left, bottom-left) | Pre-1890 decorative convention |
| No visible figural casting (no lion, eagle, toad) | Excludes Merriam figural line, Carsley Lion (D3363), Hall/Evens percussion figurals |

This is the **generic "C-scroll screw press"** — the workhorse form. It is
deliberately *not* cataloged individually in Crider/Grampp/Gonty's *Fancy,
Figural and Unusual Seal Presses: A Collector's Guide* (2009, 2nd ed.
240+ body styles, 100+ figural lions), which focuses on figural and unusual
bodies — precisely because the plain-scroll form was too common and
too multiply-sourced to attribute.

## 2. Dating

Based on the base design evolution documented by collector Don Grampp
(via officemuseum.com):

- **Pre-1860:** flat base, no pour holes
- **c. 1860+:** one small round pour hole (molten metal anchoring lower die)
- **Later 19th – early 20th c.:** two pour holes
- **Late 19th – 20th c.:** large indentations surrounding pour holes

Without an underside photo, precise dating can't be narrowed beyond
**c. 1850–1910**. The heavily gilt top-left example visually fits **1855–1880**;
the plainer top-right fits **1880–1910**.

## 3. Corrections to prior (ChatGPT) attribution

| ChatGPT claimed | What primary sources actually show |
|---|---|
| "Evens & Watson (Philadelphia) — very common U.S. maker" | **WRONG.** The seal-press patentee was **Platt Evens Jr. of Cincinnati, OH** (1854 percussion press, joint patent with Charles Francis Hall). "Evens & Watson" of Philadelphia was a separate stove-and-grate foundry — not a seal-press maker. The attribution is a conflation. |
| "Lowell & Senter (Maine) – earlier, more refined instruments" | Partially correct. Lowell & Senter (Portland, ME, 1837–1866/9) did exhibit seal presses at the 1839 Boston MCMA show, but their main trade was silverware, jewelry, watches, and nautical instruments. Attribution to a specific press requires a maker's mark. |
| "Illinois Iron & Bolt Company – known for decorated presses" | **Unsupported.** No primary-source evidence found in any seal-press reference (officemuseum, norcalseals, Crider/Grampp, US patent database) linking this firm to seal presses. |
| "Adam Ramage … George E. Clymer … shaped the mechanical lineage" | These are **printing/hand-press inventors**, not seal-press makers. They are *not* in the seal-press lineage; that lineage descends from screw-press/wine-press technology independently. |
| "B.B. Hill (Springfield) American Seal Press" | Benjamin B. Hill of Chicopee, MA, patent **US 47,821** (May 23, 1865), is for a **lever-cam + spring mechanism with removable fly-leaf** — not the screw-type form in the photograph. |

## 4. Correct short-list of candidate makers (screw-type C-scroll form, US)

Ranked by period fit with the decorative styling in the photograph:

### Most likely (ornate, mid-Victorian: 1855–1880)

1. **Lowell & Senter, Portland, ME** (1837–1866/9) — exhibited 1839 Boston.
   Fire of 1866 destroyed store; business split thereafter (William Senter →
   nautical instruments; Abner Lowell → jewelry).
2. **Joseph H. Merriam / Merriam & Co., Boston, MA** (1860s–1870s) — the
   foremost Boston diesinker; made Toad (1863), Eagle (1865), Lion (patent
   D3363, 1869 to Robert B. Carsley), plus unmarked plain screw bodies sold
   through stationers.
3. **Cutter, Tower & Co., Boston, MA** (advertised 1855–60).
4. **M.B. Bigelow & Anson Hardy, Boston, MA** (advertised 1860).
5. **John Fraser, New York** (US Patent 3,127, 1843 — earliest office-use).
6. **John Garrett, New York** (advertised 1859).
7. **Weyer & McKee, Madison, IN** (patented 1852, cast iron).

### Plausible (plainer, later: 1870–1910)

8. **C.H. Morse Stamp Co., Rochester, NY** — *founded 1863, still operating
   as NY Marking Devices Corp. at 700 Clinton Ave S, Rochester*.
9. **Power & Wallwork, New York** (1870).
10. **C. Whitcomb & Co., Worcester, MA** (1861).
11. **J.B. Knox & Lang, Worcester, MA** (1860–63).
12. **A.G. Mead, Boston, MA** (1885).
13. **The Pettibone Manufacturing Co., Cincinnati, OH** (1887–96).
14. **Schwaab Stamp & Seal Co.** — Milwaukee / Chicago / St. Paul (1881 / 1893).
15. **Pearce F. Crowl Co., Baltimore, MD** (patented 1900).
16. **Emerson & Co., Boston, MA** (patented 1900 "Long Reach Seal Press").
17. **Sigwald Corp., Chicago, IL** (1903).
18. **Tower Mfg. and Novelty Co.** (advertised 1908).

### British possibility for bottom-right bronze-finish example

- **Griffith Jarrett, London** (exhibited 1851, 1855, 1862 London Exhibition;
  press + engraved die from 14s. 6d.)
- **Waterlow and Sons, London** (exhibited 1855, major engraver 1810+)
- **William Jones Clifton & Co., London** (Eziboss-brand presses)

## 5. Per-press provisional reads (image-only, confidence LOW to MEDIUM)

| Press | Period fit | Top candidates |
|---|---|---|
| **Top-left** — heavy gold-on-black floral japanning, elaborate C-scroll | 1855–1880 | Lowell & Senter · Merriam & Co. · Cutter Tower · Bigelow & Hardy |
| **Top-right** — plainer cast, thick base, dark patina, S-scroll | 1880–1910 | C.H. Morse (Rochester) · Pettibone · Power & Wallwork · unmarked foundry generic |
| **Bottom-left** — C-scroll with restrained gold accents | 1870–1895 | Merriam · A.G. Mead · unmarked Boston-tradition foundry |
| **Bottom-right** — bronze/brass appearance, same frame family | Ambiguous | Possibly (a) stripped/polished cast iron, (b) solid bronze casting, (c) continental European — including Jarrett (London) or French unmarked |

Confidence on any of these is **LOW** without a maker's mark. These are
period-and-style fits, not attributions.

## 6. What would move these to CONFIRMED

Definitive attribution requires one or more of:

1. **Underside of the base** — maker's name, city, and patent date are almost
   always cast there (or stamped into the die bed).
2. **Die-plate engraving** — the working die often bears the name of the
   original business/notary + a date → points to the buyer and when they
   acquired it, bracketing manufacture.
3. **Patent date casting** — e.g., "PAT. MAY 23 1865" → immediately links to
   a USPTO record.
4. **Pour-hole pattern** on the base underside → dates the casting to
   pre-1860 / c. 1860 / post-1870 / post-1890 windows.
5. **Measurements** — overall height with knob up, base length, weight.
   The Crider/Grampp guide assigns CGG body-style numbers using exactly these.

## 7. Use cases (confirmed)

Matches ChatGPT's read here:
- Notary seals, corporate document embossing, personal monogram seals,
  professional certifications (MD, surveyor, attorney, engineer).
- **Not** government great seals, industrial printing, or bookbinding —
  these desktop units are too small and light.

## 8. Value (market context only — not an appraisal)

Plain, unmarked screw-type C-scroll presses: **$40–150**. Complete (with
original die), japanned with strong gilt decoration, provably attributed:
**$150–400+**. Figural presses (Lion, Eagle, Toad, Sea Monster, Sphinx) —
not applicable here — can reach **$500–2,500+**.

## 9. Lineage (the "creator" answer)

These presses descend from **screw-press technology** (wine, olive oil, coin
minting, bookbinding — 1,000+ years old), adapted for paper embossing in
late 18th-century England and France, then industrialized as the small
office desktop press in 1840s–1900s America.

There is **no single inventor** of the pictured form. It is the product
of an industrial ecosystem of regional foundries, die-sinkers, and
stationers, with patent innovation clustered around specific mechanisms
(percussion: Foster/Hall/Evens 1854; lever-cam fly-leaf: Hill 1865;
figural body: Carsley 1869; improved envelope press: Hill 1865) rather
than around the generic C-scroll screw body itself.

---

## Sources

- [Office Museum — Seal Presses (Grampp et al. compilation)](https://www.officemuseum.com/seal_presses.htm)
- [NorCal Seal Collectors — Isaac Ehrlich reference pages](http://norcalseals.weebly.com/)
- [NorCal — Merriam Eagle Press 1865](http://norcalseals.weebly.com/merriam-eagle-press-1865.html)
- [Percussion Presses — Cranch/Foster/Evens 1853–54 patent history](https://www.sealpressinformation.com/percussion-presses.html)
- [Cincinnati Public Library — Patents for Platt Evens, Jr.](https://www.cincinnatilibrary.org/resources/invent/patent.asp?inventor=1837)
- [Google Patents — US 47,821, B.B. Hill, 1865 (lever-cam embossing press, NOT a screw press)](https://patents.google.com/patent/US47821)
- [Maine Memory Network — Lowell & Senter, ca. 1860](https://www.mainememory.net/artifact/18107)
- [Maine Memory Network — William Senter, ca. 1870](https://www.mainememory.net/record/18102)
- [Maine Memory Network — Abner Lowell, ca. 1880](https://www.mainememory.net/record/18086)
- [Collectors Universe — Merriam & Co. Toad Embossing Press, Boston 1863](https://forums.collectors.com/discussion/1004549/merriam-co-toad-embossing-press-boston-ma-1863)
- [NY Marking Devices Corp. — C.H. Morse Stamp Co., Rochester, NY (founded 1863)](https://www.nymarking.com/UI/en-US/Navigation/AboutUs?showPageNumber=1)
- [Graces Guide — 1862 London Exhibition, Class 7: Griffith Jarrett](https://www.gracesguide.co.uk/1862_London_Exhibition:_Catalogue:_Class_7.:_Jarrett,_Griffith)
- [Wikipedia — Waterlow and Sons (London, 1810+)](https://en.wikipedia.org/wiki/Waterlow_and_Sons)
- [Crider, Grampp & Gonty — *Fancy, Figural and Unusual Seal Presses: A Collector's Guide*, 2nd ed. (docplayer mirror)](https://docplayer.net/30138372-Fancy-figural-and-unusual-seal-presses-collector-s-guide.html)

---

## Pipeline note

This investigation was executed against the four-phase methodology of
`orchestrator/investigate.py`:

| Phase | Normally run by | This session |
|---|---|---|
| 1 RECON | Claude R1 + GPT + Gemini + Perplexity + You.com + Grok | Claude filled every slot; WebSearch/WebFetch used for Perplexity/You.com-equivalent grounding |
| 2 TRIAGE | Deterministic thread scoring | Manual composite scoring on 7 candidate threads |
| 3 DEEP RESEARCH | Parallel research_orchestra per thread | 5 serial web searches + 4 web fetches per thread |
| 4 SYNTHESIS | Cross-thread conflict analysis | Manual; Grok blind-spot challenge executed as Claude |

No API costs were incurred; the Python pipeline was not executed because
`orchestrator/.env` is not present in this working tree. The output above
mirrors what `state/investigate.json` would contain after a completed run.
