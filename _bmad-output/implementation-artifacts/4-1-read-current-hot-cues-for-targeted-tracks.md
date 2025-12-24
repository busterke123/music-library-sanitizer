# Story 4.1: Read current hot cues for targeted tracks

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Michel,
I want the tool to read existing hot cues for tracks in the target playlist,
so that it can plan changes safely and avoid overwriting my manual work.

## Acceptance Criteria

1. Given a playlist is resolved to a set of tracks
   When the planning phase loads track state
   Then it reads each track's existing hot cue slots and values from the Rekordbox library
   And it records slot index, start position (ms), and any label/color metadata available.
2. Given a track's cue data cannot be read (missing track id, missing track entry, or malformed cue data)
   When planning continues
   Then the track is marked as failed with a clear reason for reporting.
3. Given the Rekordbox library XML is malformed or unreadable
   When the tool attempts to read hot cues
   Then it fails closed before any write-side effects occur.
4. Given a run is in dry-run or write mode
   When hot cues are read
   Then no modifications are made to the Rekordbox library.

## Tasks / Subtasks

- [x] Task 1: Define data model for existing hot cues
  - [x] Subtask 1.1: Add a dataclass to represent an existing hot cue (slot, start_ms, label, color, source if available).
  - [x] Subtask 1.2: Decide where existing cues live in the plan (new field on TrackPlan or separate TrackState structure).
- [x] Task 2: Implement Rekordbox cue reader
  - [x] Subtask 2.1: Add a reader in `src/music_library_sanitzer/rekordbox/` that parses cue data for a list of track ids.
  - [x] Subtask 2.2: Use streaming XML parsing (ElementTree iterparse) to avoid loading the full library into memory.
  - [x] Subtask 2.3: Surface per-track read failures as structured reasons without crashing the run.
- [x] Task 3: Integrate cue data into planning
  - [x] Subtask 3.1: Update the write plan builder to include existing cue data per track.
  - [x] Subtask 3.2: Ensure idempotency logic can distinguish existing cues vs planned cues.
- [x] Task 4: Tests
  - [x] Subtask 4.1: Add a Rekordbox XML fixture containing hot cues.
  - [x] Subtask 4.2: Unit tests for cue parsing and per-track failure handling.
  - [x] Subtask 4.3: Unit tests to verify plan includes existing cues for track ids.

## Dev Notes

### Developer Context

- Playlist resolution already uses streaming XML parsing in `src/music_library_sanitzer/rekordbox/playlist.py` and returns `ResolvedPlaylist` with track ids.
- The write plan currently stores planned cues only (`CuePlan`), and defaults to empty cues for each track in `build_write_plan`.
- There is no Rekordbox cue reader yet; this story introduces a dedicated reader module under the Rekordbox boundary.

### Technical Requirements

- Parse Rekordbox XML to extract hot cue entries per track id, including slot index and timing.
- Keep the reader read-only with no side effects; all errors must be either per-track failures or hard failures for invalid XML.
- Do not add network calls or external dependencies.

### Architecture Compliance

- Keep Rekordbox IO isolated under `src/music_library_sanitzer/rekordbox/` and avoid mixing with pipeline logic. [Source: _bmad-output/architecture.md#Project Structure & Boundaries]
- Preserve deterministic planning and fail-closed behavior; malformed XML must halt before any write. [Source: _bmad-output/architecture.md#Safety Preconditions (Fail Closed)]
- Maintain snake_case naming and dataclass-based models. [Source: _bmad-output/architecture.md#Naming Patterns]

### Library/Framework Requirements

- Use Python standard library XML parsing (ElementTree) consistent with existing playlist parsing.
- No new libraries required.

### File Structure Requirements

- Add a new reader module, e.g. `src/music_library_sanitzer/rekordbox/library_reader.py` or `rekordbox/cues.py`.
- Update `src/music_library_sanitzer/pipeline/models.py` if adding an "existing cues" data structure.
- Update `src/music_library_sanitzer/pipeline/planner.py` to include existing cue data in the plan.
- Add tests under `tests/unit/` and fixtures under `tests/fixtures/`.

### Testing Requirements

- Add unit coverage for parsing cue data from a fixture file containing hot cues.
- Add a test for per-track cue read failures to ensure they become skipped/failed outcomes with reasons.
- Add tests ensuring plan output includes existing cue data for resolved tracks.

### Project Context Reference

- No `project-context.md` found in repository.

### References

- [Source: _bmad-output/epics.md#Epic 4: Generate and write hot cues with provenance + overwrite policy]
- [Source: _bmad-output/epics.md#Story 4.1: Read current hot cues for targeted tracks]
- [Source: _bmad-output/prd.md#Functional Requirements]
- [Source: _bmad-output/architecture.md#Project Structure & Boundaries]
- [Source: _bmad-output/architecture.md#Safety Preconditions (Fail Closed)]

## Dev Agent Record

### Agent Model Used

gpt-5 (Codex CLI)

### Debug Log References

- create-story normal mode

### Completion Notes List

- Story context generated from epics, PRD, and architecture.
- No project-context.md found.
- No web research performed for this story.
- Added ExistingCue model and stored existing cues on TrackPlan; planner marks cue read failures as failed actions.
- Implemented streaming Rekordbox cue reader with per-track failure reasons and malformed XML hard failure.
- Updated CLI status mapping to report failed tracks and added fixtures/tests for cue parsing and plan integration.
- Code review fixes: idempotency now skips planned cues already present in existing cues; dry-run fails closed on malformed XML; added unit tests. Tests not rerun in this pass.
- Tests: `python -m pytest`.

### File List

- _bmad-output/implementation-artifacts/4-1-read-current-hot-cues-for-targeted-tracks.md
- _bmad-output/implementation-artifacts/validation-report-20251224-122419.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- src/music_library_sanitzer/cli.py
- src/music_library_sanitzer/errors.py
- src/music_library_sanitzer/pipeline/models.py
- src/music_library_sanitzer/pipeline/planner.py
- src/music_library_sanitzer/rekordbox/cues.py
- tests/e2e/test_smoke.py
- tests/fixtures/rekordbox-hot-cues.xml
- tests/fixtures/rekordbox.xml
- tests/unit/test_dry_run.py
- tests/unit/test_idempotency.py
- tests/unit/test_rekordbox_cues.py
- tests/unit/test_write_plan.py

### Change Log

- 2025-12-24: Added Rekordbox cue reader, existing cue model/planning integration, and test coverage for cue parsing and failure reporting.
- 2025-12-24: Code review fixes for existing cue idempotency and dry-run XML failure handling; added unit tests.

## Story Completion Status

Status: done
Completion note: Existing hot cue read path implemented with plan integration; code review fixes applied; tests not rerun in this pass.
