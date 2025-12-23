# Story 2.3: Idempotency rules prevent cue thrashing on reruns

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As Michel,
I want reruns to avoid duplicating or thrashing tool-created cues,
so that repeated enrichment is safe and stable.

## Acceptance Criteria

1. Given a successful previous run created tool-provenanced cues, when I rerun the tool with unchanged inputs, then the plan results in “unchanged” outcomes for those tracks. [Source: _bmad-output/epics.md#Story 2.3: Idempotency rules prevent cue thrashing on reruns]
2. Given a successful previous run created tool-provenanced cues, when I rerun the tool with unchanged inputs, then it does not create duplicate cues or move cues between slots unexpectedly. [Source: _bmad-output/epics.md#Story 2.3: Idempotency rules prevent cue thrashing on reruns]

## Tasks / Subtasks

- [x] Define idempotency rules for reruns in the write-planning flow (AC: 1, 2)
  - [x] Compare proposed cue plan to existing tool-provenanced cues and mark unchanged outcomes when no diffs (AC: 1, 2)
  - [x] Ensure identical inputs produce identical plan outputs (ordering, slots, metadata) (AC: 1, 2)
- [x] Capture and load provenance needed to detect tool-created cues (AC: 1, 2)
  - [x] Add or extend a provenance index in state for cue ownership detection (AC: 1, 2)
- [x] Update planner/executor to classify track outcomes as unchanged when idempotent (AC: 1)
- [x] Add tests for idempotency rules and no-thrashing behavior (AC: 1, 2)

## Dev Notes

- Idempotency requires comparing current library cues + provenance with planned cues to avoid duplicates or slot churn. [Source: _bmad-output/epics.md#Story 2.3: Idempotency rules prevent cue thrashing on reruns]
- Planning remains deterministic and must run before any side effects (validate config + playlist -> build plan -> backup -> write -> report). [Source: _bmad-output/architecture.md#Safety Preconditions (Fail Closed)]
- Keep deterministic planning logic in `src/music_library_sanitzer/pipeline/planner.py` and represent cue changes via `WritePlan`/`TrackPlan`. [Source: _bmad-output/architecture.md#Project Structure & Boundaries]
- Rekordbox read/write and backups must remain isolated behind `src/music_library_sanitzer/rekordbox/` boundaries. [Source: _bmad-output/architecture.md#Project Structure & Boundaries]

### Project Structure Notes

- Use `snake_case` for modules, files, functions, variables, and config keys. [Source: _bmad-output/architecture.md#Naming Patterns]
- Follow existing layout under `src/music_library_sanitzer/` for pipeline, state, and Rekordbox boundaries. [Source: _bmad-output/architecture.md#Complete Project Directory Structure]

### References

- _bmad-output/epics.md#Story 2.3: Idempotency rules prevent cue thrashing on reruns
- _bmad-output/architecture.md#Safety Preconditions (Fail Closed)
- _bmad-output/architecture.md#Project Structure & Boundaries
- _bmad-output/architecture.md#Complete Project Directory Structure
- _bmad-output/architecture.md#Naming Patterns

## Developer Context

### Technical Requirements

- Reruns with unchanged inputs must yield “unchanged” outcomes for tracks with tool-provenanced cues. [Source: _bmad-output/epics.md#Story 2.3: Idempotency rules prevent cue thrashing on reruns]
- Do not duplicate tool-created cues or move cues between slots when inputs/config are unchanged. [Source: _bmad-output/epics.md#Story 2.3: Idempotency rules prevent cue thrashing on reruns]
- Deterministic planning is a hard requirement; input hash stability must be preserved. [Source: _bmad-output/architecture.md#Write Plan Format (Deterministic)]

### Architecture Compliance

- Keep planning pure/deterministic; side effects stay in Rekordbox adapters and backup layer. [Source: _bmad-output/architecture.md#Project Structure & Boundaries]
- Fail-closed precondition order remains mandatory for write runs. [Source: _bmad-output/architecture.md#Safety Preconditions (Fail Closed)]

### Library / Framework Requirements

- CLI uses Typer + Rich for output; align outcome reporting and exit codes with existing CLI patterns. [Source: _bmad-output/architecture.md#Selected Starter: uv + Typer]
- Exit code mapping must remain consistent with existing exit-code semantics. [Source: _bmad-output/architecture.md#Error Handling & Exit Codes]

### File Structure Requirements

- Planning logic lives in `src/music_library_sanitzer/pipeline/` and state/provenance data under `src/music_library_sanitzer/state/`. [Source: _bmad-output/architecture.md#Project Structure & Boundaries]
- Rekordbox IO remains isolated under `src/music_library_sanitzer/rekordbox/`. [Source: _bmad-output/architecture.md#Project Structure & Boundaries]

### Testing Requirements

- Add unit tests that show unchanged inputs produce unchanged outcomes and no duplicate cue actions. [Source: _bmad-output/epics.md#Story 2.3: Idempotency rules prevent cue thrashing on reruns]
- Ensure tests cover stable ordering of track plans and slot decisions across reruns. [Source: _bmad-output/architecture.md#Write Plan Format (Deterministic)]

### Previous Story Intelligence

- Story 2.2 established dry-run behavior and write-plan persistence; reuse the existing plan models and planner to surface unchanged outcomes. [Source: _bmad-output/implementation-artifacts/2-2-dry-run-mode-shows-intended-changes-without-writing.md]
- Preserve deterministic `inputs_hash` generation in `build_write_plan` while extending plan logic for idempotency. [Source: src/music_library_sanitzer/pipeline/planner.py]

### Git Intelligence Summary

- Recent work concentrated in `src/music_library_sanitzer/pipeline/`, `src/music_library_sanitzer/cli.py`, and tests around write plans and dry-run. Align idempotency changes with these modules. [Source: git log 5d70c9d..3a6e6b8]
- Playlist resolution and track id handling live in `src/music_library_sanitzer/rekordbox/playlist.py`; reuse existing track ids for idempotency comparisons. [Source: git show 3330bb1]

### Latest Technical Information

- No external research performed (network restricted). Rely on internal architecture and epic guidance for this story.

## Project Context Reference

- No `project-context.md` found in repo; architecture and epics are the source of truth.

## Story Completion Status

- Status: ready-for-dev
- Completion note: Ultimate context engine analysis completed - comprehensive developer guide created.

## Dev Agent Record

### Agent Model Used

GPT-5 (Codex)

### Debug Log References

None.

### Implementation Plan

- Extend planning logic to incorporate tool-provenanced cue detection and unchanged outcomes.
- Add or extend provenance storage in state to determine cue ownership across runs.
- Add unit tests to enforce stable reruns and no cue thrashing.

### Completion Notes List

- Deterministic planning is mandatory; preserve input hash stability.
- Idempotency relies on comparing planned cues against tool-provenanced cues.
- No changes should move cues between slots on identical inputs.
- Tests: `python3 -m pytest`
- Code review fixes: add provenance hash to inputs, include cue source in comparisons, and persist provenance updates from plans.
- Tests: `python3 -m pytest tests/unit/test_idempotency.py tests/unit/test_write_plan.py tests/unit/test_dry_run.py`

### File List

- _bmad-output/implementation-artifacts/2-3-idempotency-rules-prevent-cue-thrashing-on-reruns.md
- _bmad-output/implementation-artifacts/2-4-regeneration-updates-only-tool-created-cues-when-needed.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- src/music_library_sanitzer/cli.py
- src/music_library_sanitzer/pipeline/planner.py
- src/music_library_sanitzer/state/provenance.py
- tests/unit/test_idempotency.py

### Change Log

- Created story context for idempotency rules and no-thrashing reruns. (2025-12-23)
- Implemented provenance-backed idempotency checks with tests. (2025-12-23)
- Code review fixes applied for provenance hashing and persistence. (2025-12-23)
