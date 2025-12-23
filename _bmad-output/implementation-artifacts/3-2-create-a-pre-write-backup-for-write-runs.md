# Story 3.2: Create a pre-write backup for write runs

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Michel,
I want an automatic backup created before any write is applied,
so that I can recover if something goes wrong.

## Acceptance Criteria

1. Given the tool has a non-empty write plan
   When a write run begins
   Then it creates a backup at the configured location (default `~/.music-library-sanitzer/backups`)
   And if backup creation fails, the run aborts before any write.

## Tasks / Subtasks

- [x] Task 1: Implement backup creation utility under the Rekordbox IO boundary
  - [x] Subtask 1.1: Add `rekordbox/backup.py` with a single entry point to create a backup directory and copy the library file.
  - [x] Subtask 1.2: Generate a deterministic, timestamped backup folder/file name and return the resulting path.
  - [x] Subtask 1.3: Surface clear exceptions when backup creation fails (IO errors, missing library file, permissions).
- [x] Task 2: Wire backup creation into the write-run execution flow
  - [x] Subtask 2.1: Call backup creation after preconditions and before any write-side effects.
  - [x] Subtask 2.2: Skip backup creation entirely for dry-run runs.
  - [x] Subtask 2.3: Abort the run with a fail-closed error if backup creation fails.
- [x] Task 3: Tests for backup creation and fail-closed behavior
  - [x] Subtask 3.1: Unit test backup creation with a temp library file and backup dir.
  - [x] Subtask 3.2: Test that backup failures surface as failure exit codes and block write-side effects.

## Dev Notes

### Developer Context

- Write runs already use `run_write_preconditions` in `src/music_library_sanitzer/pipeline/executor.py` to validate config, resolve playlist, and build a deterministic plan; `_run_write_side_effects` in `src/music_library_sanitzer/cli.py` is currently a stub.
- Backup creation must occur after the plan is built and before any writes, to honor the precondition order. This story does not implement retention (Epic 3.3) or restore (Epic 3.5).
- Config already includes `backup_path` and defaults to `~/.music-library-sanitzer/backups` in `src/music_library_sanitzer/config/model.py`.

### Technical Requirements

- Create a backup of the Rekordbox library file before any write-side effects are executed.
- Backup location is `config.backup_path` (absolute), defaulting to `~/.music-library-sanitzer/backups`.
- If backup creation fails for any reason, abort the run before writing and return `ExitCode.FAILURE` via a fail-closed error.
- Do not create backups for dry-run executions.
- Keep backup retention logic out of scope (handled by Story 3.3).

### Architecture Compliance

- Keep backup logic inside the Rekordbox IO boundary (`src/music_library_sanitzer/rekordbox/`), not in pipeline planning or config modules.
- Maintain the precondition order: validate config + resolve playlist + build plan + create backup + apply writes + report outcomes.
- Preserve fail-closed behavior by raising `PreconditionFailure` (or a dedicated error) with stage context when backup creation fails.

### Library/Framework Requirements

- Use the existing Python stack (stdlib only) for file IO (e.g., `pathlib`, `shutil`).
- No new dependencies or network calls.

### File Structure Requirements

- Add `src/music_library_sanitzer/rekordbox/backup.py` and import it via `src/music_library_sanitzer/rekordbox/__init__.py` if needed.
- Wire backup creation in `src/music_library_sanitzer/cli.py` (or a new helper in `pipeline/executor.py`) so `_run_write_side_effects` performs backup before any writes.

### Testing Requirements

- Add unit tests under `tests/unit/` for successful backup creation using `tmp_path` fixtures.
- Add a failure-mode test that simulates an IO error or missing library file and asserts:
  - `PreconditionFailure` (or the chosen error) is raised with stage `create_backup`
  - write-side effects are not invoked
  - CLI exits with `ExitCode.FAILURE`

### Previous Story Intelligence

- Story 3.1 introduced `PreconditionFailure` and `run_write_preconditions`; write-side effects are currently stubbed and should remain behind the same fail-closed guardrails.
- Precondition failures bypass normal run summary exit code computation and must return `ExitCode.FAILURE` immediately.

### Git Intelligence Summary

- Recent work added precondition gating in `src/music_library_sanitzer/pipeline/executor.py` and a write-side effects stub in `src/music_library_sanitzer/cli.py`; follow the same pattern to insert backup creation after preconditions.
- Prior commits focused on deterministic write plans and provenance in `src/music_library_sanitzer/pipeline/planner.py` and `src/music_library_sanitzer/state/provenance.py`; do not modify plan semantics in this story.

### Project Context Reference

- No `project-context.md` found in repository.

### References

- [Source: _bmad-output/epics.md#Story 3.2: Create a pre-write backup for write runs]
- [Source: _bmad-output/prd.md#Functional Requirements - FR14, FR15, FR16]
- [Source: _bmad-output/architecture.md#Safety Preconditions (Fail Closed)]
- [Source: _bmad-output/architecture.md#Project Structure & Boundaries]
- [Source: src/music_library_sanitzer/pipeline/executor.py]
- [Source: src/music_library_sanitzer/cli.py]
- [Source: src/music_library_sanitzer/config/model.py]

## Dev Agent Record

### Agent Model Used

gpt-5 (Codex CLI)

### Debug Log References

- create-story yolo mode
- python -m pytest -q

### Completion Notes List

- Story context generated from epics, PRD, architecture, prior story, and recent git history.
- Web research not performed (network restricted).
- Backup retention and restore explicitly kept out of scope.
- Validation report generated for checklist review.
- Added `rekordbox/backup.py` to create timestamped backups and raise fail-closed errors on IO issues.
- Wired backup creation into `_run_write_side_effects` before any write-side effects.
- Added unit coverage for backup creation and fail-closed behavior; full test suite passes.
- Review fixes: skip backup when the write plan has no planned changes.
- Review fixes: avoid timestamp collisions by adding a suffix when needed.
- Review fixes: add tests for collision handling, missing library file, and no-change backup skipping.
- Tests run for review fixes: `python -m pytest`
- Note: unrelated working tree changes belong to Story 3.1 and are excluded from this story's File List.

### File List

- _bmad-output/implementation-artifacts/3-2-create-a-pre-write-backup-for-write-runs.md
- _bmad-output/implementation-artifacts/validation-report-20251223-163848.md
- src/music_library_sanitzer/cli.py
- src/music_library_sanitzer/rekordbox/backup.py
- tests/unit/test_backup.py

## Change Log

- 2025-12-23: Added pre-write backup creation and tests for fail-closed behavior.

## Story Completion Status

Status: done
Completion note: Implemented pre-write backup creation and fail-closed tests; skip backups when no planned changes; collision-safe backups; full test suite passes.
