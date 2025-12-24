# Story 3.5: Restore from backup and report verification

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As Michel,
I want to restore the Rekordbox library from a selected backup with verification,
so that I can recover confidently after a failed or risky run.

## Acceptance Criteria

1. Given a backup identifier exists in the configured backup directory
   When I run a restore command with that identifier
   Then the Rekordbox library file is restored from that backup
   And the command reports completion.
2. Given a restore completes
   When the command reports results
   Then it includes verification signals (at minimum file presence and size match; hash is optional).
3. Given a backup identifier does not exist or is unreadable
   When I run the restore command
   Then the tool fails with a non-zero exit code and a clear error message
   And it does not perform a partial restore.
4. Given the backup directory cannot be accessed or the copy fails
   When I run restore
   Then the tool fails closed with ExitCode.FAILURE and a clear error message.
5. Given a restore is invoked
   When it runs
   Then it does not run write-plan preconditions, backup creation, or retention cleanup.

## Tasks / Subtasks

- [x] Task 1: Add restore helper in the Rekordbox IO layer (AC: 1, 2, 3, 4, 5)
  - [x] Subtask 1.1: Implement `restore_backup` in `src/music_library_sanitzer/rekordbox/backup.py`.
  - [x] Subtask 1.2: Resolve backup directory by identifier under `backup_root` and ensure it exists.
  - [x] Subtask 1.3: Validate the expected backup file is present (same filename as `library_path.name`).
  - [x] Subtask 1.4: Copy the backup file to `library_path` using `copy2`.
  - [x] Subtask 1.5: Collect verification data (exists + file size match; optional hash).
  - [x] Subtask 1.6: Raise `PreconditionFailure` with stage `restore_backup` on any errors.
- [x] Task 2: Add CLI command to restore backups (AC: 1, 2, 3, 4, 5)
  - [x] Subtask 2.1: Add `restore` (or `backup-restore`) command in `src/music_library_sanitzer/cli.py`.
  - [x] Subtask 2.2: Accept backup identifier argument and use `config.backup_path`.
  - [x] Subtask 2.3: Output clear progress and verification summary on success.
  - [x] Subtask 2.4: Convert `PreconditionFailure` into ExitCode.FAILURE with error text.
  - [x] Subtask 2.5: Ensure restore path does not call preconditions, backup creation, or retention.
- [x] Task 3: Add tests (AC: 1, 2, 3, 4, 5)
  - [x] Subtask 3.1: Unit tests for restore success (copies file, reports verification info).
  - [x] Subtask 3.2: Unit tests for missing backup directory or missing backup file (raises `PreconditionFailure` stage `restore_backup`).
  - [x] Subtask 3.3: CLI test for success output and failure exit code.

## Dev Notes

### Developer Context

- Restore is a direct IO operation; it should be isolated to the Rekordbox boundary.
- Use the same naming patterns and error handling as backup creation/listing.
- Keep behavior fail-closed: any unexpected IO error aborts with ExitCode.FAILURE.

### Technical Requirements

- Backup root is `config.backup_path` (default `~/.music-library-sanitzer/backups`).
- Identifier corresponds to the backup directory name.
- Expected backup file name matches the current library filename (`library_path.name`).
- Verification must include file presence + size match; include hash if low effort.
- Do not run backup retention or write-plan preconditions during restore.

### Architecture Compliance

- Implement in Rekordbox IO layer (`src/music_library_sanitzer/rekordbox/backup.py`).
- CLI command lives in `src/music_library_sanitzer/cli.py` and only wires config + output.
- Use `PreconditionFailure` for IO errors with stage `restore_backup`.

### Library/Framework Requirements

- Use Python standard library only.
- Follow existing Typer output patterns (`typer.echo`).

### File Structure Requirements

- `src/music_library_sanitzer/rekordbox/backup.py` (restore helper).
- `src/music_library_sanitzer/cli.py` (restore command).
- `tests/unit/test_backup.py` (restore helper + CLI tests).

### Testing Requirements

- Ensure restore uses backup identifier lookup and correct error handling.
- Cover verification output (file size match) and error paths.

### Previous Story Intelligence

- Story 3.4 implemented listing and uses `PreconditionFailure` stages for IO errors.
- Reuse backup path resolution and naming conventions from `create_backup` and listing.

### Git Intelligence Summary

- Recent work touched `src/music_library_sanitzer/rekordbox/backup.py`, `src/music_library_sanitzer/cli.py`,
  and `tests/unit/test_backup.py`; follow established patterns for errors and output.

### Project Context Reference

- No `project-context.md` found in repository.

### Project Structure Notes

- Align with Rekordbox IO boundary and snake_case naming.
- No structural conflicts detected.

### References

- [Source: _bmad-output/epics.md#Story 3.5: Restore from backup and report verification]
- [Source: _bmad-output/prd.md#Functional Requirements - FR19, FR20]
- [Source: _bmad-output/architecture.md#Safety Preconditions (Fail Closed)]
- [Source: _bmad-output/architecture.md#Project Structure & Boundaries]
- [Source: _bmad-output/implementation-artifacts/3-4-list-available-backups.md]
- [Source: src/music_library_sanitzer/rekordbox/backup.py]
- [Source: src/music_library_sanitzer/cli.py]

## Dev Agent Record

### Agent Model Used

gpt-5 (Codex CLI)

### Debug Log References

create-story yolo mode
pytest: python -m pytest tests\\unit\\test_backup.py

### Completion Notes List

- Web research not required (standard library + local repo context).
- Story context derived from epics, PRD, architecture, and Story 3.4 implementation notes.
- Implemented restore helper with verification data and fail-closed errors.
- Added restore CLI command with progress + verification output.
- Tests: python -m pytest tests\\unit\\test_backup.py.
- Code review fixes: atomic restore, identifier validation, verification failures treated as errors, tests updated.

### File List

- _bmad-output/implementation-artifacts/3-5-restore-from-backup-and-report-verification.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- src/music_library_sanitzer/rekordbox/backup.py
- src/music_library_sanitzer/cli.py
- tests/unit/test_backup.py

## Change Log

- 2025-12-24: Added restore helper, CLI command, and tests for backup restore.
- 2025-12-24: Code review fixes for restore safety and validation.
