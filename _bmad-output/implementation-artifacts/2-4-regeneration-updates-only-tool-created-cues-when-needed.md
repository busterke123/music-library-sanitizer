# Story 2.4: Regeneration updates only tool-created cues when needed

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As Michel,
I want the tool to update previously tool-created cues when regeneration is needed,
so that improvements can be applied without touching my manual cues.

## Acceptance Criteria

1. Given a track has tool-created cues from a prior run, when a regeneration trigger occurs (e.g., config change or algorithm update), then the plan may update only tool-created cues according to the overwrite policy. [Source: _bmad-output/epics.md#Story 2.4: Regeneration updates only tool-created cues when needed]
2. Given a track has tool-created cues from a prior run, when a regeneration trigger occurs, then it never overwrites user-created cues. [Source: _bmad-output/epics.md#Story 2.4: Regeneration updates only tool-created cues when needed]

## Tasks / Subtasks

- [x] Define regeneration triggers and comparison rules in planning (AC: 1, 2)
  - [x] Determine the signal for regeneration (config hash, algorithm version, stage config) (AC: 1)
  - [x] Compare planned cues with tool-provenanced cues to decide updates vs unchanged (AC: 1)
- [x] Enforce overwrite policy for tool-created cues only (AC: 1, 2)
  - [x] Ensure user-created cues are never selected for overwrite, even during regeneration (AC: 2)
- [x] Persist and load provenance needed to identify tool-created cues (AC: 1, 2)
- [x] Add tests for regeneration behavior and policy enforcement (AC: 1, 2)

## Dev Notes

- Regeneration must only update cues that were created by this tool; manual cues are never overwritten. [Source: _bmad-output/epics.md#Story 2.4: Regeneration updates only tool-created cues when needed]
- Planning remains deterministic and must run before any side effects (validate config + playlist -> build plan -> backup -> write -> report). [Source: _bmad-output/architecture.md#Safety Preconditions (Fail Closed)]
- Keep deterministic planning logic in `src/music_library_sanitzer/pipeline/` and isolate Rekordbox IO in `src/music_library_sanitzer/rekordbox/`. [Source: _bmad-output/architecture.md#Project Structure & Boundaries]

### Project Structure Notes

- Use `snake_case` for modules, files, functions, variables, and config keys. [Source: _bmad-output/architecture.md#Naming Patterns]
- Follow existing layout under `src/music_library_sanitzer/` for pipeline, state, and Rekordbox boundaries. [Source: _bmad-output/architecture.md#Complete Project Directory Structure]

### References

- _bmad-output/epics.md#Story 2.4: Regeneration updates only tool-created cues when needed
- _bmad-output/architecture.md#Safety Preconditions (Fail Closed)
- _bmad-output/architecture.md#Project Structure & Boundaries
- _bmad-output/architecture.md#Complete Project Directory Structure
- _bmad-output/architecture.md#Naming Patterns

## Developer Context

### Technical Requirements

- Regeneration updates must apply only to tool-created cues; user-created cues are never overwritten. [Source: _bmad-output/epics.md#Story 2.4: Regeneration updates only tool-created cues when needed]
- Define a deterministic regeneration trigger (e.g., config hash or algorithm version) and use it to decide when updates are allowed. [Source: _bmad-output/epics.md#Story 2.4: Regeneration updates only tool-created cues when needed]
- Preserve deterministic planning: unchanged inputs + no regeneration trigger => unchanged outcomes. [Source: _bmad-output/architecture.md#Write Plan Format (Deterministic)]

### Architecture Compliance

- Planning logic remains pure; IO side effects (writes, backups) stay behind Rekordbox adapters. [Source: _bmad-output/architecture.md#Project Structure & Boundaries]
- Fail-closed precondition order remains mandatory for write runs. [Source: _bmad-output/architecture.md#Safety Preconditions (Fail Closed)]

### Library / Framework Requirements

- CLI uses Typer + Rich for output; align with existing output and exit code patterns. [Source: _bmad-output/architecture.md#Selected Starter: uv + Typer]
- Exit code mapping must remain consistent with existing exit-code semantics. [Source: _bmad-output/architecture.md#Error Handling & Exit Codes]

### File Structure Requirements

- Planning logic belongs in `src/music_library_sanitzer/pipeline/` and state/provenance under `src/music_library_sanitzer/state/`. [Source: _bmad-output/architecture.md#Project Structure & Boundaries]
- Rekordbox read/write stays under `src/music_library_sanitzer/rekordbox/`. [Source: _bmad-output/architecture.md#Project Structure & Boundaries]

### Testing Requirements

- Add tests covering regeneration triggers and overwrite policy enforcement (tool-created cues only). [Source: _bmad-output/epics.md#Story 2.4: Regeneration updates only tool-created cues when needed]
- Include cases where user-created cues exist alongside tool-created cues to assert no overwrites. [Source: _bmad-output/epics.md#Story 2.4: Regeneration updates only tool-created cues when needed]

### Previous Story Intelligence

- Story 2.3 defined idempotency rules to avoid cue thrashing; align regeneration logic to update only tool-provenanced cues when triggers occur. [Source: _bmad-output/implementation-artifacts/2-3-idempotency-rules-prevent-cue-thrashing-on-reruns.md]
- Preserve deterministic inputs hash behavior in `build_write_plan` while adding regeneration-aware comparisons. [Source: src/music_library_sanitzer/pipeline/planner.py]

### Git Intelligence Summary

- Recent commits focused on deterministic write plan modeling and dry-run behavior (`src/music_library_sanitzer/pipeline/`, `src/music_library_sanitzer/cli.py`). Extend these patterns for regeneration updates. [Source: git log 5d70c9d..3a6e6b8]
- Playlist resolution and track id handling live in `src/music_library_sanitzer/rekordbox/playlist.py`; reuse track ids for cue comparisons. [Source: git show 3330bb1]

### Latest Technical Information

- No external research performed (network restricted). Rely on internal architecture and epic guidance for this story.

## Project Context Reference

- No `project-context.md` found in repo; architecture and epics are the source of truth.

## Story Completion Status

- Status: done
- Completion note: Regeneration gating and overwrite policy implemented with provenance-aware triggers and tests.

## Dev Agent Record

### Agent Model Used

GPT-5 (Codex)

### Debug Log References

None.

### Implementation Plan

- Define regeneration trigger and cue comparison rules in planning.
- Enforce overwrite policy for tool-created cues only and keep manual cues protected.
- Add tests for regeneration decisions and overwrite policy enforcement.

### Completion Notes List

- Regeneration must never overwrite user-created cues.
- Deterministic planning must be preserved; regeneration only when trigger applies.
- Use provenance to identify tool-created cues and avoid slot churn.
- Regeneration trigger uses generation_id derived from config snapshot + plan version.
- Tests: `python3 -m pytest` (33 passed, 1 skipped), `python3 -m pytest tests/unit/test_idempotency.py` (7 passed)
- Code review fixes: persist generation_id even without cue updates; guard regeneration when provenance is unverified.

### File List

- _bmad-output/implementation-artifacts/2-4-regeneration-updates-only-tool-created-cues-when-needed.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- src/music_library_sanitzer/cli.py
- src/music_library_sanitzer/pipeline/planner.py
- src/music_library_sanitzer/state/provenance.py
- tests/unit/test_idempotency.py

### Change Log

- Created story context for regeneration updates and overwrite policy enforcement. (2025-12-23)
- Implemented regeneration trigger gating and overwrite policy with tests. (2025-12-23)
- Applied code review fixes for generation_id persistence and verified-provenance guard. (2025-12-23)
