# Story 3.4: List available backups

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As Michel,
I want to list available backups with timestamps and identifiers,
so that I can choose a restore point confidently.

## Acceptance Criteria

1. Given backups exist in the configured backup directory
   When I run a CLI command to list backups
   Then the tool outputs each backup with at least a timestamp and identifier.
2. Given multiple backups exist
   When I list backups
   Then results are ordered from newest to oldest using the same timestamp and suffix rules as retention.
3. Given a backup directory name does not match the expected timestamp pattern
   When I list backups
   Then the tool still includes it, orders it using filesystem mtime, and outputs an identifier.
4. Given no backups exist
   When I list backups
   Then the tool prints a clear "no backups found" message and exits successfully.
5. Given the backup directory cannot be accessed
   When I list backups
   Then the tool fails with a non-zero exit code and a clear error message.

## Tasks / Subtasks

- [ ] Task 1: Add backup listing helper in the Rekordbox IO layer (AC: 1, 2, 3, 5)
  - [ ] Subtask 1.1: Create a `BackupEntry` data shape (namedtuple/dataclass) with identifier, timestamp, and path.
  - [ ] Subtask 1.2: Reuse `list_backup_directories` ordering rules and parse timestamps from directory names.
  - [ ] Subtask 1.3: For unparseable names, fall back to mtime for timestamp and ordering.
  - [ ] Subtask 1.4: Raise `PreconditionFailure` with stage `list_backups` on access errors.
- [ ] Task 2: Add CLI command to list backups (AC: 1, 2, 4, 5)
  - [ ] Subtask 2.1: Add `backups` (or `backup-list`) command in `src/music_library_sanitzer/cli.py`.
  - [ ] Subtask 2.2: Use `config.backup_path` to list backups; do not create directories or run retention.
  - [ ] Subtask 2.3: Print each backup with timestamp and identifier; if none, print "No backups found."
  - [ ] Subtask 2.4: Surface `PreconditionFailure` as ExitCode.FAILURE with a clear error message.
- [ ] Task 3: Add tests (AC: 1, 2, 3, 4, 5)
  - [ ] Subtask 3.1: Unit tests for listing order and mtime fallback in `tests/unit/test_backup.py`.
  - [ ] Subtask 3.2: Test "no backups" output behavior (helper or CLI-level).
  - [ ] Subtask 3.3: CLI test for output formatting and error handling (likely in `tests/unit/test_backup.py`).

## Dev Notes

### Developer Context

- Listing backups is a read-only action; it must not create backup folders or trigger retention.
- Reuse the same ordering logic already implemented for retention in `src/music_library_sanitzer/rekordbox/backup.py`.
- Keep CLI output responsibility in `src/music_library_sanitzer/cli.py`.

### Technical Requirements

- Backup root is `config.backup_path` (default `~/.music-library-sanitzer/backups`).
- Identifier should be the backup directory name; timestamp should be parsed from `YYYYMMDD-HHMMSS(-N)`.
- Use mtime as a fallback timestamp and ordering when the name is unparseable.
- Return results newest to oldest, consistent with retention sorting rules.
- Access errors should raise `PreconditionFailure` with stage `list_backups`.

### Architecture Compliance

- Implement listing in the Rekordbox IO layer (`src/music_library_sanitzer/rekordbox/`).
- Do not add side effects in pipeline or CLI beyond printing results.
- Keep fail-closed behavior for IO errors (ExitCode.FAILURE).

### Library/Framework Requirements

- Use Python standard library only.
- Follow existing Typer/Rich CLI patterns (use `typer.echo` for output).

### File Structure Requirements

- Add listing helper in `src/music_library_sanitzer/rekordbox/backup.py`.
- If exported, update `src/music_library_sanitzer/rekordbox/__init__.py`.
- Add a new CLI command in `src/music_library_sanitzer/cli.py`.

### Testing Requirements

- Cover ordering and mtime fallback logic in `tests/unit/test_backup.py`.
- Add coverage for empty backup directories and CLI output formatting.
- Ensure error paths raise `PreconditionFailure` with stage `list_backups`.

### Previous Story Intelligence

- Story 3.3 added deterministic backup ordering and retention logic; reuse those sort rules.
- Retention logic raises `PreconditionFailure` with stage `backup_retention`; listing should use its own stage.
- Backup creation and retention are wired in `_run_write_side_effects` in `src/music_library_sanitzer/cli.py`.

### Git Intelligence Summary

- Recent changes touched `src/music_library_sanitzer/rekordbox/backup.py`, `src/music_library_sanitzer/cli.py`,
  and `tests/unit/test_backup.py`; follow the established patterns for errors and logging.

### Project Context Reference

- No `project-context.md` found in repository.

### Project Structure Notes

- Align with existing Rekordbox IO boundary and snake_case naming.
- No structural conflicts detected.

### References

- [Source: _bmad-output/epics.md#Story 3.4: List available backups]
- [Source: _bmad-output/prd.md#Functional Requirements - FR18]
- [Source: _bmad-output/architecture.md#Safety Preconditions (Fail Closed)]
- [Source: _bmad-output/architecture.md#State Directory Structure (Authoritative)]
- [Source: _bmad-output/architecture.md#Project Structure & Boundaries]
- [Source: _bmad-output/implementation-artifacts/3-3-backup-retention-keeps-the-50-most-recent-backups.md]
- [Source: src/music_library_sanitzer/rekordbox/backup.py]
- [Source: src/music_library_sanitzer/cli.py]

## Dev Agent Record

### Agent Model Used

gpt-5 (Codex CLI)

### Debug Log References

create-story interactive mode

### Completion Notes List

- Web research not required (standard library + local repo context).
- Story context derived from epics, PRD, architecture, and Story 3.3 implementation notes.

### File List

- _bmad-output/implementation-artifacts/3-4-list-available-backups.md
