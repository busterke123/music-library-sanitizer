# Story 1.5: Exit code semantics for scripting

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As Michel,
I want distinct exit codes for success, partial success, and failure,
So that I can automate enrichment in scripts safely.

## Acceptance Criteria

1. **Given** a run completes with all tracks handled successfully  
   **When** the tool exits  
   **Then** it returns the “success” exit code  
   **And** it returns “partial success” when there are any skipped/failed tracks  
   **And** it returns “failure” when a fail-closed precondition fails before writes.

## Tasks / Subtasks

- [x] Define an explicit numeric exit code mapping (AC: #1)
  - [x] Pick stable numeric codes and document them in-code (suggestion aligned with current behavior: `0=success`, `1=partial success`, `2=failure`)
  - [x] Implement as a single source of truth (e.g., `ExitCode(IntEnum)` or constants) to avoid drift between commands

- [x] Map outcomes to exit codes for `run` (AC: #1)
  - [x] If any `skipped > 0` or `failed > 0` in the final run summary → exit “partial success”
  - [x] If no skipped/failed and run completes → exit “success”
  - [x] If a fail-closed precondition fails before any write steps (e.g., config invalid, playlist resolution fails, deterministic plan cannot be built) → exit “failure”

- [x] Fail-closed taxonomy (AC: #1)
  - [x] Keep “fail closed” failures distinct from “partial success” (partial implies the run completed and produced outcomes)
  - [x] Ensure error paths do not print the final “Run Summary” block unless the run reached the reporting stage cleanly

- [x] Update and/or add tests (AC: #1)
  - [x] Unit tests for exit code mapping from `RunCounts` (or equivalent) to numeric exit code
  - [x] E2E tests:
    - success path returns `0` (existing fixture playlist, no failures)
    - fail-closed precondition returns `2` (e.g., invalid XML or missing playlist id still yields non-zero, but validate code specifically)
  - [x] Add partial-success E2E coverage once there is a deterministic way to produce a skipped/failed track without aborting (do not add “test-only” flags unless you document and justify them)

- [x] Documentation touchpoints
  - [x] Ensure `--help` or README/docs mention exit code semantics for scripting (short, stable phrasing)
  - [x] Ensure future `--json` output (Story 5.1) uses the same classification and numeric mapping

## Dev Notes

- This story is about **exit code semantics** (FR29) only; keep it independent of future write planning/backups/writes.
- Align with existing patterns:
  - Current fail-closed errors already use `typer.Exit(code=2)` for config and playlist resolution; keep this as the canonical “failure” code unless you deliberately change it everywhere.
  - The current run flow always exits `0` even if per-track failures are recorded; this story updates that to return “partial success” when appropriate.
- Maintain the safety precondition order from `_bmad-output/architecture.md`:
  - validate config + playlist id → plan → backup → write → report
  - Any failure before “report” should be treated as “failure” (not partial success).

### Previous Story Intelligence (from 1.4)

- Per-track statuses and summary counts are modeled in `src/music_library_sanitzer/run_summary.py` (`updated|unchanged|skipped|failed`).
- The run command prints “Run Summary” counts but currently exits `0` unconditionally.
- Config and playlist resolution errors currently exit `2` and are tested as non-zero in `tests/e2e/test_smoke.py`.

### Project Structure Notes

- Candidate location for exit code constants: `src/music_library_sanitzer/errors.py` or a new `src/music_library_sanitzer/exit_codes.py` (prefer keeping errors + exit code mapping close together and dependency-light).
- Keep the CLI boundary: `src/music_library_sanitzer/cli.py` should reference the shared mapping, not re-encode numeric values inline.

### References

- Epic + story definition: `_bmad-output/epics.md` (Epic 1 → Story 1.5)
- Product requirements: `_bmad-output/prd.md` (FR29 exit codes; per-track outcomes + counts)
- Architecture: `_bmad-output/architecture.md` (Exit code mapping suggestion; fail-closed rules)
- Existing run summary model: `src/music_library_sanitzer/run_summary.py`
- Sprint tracking: `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Dev Agent Record

### Agent Model Used

GPT-5.2 (Codex CLI)

### Debug Log References

- Tests: `python -m pytest` (20 passed, 1 skipped: console entrypoint not in PATH)

### Completion Notes List

- Added `ExitCode` mapping and `exit_code_for_counts` for run outcomes.
- CLI now exits with mapped codes; fail-closed errors use the failure code.
- Mark missing track IDs as skipped, enabling deterministic partial-success exits.
- Added E2E coverage for partial success and updated failure exit code assertion.

### File List

- src/music_library_sanitzer/exit_codes.py
- src/music_library_sanitzer/cli.py
- tests/e2e/test_smoke.py
- tests/unit/test_exit_codes.py
- tests/fixtures/rekordbox-missing-track-ids.xml
- _bmad-output/implementation-artifacts/sprint-status.yaml
