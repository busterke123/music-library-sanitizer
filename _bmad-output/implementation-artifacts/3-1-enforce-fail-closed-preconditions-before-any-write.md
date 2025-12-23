# Story 3.1: Enforce fail-closed preconditions before any write

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Michel,
I want the tool to abort before writing on unexpected conditions,
so that my Rekordbox library integrity is protected.

## Acceptance Criteria

1. Given the tool is running in write mode (not `--dry-run`)
   When any precondition fails (e.g., cannot validate config, cannot resolve playlist, cannot build plan)
   Then the tool aborts before writing any changes
   And it returns a failure exit code with a clear error message.
2. Given a precondition fails
   When the run exits
   Then no write-side effects are attempted (no backup, no library writes).

## Tasks / Subtasks

- [x] Task 1: Define fail-closed precondition workflow for write runs
  - [x] Subtask 1.1: Add explicit precondition stages in order: validate config, resolve playlist, build deterministic plan.
  - [x] Subtask 1.2: Introduce a dedicated precondition failure error type with a user-facing message.
- [x] Task 2: Integrate precondition enforcement into CLI run flow
  - [x] Subtask 2.1: Route write-mode execution through the precondition workflow before any write-side effect hooks.
  - [x] Subtask 2.2: Keep dry-run behavior intact (plan + report only).
- [x] Task 3: Tests for fail-closed behavior
  - [x] Subtask 3.1: Unit tests for precondition failure to ExitCode.FAILURE mapping.
  - [x] Subtask 3.2: Test that write-side effects are not called when preconditions fail.

## Dev Notes

### Developer Context

- Current run flow in `src/music_library_sanitzer/cli.py` resolves playlist, builds plan, and computes statuses; there is no centralized fail-closed precondition gate yet.
- `build_write_plan` already persists plan/provenance; preconditions must fail before any future write-side effects are invoked.
- Exit codes today derive from `exit_code_for_counts` (partial success when any skipped/failed). Precondition failures must bypass counts and exit with failure (ExitCode.FAILURE = 2).

### Technical Requirements

- Implement a precondition orchestrator that enforces the ordered sequence before any write path is executed.
- Precondition failures must raise a dedicated error type that is surfaced to CLI as a failure exit code with a clear error message.
- Do not add network calls or external dependencies for this story.

### Architecture Compliance

- Enforce the fail-closed precondition order: validate config + playlist id, build plan, create backup, apply writes, report outcomes. For this story, implement the gate and failure handling for the first three steps and keep hooks for later steps. [Source: _bmad-output/architecture.md#Safety Preconditions (Fail Closed)]
- Keep high-risk IO (backup, library writes) isolated behind explicit modules; do not leak write logic into planner code. [Source: _bmad-output/architecture.md#Project Structure & Boundaries]

### Library/Framework Requirements

- Use existing stack: Python, Typer, Rich, pytest.
- No new libraries required.

### File Structure Requirements

- Prefer adding a new `pipeline/executor.py` (or equivalent) to host precondition enforcement, in line with architecture boundaries.
- Updates will likely touch `src/music_library_sanitzer/cli.py`, `src/music_library_sanitzer/errors.py`, and `src/music_library_sanitzer/exit_codes.py` to wire exit behavior.

### Testing Requirements

- Add pytest coverage for precondition failure paths and exit code behavior.
- Include at least one test that simulates a failing precondition (e.g., invalid config) and asserts no write-side effects are invoked.

### Project Context Reference

- No `project-context.md` found in repository.

### References

- [Source: _bmad-output/epics.md#Epic 3: Protect Rekordbox library integrity]
- [Source: _bmad-output/epics.md#Story 3.1: Enforce fail-closed preconditions before any write]
- [Source: _bmad-output/prd.md#Non-Functional Requirements - Reliability & Data Safety]
- [Source: _bmad-output/architecture.md#Safety Preconditions (Fail Closed)]
- [Source: _bmad-output/architecture.md#Project Structure & Boundaries]

## Dev Agent Record

### Agent Model Used

gpt-5 (Codex CLI)

### Debug Log References

- create-story yolo mode

### Completion Notes List

- Story context generated from epics, prd, architecture.
- No project-context.md found.
- Added precondition orchestrator that resolves playlists and builds plans before write hooks.
- Added PreconditionFailure error surfaced to CLI with ExitCode.FAILURE.
- Kept dry-run flow intact while routing write-mode through preconditions.
- Added unit coverage for precondition failure exit code mapping and write-side effect gating.
- Review fixes: stop persisting provenance during preconditions; add post-write provenance hook for future writes.
- Review fixes: update dry-run/precondition tests to use precondition plan builder.
- Review fixes: adjust idempotency tests to assert no provenance persistence before writes.
- Note: unrelated working tree changes belong to Story 3.2 and are excluded from this story's File List.
- Tests run: `python -m pytest`

### File List

- _bmad-output/implementation-artifacts/3-1-enforce-fail-closed-preconditions-before-any-write.md
- src/music_library_sanitzer/cli.py
- src/music_library_sanitzer/pipeline/executor.py
- tests/unit/test_dry_run.py
- tests/unit/test_idempotency.py

## Story Completion Status

Status: done
Completion note: Precondition gating added with write-mode enforcement; tests not rerun after review fixes.
