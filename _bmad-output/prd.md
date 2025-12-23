---
stepsCompleted: [1, 2, 3, 4, 7, 8, 9, 10]
inputDocuments:
  - _bmad-output/analysis/product-brief-music-library-sanitzer-2025-12-22.md
  - _bmad-output/analysis/research/technical-music-library-data-enrichment-research-2025-12-22.md
  - _bmad-output/analysis/brainstorming-session-2025-12-19T170840.md
documentCounts:
  briefs: 1
  research: 1
  brainstorming: 1
  projectDocs: 0
workflowType: 'prd'
lastStep: 11
project_name: 'music-library-sanitzer'
user_name: 'Arne.driesen'
date: '2025-12-22T17:12:32+01:00'
---

# Product Requirements Document - music-library-sanitzer

**Author:** Arne.driesen
**Date:** 2025-12-22T17:12:32+01:00

## Executive Summary

`music-library-sanitzer` is a CLI tool for hobby DJs using Rekordbox that reduces DJ set preparation time by enriching a Rekordbox library with missing, high-impact performance metadata—starting with hot cue points (MVP), and potentially expanding later to energy tagging and vocal presence detection.

The tool is Rekordbox-first: it analyzes local tracks and writes generated metadata back into the Rekordbox library so DJs can keep prepping and performing inside Rekordbox, instead of adopting a new ecosystem. The primary success measure is a meaningful reduction in prep time while maintaining high trust, with cue point quality as the strictest guardrail.

### What Makes This Special

- **Rekordbox-first integration:** improves the existing library and workflow instead of introducing a new one.
- **Prep-time impact focus:** prioritizes the highest-effort missing signals (starting with hot cues).
- **Trust + quality guardrails:** minimizes harmful failure modes (especially incorrect cues), aiming to reduce verification time without increasing performance risk.

## Project Classification

**Technical Type:** cli_tool  
**Domain:** general  
**Complexity:** low  
**Project Context:** Greenfield - new project

This will start as a scriptable CLI workflow (playlist-scoped enrichment), with the option to add a UI later if needed.

## Success Criteria

### User Success

- **Prep time reduction (primary):** For a 30-track playlist, reduce total prep time by **50% (median)** compared to baseline.
- **Workflow fit:** You can complete prep inside Rekordbox using the enriched library; the tool is only used to run enrichment.

### Business Success

- **Personal value:** You choose to keep using the tool for new tracks/playlists because it consistently saves time without adding risk.
- **Sustained use:** You run enrichment at least **weekly** as part of your normal “new tracks” workflow.

### Technical Success

- **Safe writes:** No corruption or destructive modifications to the Rekordbox library beyond intended cue additions/updates.
- **Repeatability:** Re-running enrichment on the same playlist is deterministic (no random drift) unless inputs changed.
- **Provider safety:** Any external providers (if used) respect rate limits and use caching to avoid blocking/throttling.

### Measurable Outcomes

- **Median prep time (30-track playlist):** (Before) vs (After) tracked across multiple playlists.
- **Cue correction rate (quality guardrail):** **< 5% of tracks** require manual edits where you **edit/delete any generated hot cue**.
- **Adoption proxy:** # of weekly runs; # of tracks enriched per week.

## Product Scope

### MVP - Minimum Viable Product

- **Playlist-scoped enrichment:** Select a Rekordbox playlist and run enrichment for its tracks.
- **Hot cue generation (MVP focus):** Generate and write hot cues back into the Rekordbox library.
- **CLI-first workflow:** Scriptable command interface, no UI required for MVP.

### Growth Features (Post-MVP)

- **Energy tagging:** Generate energy level tags written back into Rekordbox.
- **Vocal presence detection:** Add a vocal indicator to reduce vocal clash risk.
- **Review/triage:** Confidence scoring + a review workflow for low-confidence tracks (optional, if needed to maintain guardrails).

### Vision (Future)

- **Set-readiness automation:** Keep the library “set-ready” with minimal ongoing effort as new music is added.
- **Faster recovery cues (optional):** Better surfacing of “safe” tracks/transitions for rapid live-set recovery (only if it fits the Rekordbox-first philosophy).

## User Journeys

**Journey 1: Michel — Turning a Playlist into “Set-Ready” (Happy Path)**
It’s Friday afternoon and Michel is prepping a playlist for a small party. He has 30 tracks selected in Rekordbox but many are missing hot cues, which means he’d normally spend hours listening, scrubbing, and placing cues by hand.

Instead, Michel runs `music-library-sanitzer` against that specific playlist. The CLI confirms which playlist will be processed, estimates run time, and begins analyzing tracks. While it runs, Michel does something else (or keeps digging for music) instead of doing repetitive prep work.

When the run completes, Michel opens Rekordbox and sees hot cues populated across the playlist. He quickly spot-checks a handful of tracks and finds that most cues are usable defaults. The “aha” moment is realizing he can start practicing transitions immediately instead of spending the night placing cues.

By the time the party starts, Michel feels more confident: he has functional cues across the playlist, and he spent dramatically less time on track-by-track preparation.

**Journey 2: Michel — Handling Low-Quality Inputs (Edge Case: Bad Tags / Hard Tracks)**
Michel adds a few tracks from different sources; some have messy metadata or unusual structure (long intros, live versions, abrupt transitions). He runs the CLI on the playlist, but a subset of tracks can’t be analyzed reliably or produce cues that feel suspicious.

The CLI surfaces which tracks were skipped or flagged (e.g., analysis failed, low confidence, or results incomplete) and leaves everything else enriched. Michel opens Rekordbox and focuses only on the flagged tracks, manually cueing those few.

The key value is containment: the tool accelerates the majority of the playlist while making it obvious where manual work is still required, preventing silent failures that would erode trust.

**Journey 3: Michel — Building a Weekly Routine (New Tracks Workflow)**
Each week, Michel adds ~20 new tracks and creates a “New This Week” (or prep) playlist. In the past, the prep backlog would pile up and he’d end up rushing cues right before a gig.

Now, Michel’s routine is: add tracks → create/refresh the prep playlist → run `music-library-sanitzer` → quick spot-check in Rekordbox. Because enrichment is playlist-scoped, the workflow stays lightweight and repeatable.

Over time, his library becomes more “set-ready by default,” and prep stops being a recurring multi-hour tax.

**Journey 4: Michel — Re-Running Enrichment Safely (Iteration Without Fear)**
Michel re-runs enrichment on the same playlist after adding/removing a few tracks or after changing tool settings. He wants confidence that re-running won’t randomly reshuffle his existing manual work or overwrite things unexpectedly.

The CLI clearly communicates what it will change (and what it won’t), behaves deterministically, and avoids destructive edits. If some cues already exist, the tool follows the defined rules (e.g., only fill missing cues, or only write to specific cue slots depending on configuration).

This journey succeeds when Michel trusts he can iterate without risking his library integrity.

### Journey Requirements Summary

These journeys reveal requirements for:

- **Playlist targeting:** Identify/select a specific Rekordbox playlist as the unit of work.
- **Batch processing UX (CLI):** Clear start/finish feedback, progress, and actionable output.
- **Failure containment:** Skip/flag hard tracks and report them; don’t silently fail.
- **Trust safeguards:** Predictable behavior on re-runs; clear rules around overwriting vs filling missing cues.
- **Workflow fit:** Results appear directly in Rekordbox with minimal extra steps.

## CLI Tool Specific Requirements

### Project-Type Overview

`music-library-sanitzer` is a scriptable, CLI-first tool designed to be run repeatedly against a specific Rekordbox playlist to generate and write hot cues into the Rekordbox library.

### Output Formats

- **Human-readable logs:** Default console output optimized for a single user running the tool locally.
- **Machine-readable output:** Provide a JSON summary output for automation, archiving, and future extensibility.

### Configuration

- Support a **configuration file** for stable settings (e.g., library locations, default behavior), with **CLI flags overriding config values**.
- Avoid interactive prompting by default to keep runs repeatable and script-friendly.

### Shell Integration

- Shell completion is **out of scope for MVP**.

### Implementation Considerations

- Provide a `--dry-run` mode to preview intended changes without writing to the Rekordbox library.
- Provide clear exit codes (success, partial success with skips, failure) to support scripting.

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Platform MVP  
**Rationale:** Prioritize a clean, extensible foundation (pipeline architecture, provenance, safe write rules, and provider adapters) so future phases (energy tagging, vocal detection, additional data sources) can be added without reworking the core.

**Resource Requirements:** 1 developer (you) with familiarity in audio analysis + CLI design + careful data writing practices.

### MVP Feature Set (Phase 1)

**Core User Journeys Supported:**
- Playlist-scoped enrichment (run against a specific Rekordbox playlist)
- Handling partial failures (skips/flags) without breaking the library
- Safe re-runs without fear (deterministic behavior + clear write rules)

**Must-Have Capabilities:**
- Rekordbox playlist targeting (identify/select a playlist deterministically)
- Hot cue generation and writing
- Provenance for tool-created cues (so the tool can recognize “its own” changes)
- Overwrite policy: **only overwrite hot cues previously created by this tool**; never overwrite user-created cues
- `--dry-run` to preview changes
- JSON summary output (machine-readable) + human-readable logs
- Stable config file with CLI flag overrides
- Clear exit codes (success / partial success / failure)

### Post-MVP Features

**Phase 2 (Post-MVP):**
- Energy tagging written back into Rekordbox
- Confidence scoring + review/triage workflow for low-confidence tracks (if needed to maintain guardrails)
- Performance improvements for larger playlists/libraries

**Phase 3 (Expansion):**
- Vocal presence detection written back into Rekordbox
- Additional enrichment sources/providers (optional, if “free-to-use” constraints remain acceptable)
- Optional UI layer (only if CLI workflow becomes a bottleneck)

### Risk Mitigation Strategy

**Technical Risks:** Incorrect or destructive library writes; unreliable identification; algorithmic cue quality.  
**Mitigation Approach:** provenance + constrained overwrite rules; `--dry-run`; deterministic runs; explicit reporting of skipped/flagged tracks.

**Market Risks:** (low, personal-use) the tool doesn’t meaningfully save time or cues require too much cleanup.  
**Validation Approach:** track “before vs after” prep time on real playlists and measure cue correction rate (<5%).

**Resource Risks:** solo dev time constraints and scope creep.  
**Contingency Approach:** keep MVP limited to playlist-scoped hot cues; defer energy/vocals/providers unless MVP guardrails are met.

## Functional Requirements

### CLI Execution & Control

- FR1: Michel can run enrichment non-interactively via CLI flags (no prompts by default).
- FR2: Michel can provide a configuration file for defaults.
- FR3: Michel can override configuration values via CLI flags.
- FR4: Michel can run the tool in `--dry-run` mode to preview intended changes without writing.
- FR5: Michel can request a machine-readable JSON summary of a run.

### Playlist Targeting & Scope

- FR6: Michel can target enrichment to a single Rekordbox playlist via a stable playlist ID.
- FR7: The system can resolve a playlist ID to the set of tracks included in that playlist at run time.
- FR8: The system can report the resolved playlist (ID and human-readable name, if available) before applying changes.

### Library Access, Backup/Restore, & Safety

- FR9: The system can read the necessary Rekordbox library data to determine current hot cues for targeted tracks.
- FR10: The system can write hot cues back into the Rekordbox library for targeted tracks.
- FR11: The system can apply a write policy that prevents overwriting user-created cues.
- FR12: The system can overwrite hot cues only when they were previously created by this tool (provenanced).
- FR13: The system can detect whether an existing hot cue was created by this tool (provenance check).
- FR14: The system can create a backup of the Rekordbox library before any write is performed.
- FR15: If backup creation fails, the system aborts the run before making any changes to the Rekordbox library.
- FR16: The system can store backups by default in `~/.music-library-sanitzer/backups` (with configurable override).
- FR17: The system can retain the **50 most recent** backups and remove older backups beyond this limit.
- FR18: Michel can list available backups (at minimum: timestamp and identifier).
- FR19: Michel can restore the Rekordbox library from a selected backup.
- FR20: After a restore, the system can confirm restore completion (verification/reporting).

### Hot Cue Generation

- FR21: The system can generate hot cue candidates for each eligible track in the playlist.
- FR22: The system can decide which cue slots to fill based on the configured policy and existing cues.
- FR23: The system can write the chosen cues in a way that they are visible and usable inside Rekordbox.
- FR24: The system can report which tracks would be changed (and how) in `--dry-run`.

### Run Reporting & Observability (Local)

- FR25: The system can output human-readable run progress and completion status to the console.
- FR26: The system can produce a per-track outcome (e.g., updated, unchanged, skipped, failed).
- FR27: The system can list skipped/flagged tracks and a reason for each (e.g., analysis failed, unsupported file).
- FR28: The system can output a summary including counts: processed, updated, unchanged, skipped, failed.
- FR29: The system can return distinct exit codes for: success, partial success (some skips/failures), and failure.

### Determinism & Re-runs

- FR30: Re-running enrichment with the same inputs and configuration produces consistent results (no random drift).
- FR31: The system can avoid duplicating or thrashing tool-created cues across re-runs (idempotent behavior).
- FR32: The system can update previously tool-created cues when regeneration is needed (within the overwrite policy).

### Extensibility (Platform MVP)

- FR33: The system can support multiple enrichment stages as a pipeline (e.g., cues now; energy/vocals later).
- FR34: The system can enable/disable pipeline stages via configuration.
- FR35: The system can record provenance per generated artifact to support future safe updates and debugging.
- FR36: The system can add new enrichment stages in the future without changing existing CLI workflows for running a playlist.

### Provider Integration (Future-Compatible, Optional at MVP)

- FR37: The system can support optional external providers via adapters (enabled/disabled by config).
- FR38: When providers are used, the system can cache results to reduce repeat calls (capability requirement, not implementation).

## Non-Functional Requirements

### Performance

- The system must complete playlist enrichment runs eventually (no strict runtime SLA for MVP), while providing progress feedback so the user can tell the process is still advancing.

### Reliability & Data Safety

- The system must **fail closed**: on any unexpected condition, it must abort **before writing** to the Rekordbox library.
- The system must never partially write changes if preconditions are not met (e.g., cannot create backup, cannot validate write plan, cannot access library safely).
- The system must preserve library integrity as the highest priority (no silent failures; clear error reporting on abort).

### Security & Privacy

- The system must minimize exposure of local library data: any network usage must be intentional, bounded, and observable (clear indication that network calls are enabled/active).
- The system must avoid sending unnecessary personal/local file information to external services (principle: least data necessary).

### Integration (External Providers)

- When network calls are enabled, the system must behave respectfully toward external services (e.g., rate limiting and caching to reduce repeated calls) and degrade gracefully when providers are unavailable (abort before writes if provider dependency is required for a safe plan; otherwise skip provider-dependent enrichment and report clearly).
