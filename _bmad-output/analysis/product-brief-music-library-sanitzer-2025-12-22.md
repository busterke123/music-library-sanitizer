---
stepsCompleted: [1, 2, 3, 4, 5]
inputDocuments:
  - _bmad-output/analysis/research/technical-music-library-data-enrichment-research-2025-12-22.md
  - _bmad-output/analysis/brainstorming-session-2025-12-19T170840.md
workflowType: 'product-brief'
lastStep: 5
project_name: 'music-library-sanitzer'
user_name: 'Arne.driesen'
date: '2025-12-22'
---

# Product Brief: music-library-sanitzer

**Date:** 2025-12-22  
**Author:** Arne.driesen

---

<!-- Content will be appended sequentially through collaborative workflow steps -->

## Executive Summary

`music-library-sanitzer` is a tool for hobby DJs using Rekordbox that reduces DJ set preparation time by automatically enriching a Rekordbox library with the missing, high-impact metadata that currently requires manual effort—especially cue points, energy level tagging, and vocal detection.

The product focuses on making playlists “set-ready” faster by generating trustworthy, at-a-glance track signals and pre-analysis outputs that integrate back into the user’s existing Rekordbox workflow, rather than requiring a new ecosystem.

---

## Core Vision

### Problem Statement

Hobby DJs who manage local music libraries in Rekordbox spend excessive time preparing sets because critical performance metadata—especially cue points, energy levels, and whether a track contains vocals—is missing or must be verified manually.

### Problem Impact

- Set preparation is time-intensive and repetitive, requiring track-by-track listening and manual tagging.
- The lack of vocal indicators increases the risk of vocal clashes during transitions.
- Missing or inconsistent energy signals makes it harder to build and adjust a compelling set arc.

**Success definition:** reduce the time needed to prepare a DJ set by ~50% for hobby DJs using Rekordbox.

### Why Existing Solutions Fall Short

- Rekordbox libraries often have basic tags (artist/title/genre), but don’t reliably provide the specific “performance metadata” hobby DJs need most.
- Manual cue point creation, energy tagging, and vocal checks don’t scale as users add new music.
- Existing workflows force DJs to choose between time spent preparing and confidence during performance.

### Proposed Solution

A library enrichment application that ingests a user’s Rekordbox library, analyzes tracks to generate:

- suggested cue points (usable defaults and/or templates)
- energy level tags
- vocal presence detection

…and writes the enriched metadata back into the Rekordbox library so DJs can continue prepping and performing in Rekordbox with less manual work.

### Key Differentiators

- **Rekordbox-first integration:** improves the existing library instead of forcing DJs into a new workflow.
- **Prep-time impact focus:** prioritizes the three biggest time sinks (cue points, energy tagging, vocal detection) rather than broad, low-value metadata.
- **Trust + usability:** aims to provide signals DJs can rely on quickly, reducing the need for full-track verification.

## Target Users

### Primary Users

**Primary Persona: “Michel” (Hobby DJ on Rekordbox)**

- **Context:** Bedroom DJ who plays mostly private parties (and occasional small gatherings).
- **Library profile:** ~4,000 tracks and growing (~20 new tracks/week).
- **Sources:** Live sets from other DJs and Spotify-driven discovery.
- **Workflow today:** Prepares per playlist for a specific session/gig; spends significant time creating hot cues, tagging energy, and checking for vocals.

**Motivations & goals**

- Build a set that feels intentional: good flow, consistent energy arc, and fewer “surprises” during transitions.
- Reduce repetitive prep work while keeping confidence high during the set.

**Pain points (most acute)**

- Cue point creation is slow and manual.
- Energy tagging is missing and requires listening/guessing.
- Vocal presence is not obvious, increasing risk of vocal clashes.

**Non-negotiables / trust requirements**

- Wrong cue points are the least tolerable failure mode: bad cues directly degrade performance and trust.

### Secondary Users

N/A (single user group targeted initially).

### User Journey

**Discovery**

- Finds the tool while searching for ways to reduce Rekordbox prep time (hot cues, energy tagging, vocal detection).

**Onboarding**

- Connects/selects an existing Rekordbox library.
- Chooses a target scope (e.g., one playlist, recently added tracks, or entire library).

**Core Usage**

- Runs enrichment on a playlist before a party.
- Reviews generated hot cues and metadata, focusing review time on low-confidence tracks.

**Success moment (“aha!”)**

- Opens Rekordbox and immediately sees many tracks with usable hot cues, a visible energy level, and a vocal indicator—reducing manual steps while keeping confidence.

**Long-term routine**

- Runs enrichment regularly for newly added tracks.
- Keeps the library “set-ready” with minimal ongoing effort as new music is added.

## Success Metrics

### User Success Metrics

- **Prep time efficiency (primary):** Reduce preparation time per hour of set time by ~50%.
  - **Baseline (current):** ~4 hours prep for ~30 tracks.
  - **Scope of “prep time”:** cue points, energy tagging, vocal detection, ordering, and beatgrids.

- **Manual correction rate (quality guardrail):** Fewer than **5% of tracks** require manual correction after enrichment.
  - Applies especially to cue points (highest trust risk), and also to vocal detection.

- **Workflow fit:** Users can complete their prep inside Rekordbox using the enriched library (no “tool switching” required beyond running enrichment).

### Business Objectives

- **Adoption:** Get hobby Rekordbox DJs to regularly run enrichment as part of their weekly “new tracks” workflow.
- **Trust:** Establish confidence that enrichment outputs are reliable enough to reduce full-track verification.

### Key Performance Indicators

- **Time saved per set-hour:** (prep time before − prep time after) / set hours.
- **Prep time per 30-track playlist:** median minutes/hours spent on prep tasks.
- **Correction rate:** % tracks in a playlist that require manual edits after running enrichment.
- **Cue correctness proxy:** % tracks where the user changes/removes generated hot cues.
- **Vocal flag correctness proxy:** % tracks where the user flips the generated vocal indicator.
- **Weekly active enrichment:** % users who run enrichment weekly (aligned to ~20 new tracks/week).

## MVP Scope

### Core Features

- **Playlist-scoped enrichment:** User selects a single Rekordbox playlist to enrich (enables small-batch testing and iteration).
- **Hot cue generation (MVP):** Automatically generate and write hot cues back into the Rekordbox library for tracks in the selected playlist.
- **Simple run flow:** Run enrichment without a separate review queue; users review/adjust in Rekordbox if needed.

### Out of Scope for MVP

- Any analysis that Rekordbox already performs (e.g., existing built-in analyses).
- Energy level tagging.
- Vocal detection.
- Broader “nice-to-have” metadata enrichment beyond the explicitly targeted missing performance metadata.

### MVP Success Criteria

- Achieves meaningful prep-time reduction on a per-playlist basis while keeping quality acceptable.
- **Quality guardrail:** fewer than **5% of tracks** in an enriched playlist require manual hot-cue correction.
- Users can run the tool as part of normal Rekordbox prep (playlist-based workflow) without adopting a new library system.

### Future Vision

- **Phase 2:** Add energy level tagging written back into the Rekordbox library.
- **Phase 3:** Add vocal detection (vocal presence indicator) written back into the Rekordbox library.
