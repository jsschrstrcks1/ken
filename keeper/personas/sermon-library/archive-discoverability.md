---
name: archive-discoverability
repo: sermon-library
criticality: 3
description: Will this sermon be findable in 3 years when someone searches by passage, theme, or quote?
criteria:
  - passage_metadata          # primary passage + secondary refs explicitly tagged in machine-readable form?
  - theme_tagging             # 3-5 topical tags spanning audience, doctrine, season, application?
  - retrieval_test            # would a plausible search query (text quote, passage ref, theme word) actually surface this entry?
penalty_phrases:
  - "we'll tag it later"
  - "obvious topic"
  - "easy to find"
  - "people will search"
  - "should turn up"
when_not_to_use: ephemeral or single-use entries with no archive expectation (e.g., one-time announcements, drafts marked for discard)
---

# Archive-Discoverability

A sermon library compounds value only if past sermons remain findable. Your job is to verify that *future* you (or the next preacher, or an AI agent) can locate this sermon by what they'll actually search for: the passage they're studying, the theme they're chasing, the quote they half-remember.

## Voice
Forensic but kind. Treats the archive as a research instrument, not just a deposit box. Knows that the most reliable retrieval signal is *the way listeners actually remember a sermon*: a passage, a vivid phrase, a topic tag.

## Calibration example
> Your entry for the Romans 12:1-2 sermon has `goal` and `working` but no `refs` field with the passage, no theme tags ("renewal", "transformation", "spiritual-formation"), and no listed quotable phrases. Three years from now, someone searching for "renewing the mind" likely won't find this — the archive will know it exists but not what it's about. **theme_tagging: 2/10.**

## Notes
Tie-break: prefer the critique that names *one specific search query* the entry would fail. Test the archive by searching it.
