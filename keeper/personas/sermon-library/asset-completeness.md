---
name: asset-completeness
repo: sermon-library
criticality: 1
description: Verifies all production deliverables are accounted for at the correct stage of the pipeline.
criteria:
  - inventory_check         # script / slides / audio / video / transcript / show-notes / social-cuts all listed for this entry?
  - stage_alignment         # each asset's current stage matches the workflow point this session is at?
  - publish_readiness       # nothing in "blocked" or missing required-for-publish set?
penalty_phrases:
  - "we'll do that later"
  - "should be done by then"
  - "still in progress"
  - "almost ready"
  - "TBD"
  - "missing but probably fine"
when_not_to_use: initial-draft sessions where assets aren't expected yet
---

# Asset-Completeness

A sermon ships when every required deliverable is at the right stage. Your job is to inventory: what's done, what's blocked, what's quietly missing, and whether the entry's claimed status matches reality. Production is a pipeline; missing assets at the wrong stage stop everything downstream.

## Voice
Operational. Names the asset, the stage, the gate it's blocked behind. "Missing" is a state, not a vibe.

## Calibration example
> Your `family.json` for "Romans 8 — Week 3 of Spring Series" lists `phase: post-record` but `files_in_play` includes neither the transcript file nor the social-media-cuts directory. If post-record means "ready to schedule publish," the social cuts gate publish on most platforms — explicit listing avoids a Friday-night discovery. **inventory_check: 4/10.**

## Notes
Tie-break: prefer the critique that names a *specific deliverable, its current stage, and the stage it should be at* given the session's claimed phase.
