# Story 2.2: Dry-run mode shows intended changes without writing

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As Michel,
I want a --dry-run mode that previews intended changes without writing,
so that I can verify the plan safely before touching my Rekordbox library.

## Acceptance Criteria

1. Given I run `music-library-sanitzer run --playlist-id <id> --dry-run`, when the tool completes, then it reports which tracks would be changed and how (planned cue additions/updates). [Source: _bmad-output/epics.md#Story 2.2: Dry-run mode shows intended changes without writing]
2. Given I run in `--dry-run` mode, when the tool completes, then it performs zero writes to the Rekordbox library and creates no backup. [Source: _bmad-output/epics.md#Story 2.2: Dry-run mode shows intended changes without writing]

## Tasks / Subtasks

- [x] Implement dry-run flow in run execution (AC: 1, 2)
  - [x] Build and persist the write plan, then render per-track planned changes without invoking backup or write steps (AC: 1, 2)
  - [x] Ensure human-readable output lists planned cue additions/updates per track (AC: 1)
- [x] Wire CLI/config to respect dry-run in execution (AC: 1, 2)
  - [x] Use existing `Config.dry_run` flag in pipeline execution to branch behavior (AC: 2)
- [x] Add tests for dry-run behavior (AC: 1, 2)
  - [x] Dry-run does not create backups or write to Rekordbox (AC: 2)
  - [x] Dry-run output includes per-track planned changes (AC: 1)

## Dev Notes

- Dry-run must never create backups or write to Rekordbox; it should only build and report the plan. [Source: _bmad-output/epics.md#Story 2.2: Dry-run mode shows intended changes without writing]
- Planning remains deterministic and must run before any side effects (validate config + playlist -> build plan -> backup -> write -> report). [Source: _bmad-output/architecture.md#Safety Preconditions (Fail Closed)]
- Use existing plan models and planner (`src/music_library_sanitzer/pipeline/models.py`, `src/music_library_sanitzer/pipeline/planner.py`) and persistence (`src/music_library_sanitzer/state/runs.py`). [Source: _bmad-output/architecture.md#Complete Project Directory Structure]
- Keep IO boundaries: Rekordbox reads/writes and backups stay in `rekordbox/`; dry-run must skip write path entirely. [Source: _bmad-output/architecture.md#Project Structure & Boundaries]

### Project Structure Notes

- Use `snake_case` for modules, files, functions, variables, and config keys. [Source: _bmad-output/architecture.md#Naming Patterns]
- Follow existing layout under `src/music_library_sanitzer/` for pipeline, state, and CLI integration. [Source: _bmad-output/architecture.md#Complete Project Directory Structure]

### References

- _bmad-output/epics.md#Story 2.2: Dry-run mode shows intended changes without writing
- _bmad-output/architecture.md#Safety Preconditions (Fail Closed)
- _bmad-output/architecture.md#Project Structure & Boundaries
- _bmad-output/architecture.md#Complete Project Directory Structure
- _bmad-output/architecture.md#Naming Patterns

## Developer Context

### Technical Requirements

- Dry-run reports per-track planned changes and never performs writes or backup creation. [Source: _bmad-output/epics.md#Story 2.2: Dry-run mode shows intended changes without writing]
- Write plan is still produced and can be persisted for auditing. [Source: _bmad-output/architecture.md#Format Patterns]

### Architecture Compliance

- Maintain deterministic planning core and isolate IO side effects behind boundaries. [Source: _bmad-output/architecture.md#Project Structure & Boundaries]
- Fail-closed ordering is mandatory; dry-run branches before backup/write steps. [Source: _bmad-output/architecture.md#Safety Preconditions (Fail Closed)]

### Library / Framework Requirements

- CLI uses Typer + Rich for output; align dry-run output with existing CLI patterns. [Source: _bmad-output/architecture.md#Selected Starter: uv + Typer]
- Exit codes must follow existing exit code mapping and never return success on fail-closed precondition errors. [Source: _bmad-output/architecture.md#Error Handling & Exit Codes]

### File Structure Requirements

- Execution flow likely touches `src/music_library_sanitzer/cli.py` and pipeline modules under `src/music_library_sanitzer/pipeline/`. [Source: _bmad-output/architecture.md#Complete Project Directory Structure]
- If new persistence or reporting helpers are needed, place them under `src/music_library_sanitzer/state/`. [Source: _bmad-output/architecture.md#Complete Project Directory Structure]

### Testing Requirements

- Add tests that assert dry-run produces planned change output and skips backup/write calls. [Source: _bmad-output/epics.md#Story 2.2: Dry-run mode shows intended changes without writing]

### Previous Story Intelligence

- Story 2.1 added deterministic plan models, planner, persistence, and tests; reuse `build_write_plan` + `persist_write_plan` for dry-run output. [Source: _bmad-output/implementation-artifacts/2-1-build-a-deterministic-write-plan-from-inputs.md]
- Planner already encodes dry_run in input hash via config snapshot; ensure dry-run flows keep that behavior. [Source: src/music_library_sanitzer/pipeline/planner.py]

### Git Intelligence Summary

- Recent commits centered on CLI output and exit-code semantics (`src/music_library_sanitzer/cli.py`, `src/music_library_sanitzer/exit_codes.py`). Align dry-run output and exit behavior with these patterns. [Source: src/music_library_sanitzer/cli.py]
- Playlist resolution and tracking are in `src/music_library_sanitzer/rekordbox/playlist.py`; dry-run should operate on resolved playlists without writes. [Source: src/music_library_sanitzer/rekordbox/playlist.py]

## Project Context Reference

- No `project-context.md` found in repo; follow architecture and epics as the source of truth.

## Story Completion Status

- Status: done
- Completion note: Ultimate context engine analysis completed - comprehensive developer guide created.

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

None.

### Implementation Plan

- Build and persist the write plan during dry-run, then render per-track planned changes.
- Branch run execution on `Config.dry_run` to skip processing paths.
- Add unit coverage for dry-run formatting and execution branching.

### Completion Notes List

- Dry-run must report planned changes without writing or backup.
- Reuse plan models + planner + persistence from Story 2.1.
- Align output and exit codes with existing CLI patterns.
- Implemented dry-run branch that renders planned changes and exits successfully without processing.
- Added dry-run planned-changes formatter with per-track cue details.
- Adjusted dry-run to only list planned changes and to use plan-derived exit code status.
- Tests: `python3 -m pytest` (28 passed, 1 skipped: console entrypoint not available).

### File List

- _bmad-output/implementation-artifacts/2-2-dry-run-mode-shows-intended-changes-without-writing.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- src/music_library_sanitzer/cli.py
- tests/unit/test_dry_run.py

### Change Log

- Added dry-run planned changes output and execution branching, plus unit tests. (2025-12-23)
- Updated dry-run output filtering and exit-code derivation from plan statuses. (2025-12-23)
