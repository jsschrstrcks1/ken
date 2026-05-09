# Soul of `flickersofmajesty`

> *Soli Deo Gloria.* Fine art photography that catches divine light in creation.

The storefront. Ken Baker's photographs sold as canvas, framed, and metal prints — built so AI assistants can describe them honestly to a buyer who's looking for the right print for a specific room.

---

## Identity

`flickersofmajesty` is the **fine-art photography e-commerce site** at [flickersofmajesty.com](https://flickersofmajesty.com). Each photograph is sold as a print in canvas, framed, or metal formats across multiple sizes. The fulfillment model is dropshipping — the photographer captures the image, the print lab produces it on demand, the customer receives it.

The repo is the only **commercial** site in the family. The recipe repos are family treasures, the sermons are pastoral work, the cruise blog is hospitality, the sheep flock is stewardship. This one is a business — and it's run with the same theological framing as the rest of the household. The first line of the CLAUDE.md is *Soli Deo Gloria*.

The site's English title — *Flickers of Majesty* — appears in the `llms.txt` of the `ken` repo as Ken Baker's photography project, "*capturing divine light in creation.*" The aesthetic premise is theological: the photograph is not the majesty; it is a flicker of it.

## What it actually is

1. **A static photography storefront** — pure HTML + CSS + vanilla JS. No build step. No framework. Drop the directory on Cloudflare Pages, Netlify, or Vercel and it works.
2. **The FOM-Lite Protocol** — a content protocol governing every page. AI-first AND human-first; AI scaffolding hidden by design; never compromise the user experience for AI optimization. Adapted wholesale from the **ITW-Lite Protocol** built for the `InTheWake` cruise blog.
3. **Product pages** at `products/*.html` — each photograph gets its own page with images, format/size selector, fit-guidance ("good for north-light living rooms; less ideal for south-facing rooms with strong glare"), full Schema.org Product markup, and FAQ.
4. **Category pages** at `categories/*.html` — collection landing pages with hero, fit-guidance for the *category* as a whole, product grid, FAQ.
5. **Standards documents** at `standards/` — `main-standards.md`, `product-standards.md`, `category-standards.md`. The page-shape rules are codified, not improvised.
6. **AI breadcrumbs** — HTML comments invisible to humans, parsed by AI assistants:

   ```html
   <!-- ai-breadcrumbs: product | landscape-photography | mountain-photography -->
   <!-- ai-fit-guidance: Good for: X. Not for: Y -->
   <!-- ai-price-range: $X - $Y USD -->
   ```

   These are documentation for crawlers and assistants. The README's rule for them is unambiguous: *"They must always reflect the truth of the page — never use them to inflate or game search."*

7. **A FOM-Lite Protocol spec** at `admin/claude/FOM-LITE_PROTOCOL.md` — the full normative document.

## Voice

**Curatorial, with the camera lowered.** The README does not call the photographs beautiful. It does not call them powerful, breathtaking, evocative, masterful, or any of the other words a photography portfolio would normally use. It says: "*A dropship photography storefront featuring fine-art prints in canvas, framed, and metal formats across multiple sizes.*" Functional, accurate, restrained.

**Refusing AI sycophancy.** The CLAUDE.md spells out the boundary: *"External models (GPT, Gemini, Grok) serve as **consultants only** — Claude remains lead author and decision-maker."* And: *"NEVER SEND: Full codebase, internal standards docs, analytics, financial data."* The repo treats AI as a hire, not a partner.

**Theology folded into commerce, not painted over it.** The site sells prints. The site is built so AI assistants can match a print to a buyer's room. The site is also explicit, in its parent repo's `llms.txt`, that the photographs are about "*divine light in creation.*" None of these things are at war. The voice holds them together by simply describing each layer accurately.

**The AI breadcrumbs rule as a confession.** "*Never use them to inflate or game search.*" One sentence in the middle of a long README. It tells you everything about the repo's posture toward SEO: there is a temptation, and the repo names the temptation, and refuses it.

## Style markers

- **Absolute URLs everywhere.** All internal links start with `https://www.flickersofmajesty.com/`. The README explains why: better AI scraping, fewer broken links, CDN-ready. The constraint is not aesthetic; it's operational.
- **WebP images only.** The only exception is the favicon. The standard is enforced at the page-template level.
- **Lighthouse accessibility 100, non-negotiable.** Keyboard nav, screen reader, WCAG AA contrast — written as ground rules, not aspirations. *"Never include placeholder images, lorem ipsum, or 'coming soon' pages in production."*
- **Performance targets stated as numbers.** LCP < 2.5s, FID < 100ms, CLS < 0.1. The repo does not say "fast"; it says how fast.
- **A "Testing checklist" of 11 items** that gates every page deploy: Lighthouse, W3C HTML, Google Rich Results, mobile breakpoints, four-browser cross-test, keyboard, screen reader, WebP, absolute URLs, FOM-Lite meta tags, AI breadcrumbs accuracy. Eleven boxes. No deploy without all eleven.
- **Three implementation levels.** Level 1 (meta tags) is foundational. Level 2 (content structure) is core. Level 3 (progressive enhancement) is planned. The repo numbers its standards.
- **CSS variables in `:root` for everything** — colors, typography, spacing, layout. No hard-coded values. The aesthetic system is centralized and themeable.

## Philosophy

### AI-first and human-first, hidden by design

This is the FOM-Lite Protocol's load-bearing axiom — adapted from ITW-Lite. Four principles:

1. **AI-first** — Structure content so AI assistants can accurately understand and recommend products.
2. **Human-first** — Never compromise the user experience for AI optimization. **When the two conflict, humans win.**
3. **Progressive enhancement** — All AI features are additive.
4. **Hidden by design** — AI-facing elements are invisible to users.

The win condition is: an assistant asked "*Show me a calming photograph for a small bedroom*" can find the right print and accurately describe its fit, **without ever scraping pixel data**, and the human buying that print never sees the AI scaffolding. Both audiences are served fully without serving them the same content.

### Truth-bound metadata

Every AI breadcrumb, every `ai:summary` meta tag, every Schema.org price must reflect the truth of the page. The README's rule is direct: *"never use them to inflate or game search."* This is the same posture as the recipe repos' "never invent" rule, applied to commerce. The temptation in e-commerce is to lie subtly to the search engine; the repo refuses.

### Page shape is a public contract

The standards documents (`main-standards.md`, `product-standards.md`, `category-standards.md`) define the required shape of every page type. Product pages must have eight specific sections in order. Category pages must have five. The repo treats page shape as a contract with both the human user and the AI assistant — predictable structure is mutual respect.

### Photography that names what it isn't

"*Good for north-light living rooms; less ideal for south-facing rooms with strong glare.*" The fit-guidance section names *who the print is not for* alongside who it's for. This is unusual in retail. It's how craft sellers talk to people who are about to spend real money. The repo turns this into a structured field with a CSS class (`.fit-guidance-poor`, orange) and a Schema.org-friendly format. **Saying "this isn't for you" is a business choice the repo encodes.**

### Adapted, not invented

The README opens its FOM-Lite section by crediting ITW-Lite from `InTheWake`. The CSS architecture, the AI-first/human-first axiom, the breadcrumb pattern — all carry over. The repo does not reinvent. It adapts a working protocol from a sister site and applies it to a different domain. Same family-wide ethic of "lift with credit" that runs through `ken`.

### Commerce in the same household register

*Soli Deo Gloria* opens the CLAUDE.md. The closing of the README is dry: *"All rights reserved © 2025–2026 Flickers of Majesty. Photographs and prints are sold under their own purchase terms. Site source code is internal and not currently open-licensed."* The faith framing and the proprietary-license framing coexist without strain. The store sells prints; the proceeds belong to the photographer; the work is offered as worship anyway.

## Technical anatomy

### Layout

```
flickersofmajesty/
├── admin/claude/FOM-LITE_PROTOCOL.md  ← full protocol spec
├── standards/
│   ├── main-standards.md              ← URLs, images, accessibility
│   ├── product-standards.md           ← product page contract
│   └── category-standards.md          ← category page contract
├── css/main.css                       ← single stylesheet w/ FOM-Lite classes
├── images/{products, categories, ...} ← WebP only
├── products/*.html                    ← product detail pages
├── categories/*.html                  ← category landing pages
├── index.html                         ← homepage (hero, featured, fit-guidance, FAQ)
├── CNAME                              ← flickersofmajesty.com
├── TODO.md                            ← active task list
├── new-skills-proposal.md
└── skills-audit.md
```

### FOM-Lite implementation

#### Level 1 — meta tags

```html
<meta name="content-protocol" content="ICP-Lite v1.0">
<meta name="ai:summary" content="...">
<meta name="ai:product-category" content="...">
<meta name="ai:use-cases" content="...">
<meta name="last-reviewed" content="YYYY-MM-DD">
```

#### Level 2 — structure

H1 + Answer Line; fit-guidance sections (good-for / not-for); product specs; FAQ with `FAQPage` schema; AI breadcrumbs as HTML comments.

#### Level 3 — progressive enhancement (planned)

No-JS baseline; static fallbacks for dynamic content; graceful degradation on older browsers.

### Schema.org coverage

| Page type | Schema |
|---|---|
| Product | `Product` (pricing, availability) |
| Category | `CollectionPage` |
| FAQ | `FAQPage` |
| All | `BreadcrumbList` |

### CSS architecture

A single `css/main.css` defines:
- Custom properties in `:root` for every color, font, spacing token, max-width.
- Named FOM-Lite classes: `.answer-line`, `.fit-guidance`, `.fit-guidance-good`, `.fit-guidance-poor`, `.product-specs`, `.faq`, `.product-grid`, `.product-card`.
- Mobile-first responsive design with breakpoints at 640 px and 1024 px.

### Multi-LLM integration

Mode: `cruising` (per `ken/orchestrator/repo-modes.json`) — the same pipeline that powers `InTheWake`. The CLAUDE.md notes that this *"may evolve into a custom `photography` mode"* but for now the cruising pipeline (Read Standards → Generate → Content (GPT) → Completeness (Gemini) → UX (Grok) → Integrate) is sufficient.

Lead: Claude (standards enforcement, file access). Memory scope: `/flickersofmajesty`.

**Context boundaries** are explicit:
- **SEND** to consultants: page requirements, content topics, SEO targets, product descriptions.
- **NEVER SEND**: full codebase, internal standards docs, analytics, financial data.

The boundary is enforced by convention; the CLAUDE.md is short on purpose so that any session can read it.

### Hosting

Static. Recommended: Cloudflare Pages (fast global edge, free tier covers it), Netlify, Vercel. The `CNAME` file pins the custom domain.

## Distinguishing marks

- **The only commercial repo in the family.** The recipes are gifts; the sermons are ministry; the photography is sold.
- **The most rigorous accessibility posture.** Lighthouse 100. Keyboard. Screen reader. WCAG AA. *Non-negotiable.*
- **The AI-first/human-first axiom written in capital letters.** "**When the two conflict, humans win.**" That sentence is repeated, in different words, in the standards docs.
- **AI breadcrumbs as a tested invariant.** Every page deploy has a checkbox for "AI breadcrumbs present and accurate." The repo treats them as load-bearing for both AI assistants and the photographer's reputation.
- **Adapted from ITW-Lite, with credit.** The protocol is not invented here; it is the second instance of a pattern. The README and CLAUDE.md both credit `InTheWake`.
- **A photo from `frenchpolynesia-1.jpeg` lives in `ken`'s root.** That photograph is part of this repo's source corpus, sitting upstream in the hub repo. The photography flows from one place but lives across multiple repos.
- **No build step. No framework. Vanilla JS.** A 2026 e-commerce site without React, without Next, without webpack. Static HTML deployed to a CDN. The repo proves the modern web doesn't need the modern web's defaults.
- **All rights reserved.** Unlike the recipe repos (AGPL v3) or `ken` (open), this one's license is closed. The site source is internal. The photographs are sold under their own purchase terms.

## Relationship to siblings

`flickersofmajesty` is the **commercial** corner of the household:

| Repo | Purpose | License | Audience |
|---|---|---|---|
| **`flickersofmajesty`** | **Print sales** | **All rights reserved** | **buyers** |
| `InTheWake` | Cruise planning hospitality | open | travelers |
| `Romans` | Sermon preparation | (depends) | pastor + congregation |
| four recipe repos | Family kitchen archive | AGPL v3 | family + curious |
| `manateecreeksheep` | Flock management | (depends) | shepherd + farm |
| `Family-History` | Genealogy | (depends) | family |
| `ken` | Hub | open | self |

The family of repos has one source of revenue, and this is it. The protocol it pioneered (ITW-Lite, then FOM-Lite) is migrating outward — `Romans` and recipe sites may eventually carry the same AI-first/human-first scaffolding, because the pattern is generic across content types.

## What would be lost

If `flickersofmajesty` disappeared, the photographer would lose the storefront, the dropshipping pipeline, and the print-sales business. The FOM-Lite Protocol would survive in `InTheWake` (its parent), but the *photography-specific* application of it — the print-format selector, the room-fit guidance, the canvas/framed/metal pricing — would have to be reinvented. The accessibility-100 posture, the testing checklist, the absolute-URL rule could all be ported to a successor, but the catalog of photographs presented under those rules would be lost.

## One-line summary

**`flickersofmajesty` is the household's photography storefront — a static, dropship, FOM-Lite-protocol-governed print store where AI assistants can recommend the right print to the right room without ever speaking marketing, where humans buy without seeing the AI scaffolding, and where commerce is offered with the same Soli Deo Gloria framing as the sermons next door.**
