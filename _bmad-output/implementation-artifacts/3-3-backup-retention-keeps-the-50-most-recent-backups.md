# Story 3.3: Backup retention keeps the 50 most recent backups

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As Michel,
I want old backups cleaned up automatically,
so that disk usage stays bounded without manual cleanup.

## Acceptance Criteria

1. Given more than 50 backups exist in the backup directory
   When a new backup is created successfully
   Then the tool removes older backups to keep only the 50 most recent
   And it reports which backups were removed (at least in logs).

## Tasks / Subtasks

- [x] Task 1: Implement backup retention pruning in the backup module
  - [x] Subtask 1.1: Add a helper that lists backup directories and orders them from newest to oldest.
  - [x] Subtask 1.2: Keep the newest 50 backup directories and remove the rest.
  - [x] Subtask 1.3: Return the removed backup identifiers for logging.
  - [x] Subtask 1.4: Raise a fail-closed error if pruning fails (permissions, IO errors).
- [x] Task 2: Wire retention into the write-run path
  - [x] Subtask 2.1: Run retention immediately after a successful backup creation and before write side effects.
  - [x] Subtask 2.2: Log the removed backup identifiers in the CLI output or logs.
- [x] Task 3: Add retention tests
  - [x] Subtask 3.1: Create >50 dummy backup directories and assert only the newest 50 remain.
  - [x] Subtask 3.2: Assert the removed list matches the pruned backups (oldest first).
  - [x] Subtask 3.3: Assert retention is a no-op when <=50 backups exist.
  - [x] Subtask 3.4: Assert retention failures raise a PreconditionFailure with stage `backup_retention`.

## Dev Notes

### Developer Context

- Backup creation is implemented in `src/music_library_sanitzer/rekordbox/backup.py` and invoked from `_run_write_side_effects` in `src/music_library_sanitzer/cli.py`.
- Story 3.2 added fail-closed preconditions and backup creation; retention must run after a successful backup and before any write side effects.
- Retention is explicitly out of scope for 3.2 and is now required by Story 3.3.

### Technical Requirements

- Use `config.backup_path` as the backup root directory.
- Retention should keep the newest 50 backup directories; remove all older ones.
- Sort backups by the timestamp encoded in the directory name (`YYYYMMDD-HHMMSS`), with `-N` suffixes treated as the same timestamp but later than the base timestamp. If a directory name does not parse, fall back to filesystem mtime for ordering and still include it in retention.
- Run retention only after a backup is successfully created, and before any write side effects.
- If retention fails (unable to list, delete, or access backups), raise `PreconditionFailure` with stage `backup_retention` and abort before writing.
- Report which backups were removed (at least in logs). Prefer returning a list of removed identifiers to the CLI so logging stays in the user-facing layer.

### Architecture Compliance

- Keep retention logic inside the Rekordbox IO boundary (`src/music_library_sanitzer/rekordbox/`), not in pipeline planning code.
- Preserve the precondition order: validate config + resolve playlist + build plan + create backup + retention prune + apply writes + report outcomes.
- Maintain fail-closed behavior via `PreconditionFailure` for retention errors.

### Library/Framework Requirements

- Use Python standard library only (e.g., `pathlib`, `shutil`, `datetime`, `os`).
- Do not add dependencies or network calls.

### File Structure Requirements

- Update `src/music_library_sanitzer/rekordbox/backup.py` to add retention logic and expose a helper for CLI logging.
- If a new helper is exported, update `src/music_library_sanitzer/rekordbox/__init__.py` accordingly.
- Update `src/music_library_sanitzer/cli.py` to log removed backups after retention runs.

### Testing Requirements

- Add unit tests under `tests/unit/test_backup.py` for retention pruning and failure behavior.
- Use `tmp_path` to create fake backup directories with deterministic names and mtimes.
- Verify no backups are removed when the count is <=50.
- Verify removal order and logging list are deterministic based on the sort rules.

### Previous Story Intelligence

- Story 3.2 introduced `create_backup` in `src/music_library_sanitzer/rekordbox/backup.py` and wired it into `_run_write_side_effects` in `src/music_library_sanitzer/cli.py`.
- Backup creation is skipped when there are no planned changes and for dry-run runs; retention should follow the same gating (only after successful backup).
- Precondition failures should surface as `ExitCode.FAILURE` without invoking write-side effects.

### Git Intelligence Summary

- Recent commits modified `src/music_library_sanitzer/rekordbox/backup.py`, `src/music_library_sanitzer/cli.py`, and unit tests around preconditions and backups.
- Follow the established patterns for fail-closed errors and the precondition order in `src/music_library_sanitzer/pipeline/executor.py` and `src/music_library_sanitzer/cli.py`.

### Project Context Reference

- No `project-context.md` found in repository.

### References

- [Source: _bmad-output/epics.md#Story 3.3: Backup retention keeps the 50 most recent backups]
- [Source: _bmad-output/prd.md#Functional Requirements - FR17]
- [Source: _bmad-output/architecture.md#Safety Preconditions (Fail Closed)]
- [Source: _bmad-output/architecture.md#State Directory Structure (Authoritative)]
- [Source: _bmad-output/architecture.md#Project Structure & Boundaries]
- [Source: _bmad-output/implementation-artifacts/3-2-create-a-pre-write-backup-for-write-runs.md]
- [Source: src/music_library_sanitzer/rekordbox/backup.py]
- [Source: src/music_library_sanitzer/cli.py]

## Dev Agent Record

### Agent Model Used

gpt-5 (Codex CLI)

### Debug Log References

- create-story yolo mode

### Completion Notes List

- Story context generated from epics, PRD, architecture, previous story, and recent git history.
- Web research not performed (network restricted).
- Validation report generated: _bmad-output/implementation-artifacts/validation-report-20251223-171422.md.
- Implemented backup retention sorting, pruning, and fail-closed errors with CLI logging.
- Added unit coverage for retention ordering, pruning, no-op behavior, and failure handling.
- Code review fixes: corrected suffix ordering for zero-padded backups, added mtime fallback ordering test, and added CLI retention logging test.
- Tests not re-run after code review fixes.
- Tests run: `python -m pytest tests/unit/test_backup.py`.
- Full test suite: `python -m pytest` (46 passed, 1 skipped: console entrypoint not in PATH).

### File List

- _bmad-output/implementation-artifacts/3-3-backup-retention-keeps-the-50-most-recent-backups.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- src/music_library_sanitzer/rekordbox/backup.py
- src/music_library_sanitzer/cli.py
- tests/unit/test_backup.py

### Change Log

- 2025-12-23: Added backup retention pruning with fail-closed handling and logging; added retention tests.
- 2025-12-23: Code review fixes for retention ordering edge cases and logging coverage.

### Senior Developer Review (AI)

- MEDIUM: Zero-padded suffixes could sort equal to base timestamp; fixed to ensure any suffix sorts later than base.
- MEDIUM: No mtime fallback coverage for unparseable backup names; added ordering test.
- LOW: No test asserting CLI logging of pruned backups; added coverage for retention log output.

## Story Completion Status

Status: done
Completion note: Backup retention implemented; full test suite passed with 1 skipped.
