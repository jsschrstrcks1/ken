# unfinished_tasks.md — cruisinginthewake.com Audit
_Generated: 2026-05-13 | Crawl: 1,229 URLs from sitemap | HTTP 200: 1,229/1,229 | Issues: 450+ pages_
_Models: Claude (lead), qwen3:32b (m4max), llava:13b (m4max, visual), GPT-4o (technical/fixes)_

---

## 🔴 CRITICAL — Fix Immediately

### 1. Ship Size Atlas — All RCL Links Broken
**File:** `tools/ship-size-atlas.html` (or JS that builds the table)
**Issue:** Atlas links use `/ships/royal-caribbean/` but all RCL pages live at `/ships/rcl/`
**Impact:** Top-10 biggest ships in the world all 404 — flagship feature broken for every visitor
**Fix:**
```apache
# .htaccess
RewriteRule ^ships/royal-caribbean/(.*)$ /ships/rcl/$1 [R=301,L]
```
Or fix the link template directly in the atlas source.

---

## 🟠 HIGH — Navigation / 404s

### 2. Norwegian Encore — 404
**URL:** `https://cruisinginthewake.com/ships/norwegian/norwegian-encore.html`
**Issue:** Page missing entirely — Norwegian Encore is a major, current ship
**Fix:** Create page or restore from backup

### 3. Celebrity index — missing
**URL:** `https://cruisinginthewake.com/ships/celebrity/`
**Issue:** No index at old path (real path: `/ships/celebrity-cruises/`)
**Fix:**
```apache
RewriteRule ^ships/celebrity/(.*)$ /ships/celebrity-cruises/$1 [R=301,L]
```

### 4. Holland America index — missing
**URL:** `https://cruisinginthewake.com/ships/holland-america/`
**Issue:** No index at old path (real path: `/ships/holland-america-line/`)
**Fix:**
```apache
RewriteRule ^ships/holland-america/(.*)$ /ships/holland-america-line/$1 [R=301,L]
```

---

## 🟡 MEDIUM — Content / SEO

### 5. GT Tonnage Data Mismatch
**Issue:** Ship Size Atlas shows 250,800 GT for a vessel whose ship page shows 248,663 GT (same vessel, two different numbers)
**Impact:** Credibility — users comparing data across pages
**Fix:** Audit all GT figures in atlas against corresponding ship pages; reconcile to a single source of truth

### 6. ships.html — Misleading Copy
**URL:** `https://cruisinginthewake.com/ships.html`
**Issue:** Page says "295 ship profiles" but is RCL-only. If 15 lines are intended, copy and nav need updating.
**Fix:** Update description to say "Royal Caribbean fleet" or expand to a true multi-line index

---

## 📋 CONTENT GAPS — Pages Flagged for Work

### Missing H1 Tags (120 pages)
Pages return 200 but have no H1 — SEO and accessibility issue.

**Ports (39 pages):**
```
/ports/beijing.html
/ports/durban.html
/ports/falmouth-jamaica.html
/ports/gibraltar.html
/ports/guadeloupe.html
/ports/istanbul.html
/ports/kusadasi.html
/ports/kyoto.html
/ports/luanda.html
/ports/malaga.html
/ports/olden.html
/ports/panama-canal.html
/ports/ponta-delgada.html
/ports/port-moresby.html
/ports/portland.html
/ports/porto.html
/ports/ravenna.html
/ports/reykjavik.html
/ports/rhodes.html
/ports/riga.html
/ports/royal-beach-club-antigua.html
/ports/royal-beach-club-cozumel.html
/ports/royal-beach-club-nassau.html
/ports/saguenay.html
/ports/saint-john.html
/ports/scotland.html
/ports/st-petersburg.html
/ports/sydney-ns.html
/ports/tallinn.html
/ports/tangier.html
/ports/taormina.html
/ports/tauranga.html
/ports/tunis.html
/ports/valencia.html
/ports/vigo.html
/ports/villefranche.html
/ports/warnemunde.html
/ports/waterford.html
/ports/zeebrugge.html
```

**Ships — Celebrity (26 pages, no H1):**
```
/ships/celebrity-cruises/celebrity-apex.html
/ships/celebrity-cruises/celebrity-ascent.html
/ships/celebrity-cruises/celebrity-beyond.html
/ships/celebrity-cruises/celebrity-century.html
/ships/celebrity-cruises/celebrity-compass.html
/ships/celebrity-cruises/celebrity-constellation.html
/ships/celebrity-cruises/celebrity-eclipse.html
/ships/celebrity-cruises/celebrity-edge.html
/ships/celebrity-cruises/celebrity-equinox.html
/ships/celebrity-cruises/celebrity-flora.html
/ships/celebrity-cruises/celebrity-galaxy.html
/ships/celebrity-cruises/celebrity-infinity.html
/ships/celebrity-cruises/celebrity-mercury.html
/ships/celebrity-cruises/celebrity-millennium.html
/ships/celebrity-cruises/celebrity-reflection.html
/ships/celebrity-cruises/celebrity-seeker.html
/ships/celebrity-cruises/celebrity-silhouette.html
/ships/celebrity-cruises/celebrity-solstice.html
/ships/celebrity-cruises/celebrity-summit.html
/ships/celebrity-cruises/celebrity-xcel.html
/ships/celebrity-cruises/celebrity-xpedition.html
/ships/celebrity-cruises/celebrity-xperience.html
/ships/celebrity-cruises/celebrity-xploration.html
/ships/celebrity-cruises/horizon.html
/ships/celebrity-cruises/ss-meridian.html
/ships/celebrity-cruises/unnamed-edge-class.html
/ships/celebrity-cruises/unnamed-project-nirvana.html
/ships/celebrity-cruises/unnamed-river-class-x6.html
/ships/celebrity-cruises/zenith.html
```

**Ships — Holland America (40+ pages, no H1):**
```
/ships/holland-america-line/amsterdam.html
/ships/holland-america-line/edam.html
/ships/holland-america-line/eurodam.html
/ships/holland-america-line/koningsdam.html
/ships/holland-america-line/leerdam.html
/ships/holland-america-line/maartensdijk.html
/ships/holland-america-line/maasdam.html
/ships/holland-america-line/nieuw-amsterdam-ii.html
/ships/holland-america-line/nieuw-amsterdam-iii.html
/ships/holland-america-line/nieuw-amsterdam-iv.html
/ships/holland-america-line/nieuw-amsterdam-v.html
/ships/holland-america-line/nieuw-amsterdam.html
/ships/holland-america-line/nieuw-statendam.html
/ships/holland-america-line/none-announced.html
/ships/holland-america-line/noordam-ii.html
/ships/holland-america-line/noordam-iii.html
/ships/holland-america-line/noordam-iv.html
/ships/holland-america-line/noordam.html
/ships/holland-america-line/oosterdam.html
/ships/holland-america-line/p-caland.html
/ships/holland-america-line/potsdam.html
/ships/holland-america-line/prinsendam-i.html
/ships/holland-america-line/prinsendam-ii.html
/ships/holland-america-line/rijndam-ii.html
/ships/holland-america-line/rijndam.html
/ships/holland-america-line/rotterdam-iv.html
/ships/holland-america-line/rotterdam-v.html
/ships/holland-america-line/rotterdam-vi.html
/ships/holland-america-line/rotterdam.html
/ships/holland-america-line/ryndam.html
/ships/holland-america-line/statendam-ii.html
/ships/holland-america-line/statendam-iii.html
/ships/holland-america-line/statendam.html
/ships/holland-america-line/veendam-ii.html
/ships/holland-america-line/veendam-iii.html
/ships/holland-america-line/veendam-iv.html
/ships/holland-america-line/veendam.html
/ships/holland-america-line/volendam-ii.html
/ships/holland-america-line/volendam-iii.html
/ships/holland-america-line/volendam.html
/ships/holland-america-line/w-a-scholten.html
/ships/holland-america-line/westerdam-i.html
/ships/holland-america-line/westerdam-ii.html
```

**Restaurants (5 pages, no H1):**
```
/restaurants/aquadome-market.html
/restaurants/cafe-two70.html
/restaurants/el-loco-fresh.html
/restaurants/giovannis.html
/restaurants/pearl-cafe.html
```

**Other (3 pages, no H1):**
```
/packing.html
/solo/in-the-wake-of-grief-meta.html
/tools/cruise-tipping-calculator.html
/ships/rooms.html
```

---

### Short/Missing Meta Descriptions (164 pages)
Meta description present but too short (<70 chars), or missing entirely.

**No meta at all (4 pages):**
```
/packing.html
/ports/falmouth-jamaica.html
/restaurants/dining-activities.html
/ships/rooms.html
```

**Short meta — Ports (46 pages):**
```
/ports/anchorage.html        /ports/antigua.html
/ports/bilbao.html           /ports/bimini.html
/ports/busan.html            /ports/buzios.html
/ports/cape-horn.html        /ports/cephalonia.html
/ports/colon.html            /ports/dunedin.html
/ports/durban.html           /ports/gatun-lake.html
/ports/greenock.html         /ports/guadeloupe.html
/ports/guayaquil.html        /ports/hamburg.html
/ports/harvest-caye.html     /ports/hilo.html
/ports/hurghada.html         /ports/jamaica.html
/ports/juneau.html           /ports/ketchikan.html
/ports/kodiak.html           /ports/la-spezia.html
/ports/lautoka.html          /ports/luanda.html
/ports/malaga.html           /ports/marthas-vineyard.html
/ports/maui.html             /ports/port-moresby.html
/ports/port-said.html        /ports/progreso.html
/ports/puerto-caldera.html   /ports/royal-beach-club-antigua.html
/ports/royal-beach-club-cozumel.html  /ports/royal-beach-club-nassau.html
/ports/santa-marta.html      /ports/santos.html
/ports/sihanoukville.html    /ports/southampton.html
/ports/taormina.html         /ports/tonga.html
/ports/tortola.html          /ports/ushuaia.html
/ports/venice.html           /ports/wrangell.html
```

**Short meta — Restaurants (75 pages):** `/restaurants/absolute-zero.html`, `/restaurants/aqua-theater.html`, `/restaurants/aqua80.html`, `/restaurants/aquadome.html`, `/restaurants/aquatheater.html`, `/restaurants/ben-and-jerrys.html`, `/restaurants/big-daddys-hideaway-heist.html`, `/restaurants/blades.html`, `/restaurants/boardwalk.html`, `/restaurants/cant-stop-the-rock.html`, `/restaurants/carnival/alchemy-bar.html`, `/restaurants/carnival/big-chicken.html`, `/restaurants/carnival/chefs-table.html`, `/restaurants/carnival/emerils-bistro.html`, `/restaurants/carnival/guys-burger-joint.html`, `/restaurants/carnival/guys-pig-and-anchor.html`, `/restaurants/carnival/rudis-seagrill.html`, `/restaurants/carousel.html`, `/restaurants/casino-royale.html`, `/restaurants/casino.html`, `/restaurants/category-6-waterpark.html`, `/restaurants/cats.html`, `/restaurants/central-park.html`, `/restaurants/chefs-table.html`, `/restaurants/chill-island.html`, `/restaurants/comedy-live.html`, `/restaurants/crowns-edge.html`, `/restaurants/encore-ice-show.html`, `/restaurants/flowrider.html`, `/restaurants/freeze-frame.html`, `/restaurants/frozen-in-time.html`, `/restaurants/giovannis-italian-kitchen.html`, `/restaurants/giovannis.html`, `/restaurants/grease.html`, `/restaurants/hiro.html`, `/restaurants/ice-odyssey.html`, `/restaurants/intense.html`, `/restaurants/jamies-italian.html`, `/restaurants/lous-jazz-n-blues.html`, `/restaurants/msc/butchers-cut.html`, `/restaurants/msc/chefs-garden-kitchen.html`, `/restaurants/msc/lapprodo-restaurant.html`, `/restaurants/msc/lippocampo-restaurant.html`, `/restaurants/msc/main-dining-room.html`, `/restaurants/msc/marketplace-buffet.html`, `/restaurants/music-hall.html`, `/restaurants/ncl/bulls-eye-bar.html`, `/restaurants/ncl/cagneys-steakhouse.html`, `/restaurants/ncl/cocos.html`, `/restaurants/ncl/hudsons.html`, `/restaurants/ncl/osheehans.html`, `/restaurants/ncl/shakers-martini-bar.html`, `/restaurants/ncl/shanghais-noodle-bar.html`, `/restaurants/ncl/syd-normans-pour-house.html`, `/restaurants/on-air-club.html`, `/restaurants/perfect-storm.html`, `/restaurants/ritas-cantina.html`, `/restaurants/royal-promenade.html`, `/restaurants/royal-theater.html`, `/restaurants/sky-lounge.html`, `/restaurants/social-100.html`, `/restaurants/solarium-bistro.html`, `/restaurants/spectras-cabaret.html`, `/restaurants/splashaway-bay.html`, `/restaurants/spotlight-karaoke.html`, `/restaurants/starburst-sol.html`, `/restaurants/studio-b.html`, `/restaurants/surfside.html`, `/restaurants/the-attic.html`, `/restaurants/thrill-island.html`, `/restaurants/torque.html`, `/restaurants/two70.html`, `/restaurants/virgin/lolas-library.html`, `/restaurants/virgin/richards-rooftop.html`, `/restaurants/wild-cool-swingin.html`

**Short meta — Ships (39 pages):** Carnival, Celebrity, HAL, MSC, RCL, Regent, Virgin Voyages ships — see full list in `/tmp/itw_all_issues_full.txt`

**Short meta — Tools (3 pages):**
```
/tools/cruise-tipping-calculator.html
/tools/release-notes.html
/tools/ship-tracker.html
```

---

### Placeholder Content (278 pages)
Pages exist and return 200 but contain placeholder/stub content — not ready for public.

**Cruise Line Index Pages (7):**
```
/cruise-lines.html
/cruise-lines/carnival.html
/cruise-lines/celebrity.html
/cruise-lines/holland-america.html
/cruise-lines/msc.html
/cruise-lines/norwegian.html
/cruise-lines/princess.html
/cruise-lines/virgin.html
```

**Tool/Index Pages (6):**
```
/drink-calculator.html
/ports.html
/restaurants.html
/search.html
/ships.html
/stateroom-check.html
/tools/port-day-planner.html
/tools/port-tracker.html
/tools/ship-size-atlas.html
/tools/ship-tracker.html
/travel.html
```

**Ships — Carnival (38 pages):** All current Carnival fleet + retired ships — full placeholder content

**Ships — Celebrity (23 pages):** Most Celebrity fleet pages are placeholder

**Ships — Holland America (40+ pages):** Most HAL fleet pages are placeholder

**Ships — Other lines (placeholder):**
- Costa: `costa-venezia`
- Cunard: `queen-anne`, `queen-elizabeth`, `queen-mary-2`, `queen-victoria`
- Explora Journeys: `explora-i`, `explora-iii` through `explora-vi`
- Norwegian: `norwegian-bliss`, `norwegian-encore`, `norwegian-escape`, `norwegian-gem`, `norwegian-spirit`
- Oceania: `allura`, `marina`, `riviera`, `sirena`, `vista`
- Princess: full fleet (16 ships)
- RCL: `nordic-empress`, `nordic-prince`, `oasis-of-the-seas`, `radiance-of-the-seas`, `song-of-america`, `song-of-norway`, `sovereign-of-the-seas`, `splendour-of-the-seas`, `sun-viking`, `viking-serenade` + multiple TBN future ships
- Regent: `prestige`
- Silversea: full fleet (12 ships)
- Virgin Voyages: `resilient-lady`, `scarlet-lady`, `valiant-lady`

**Ports — Placeholder (76 pages):** `barbados`, `cape-town`, `capri`, `catania`, `cochin`, `colombo`, `dravuni`, `dunedin`, `flam`, `freeport`, `funchal`, `geiranger`, `goa`, `guam`, `ha-long-bay`, `hamburg`, `harvest-caye`, `helsinki`, `heraklion`, `ho-chi-minh-city`, `hobart`, `honningsvag`, `hvar`, `ilhabela`, `isafjordur`, `jacksonville`, `jakarta`, `jeju`, `kagoshima`, `kiel`, `kirkwall`, `kona`, `kotor`, `kuala-lumpur`, `la-coruna`, `langkawi`, `le-havre`, `lerwick`, `lifou`, `liverpool`, `lombok`, `lyttelton`, `maputo`, `marthas-vineyard`, `melbourne`, `messina`, `milford-sound`, `mindelo`, `misty-fjords`, `mobile`, `monte-carlo`, `montreal`, `moorea`, `muscat`, `ocho-rios`, `okinawa`, `philipsburg`, `ponta-delgada`, `portofino`, `recife`, `rostock`, `royal-beach-club-antigua`, `royal-beach-club-cozumel`, `safaga`, `salalah`, `samana`, `sharm-el-sheikh`, `st-lucia`, `tauranga`, `virgin-gorda`, `walvis-bay`, `wellington`, `whittier`, `zanzibar`

---

### Missing Page Titles (8 pages)
`<title>` tag absent — these pages have no browser tab name or SEO title signal.
```
/restaurants/giovannis-italian-kitchen.html
/restaurants/hooked-seafood.html
/restaurants/izumi-in-the-park.html
/restaurants/sabor-taqueria.html
/restaurants/solarium-bar.html
/restaurants/solarium-cafe.html
/ships/rcl/oasis-class-ship-tbn-2028.html
/solo/in-the-wake-of-grief-meta.html
```

---

### Other Flagged Issues (11 pages)
Content anomalies that didn't fit above categories — require manual review:
```
/packing.html                                            (no H1 + no meta + other)
/ports/beijing.html                                      (no H1 + redirect-style page)
/ports/falmouth-jamaica.html                             (no H1 + no meta)
/ports/kyoto.html                                        (no H1 + redirect-style page)
/restaurants/seaplex.html                                (content anomaly)
/ships/celebrity-cruises/celebrity-xpedition.html        (content anomaly)
/ships/celebrity-cruises/unnamed-edge-class.html         (content anomaly)
/ships/celebrity-cruises/unnamed-project-nirvana.html    (content anomaly)
/ships/celebrity-cruises/unnamed-river-class-x6.html     (content anomaly)
/ships/rooms.html                                        (no H1 + no meta + placeholder)
/tools/ship-size-atlas.html                              (broken links + placeholder)
```

---

## 📊 Summary

| Category | Count | Priority |
|----------|-------|----------|
| Broken Atlas links (critical tool) | 1 tool, ~40 links | 🔴 CRITICAL |
| 404 pages | 1 confirmed (Norwegian Encore) | 🟠 HIGH |
| Redirect path mismatches | 2 (Celebrity, HAL) | 🟠 HIGH |
| GT data mismatch | 1 confirmed, audit needed | 🟡 MEDIUM |
| Missing H1 | 120 pages | 🟡 MEDIUM |
| Short/missing meta | 164 pages | 🟡 MEDIUM |
| Placeholder content | 278 pages | 🟡 MEDIUM |
| Missing page title | 8 pages | 🟡 MEDIUM |
| Other anomalies | 11 pages | 🔵 LOW |

**Total pages with at least one issue: ~450 of 1,229 crawled**
**Pages clean: ~779**

---

## 🛠 Quick Wins (.htaccess — 3 lines, deploy immediately)

```apache
# Fix Ship Size Atlas + Celebrity + HAL path mismatches
RewriteRule ^ships/royal-caribbean/(.*)$ /ships/rcl/$1 [R=301,L]
RewriteRule ^ships/celebrity/(.*)$ /ships/celebrity-cruises/$1 [R=301,L]
RewriteRule ^ships/holland-america/(.*)$ /ships/holland-america-line/$1 [R=301,L]
```

---

## 📁 Raw Data

- Full URL list: `/tmp/itw_urls.txt` (1,229 URLs)
- Full audit JSON: `/tmp/itw_full_audit.json`
- All issues categorized: `/tmp/itw_all_issues_full.txt`
- Screenshots: `/tmp/itw_screenshots/` (9 templates captured)
- Session audit log: `memory/itw-audit-2026-05-13.md`
