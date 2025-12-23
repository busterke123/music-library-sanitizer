# Story 2.1: Build a deterministic write plan from inputs

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As Michel,
I want the tool to compute a deterministic write plan from my playlist and configuration before any write,
so that re-runs are consistent and I can trust exactly what will change.

## Acceptance Criteria

1. Given the same playlist tracks and the same effective configuration, when I run the tool twice, then the computed write plan is identical (same per-track planned actions and cue content). [Source: _bmad-output/epics.md#Story 2.1: Build a deterministic write plan from inputs]
2. Given any write run, when the tool begins execution, then it creates the write plan before any backup or write steps start. [Source: _bmad-output/epics.md#Story 2.1: Build a deterministic write plan from inputs]

## Tasks / Subtasks

- [x] Define write plan data model and serialization format (AC: 1, 2)
  - [x] Specify required fields for per-track planned actions and cue content (AC: 1)
  - [x] Ensure stable ordering and deterministic serialization (AC: 1)
- [x] Implement deterministic planner entrypoint (AC: 1, 2)
  - [x] Build plan from resolved playlist tracks and effective config inputs (AC: 1, 2)
  - [x] Guarantee no write-side effects before plan completion (AC: 2)
- [x] Add tests for determinism and precondition ordering (AC: 1, 2)
  - [x] Same inputs produce identical plan artifacts (AC: 1)
  - [x] Planner runs before backup/write steps are invoked (AC: 2)

## Dev Notes

- Write plan must be deterministic: same playlist + same effective config => identical per-track planned actions and cue content. Treat planning as pure function of inputs. [Source: _bmad-output/epics.md#Story 2.1: Build a deterministic write plan from inputs]
- Plan must be created before any backup or write steps (fail-closed precondition order: validate config + playlist -> build plan -> backup -> write -> report). [Source: _bmad-output/architecture.md#Safety Preconditions (Fail Closed)]
- Keep pipeline planning deterministic and isolated from IO side effects. [Source: _bmad-output/architecture.md#Project Structure & Boundaries]
- Exit codes: never report success when a fail-closed precondition fails. [Source: _bmad-output/architecture.md#Error Handling & Exit Codes]
- Implement in planned modules: `src/music_library_sanitzer/pipeline/` for plan models + planner logic, `src/music_library_sanitzer/state/` for persisting plan artifact (if added in this story). [Source: _bmad-output/architecture.md#Complete Project Directory Structure]

### Project Structure Notes

- Use `snake_case` for modules, files, functions, variables, and config keys. [Source: _bmad-output/architecture.md#Naming Patterns]
- If introducing new files, align with architecture layout under `src/music_library_sanitzer/pipeline/` and `src/music_library_sanitzer/state/`. [Source: _bmad-output/architecture.md#Complete Project Directory Structure]
- No conflicts detected with current layout (`src/music_library_sanitzer/` already exists). [Source: _bmad-output/architecture.md#Project Structure & Boundaries]

### References

- _bmad-output/epics.md#Story 2.1: Build a deterministic write plan from inputs
- _bmad-output/architecture.md#Safety Preconditions (Fail Closed)
- _bmad-output/architecture.md#Project Structure & Boundaries
- _bmad-output/architecture.md#Complete Project Directory Structure
- _bmad-output/architecture.md#Naming Patterns
- _bmad-output/architecture.md#Error Handling & Exit Codes

## Developer Context

### Technical Requirements

- Deterministic write plan: same playlist + same effective config => identical per-track planned actions and cue content. [Source: _bmad-output/epics.md#Story 2.1: Build a deterministic write plan from inputs]
- Plan must exist before any backup or write steps run (fail-closed order). [Source: _bmad-output/architecture.md#Safety Preconditions (Fail Closed)]
- Persisted plan artifact should use `snake_case` fields and stable ordering. [Source: _bmad-output/architecture.md#Naming Patterns]

### Architecture Compliance

- Keep planning logic pure; isolate IO (backup/write) behind boundaries. [Source: _bmad-output/architecture.md#Project Structure & Boundaries]
- Deterministic planner belongs in `pipeline/` and should not touch Rekordbox writes directly. [Source: _bmad-output/architecture.md#Project Structure & Boundaries]

### Library / Framework Requirements

- Python CLI stack: Typer + Rich, pytest for tests. [Source: _bmad-output/architecture.md#Selected Starter: uv + Typer]
- Use existing project patterns for exit codes and error handling. [Source: _bmad-output/architecture.md#Error Handling & Exit Codes]

### File Structure Requirements

- Add plan models + planner under `src/music_library_sanitzer/pipeline/`. [Source: _bmad-output/architecture.md#Complete Project Directory Structure]
- Add persistence helpers under `src/music_library_sanitzer/state/` if plan artifact is written. [Source: _bmad-output/architecture.md#Complete Project Directory Structure]

### Testing Requirements

- Add determinism tests: identical inputs -> identical plan artifact. [Source: _bmad-output/epics.md#Story 2.1: Build a deterministic write plan from inputs]
- Add precondition ordering tests: planner runs before backup/write calls. [Source: _bmad-output/architecture.md#Safety Preconditions (Fail Closed)]

## Project Context Reference

- No `project-context.md` found in repo; follow architecture decisions and epics as source of truth.

## Story Completion Status

- Status: done
- Completion note: Ultimate context engine analysis completed - comprehensive developer guide created.

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

None.
### Completion Notes List

- Write plan must be deterministic and produced before any backup/write steps.
- Planner should be pure and isolated from IO.
- Tests required for determinism and precondition ordering.
- Added deterministic write plan models + planner entrypoint and CLI sequencing hook.
- Added unit coverage for determinism, planned actions/cues fields, and plan-before-processing ordering.
- Tests run: `python3 -m pytest`
- Added deterministic inputs hash and persisted write plan artifact under state runs.
- Fail-closed behavior now exits with failure code on write plan persistence errors.
- Persistence falls back to a local state directory if the home state path is not writable.
### File List

- _bmad-output/implementation-artifacts/2-1-build-a-deterministic-write-plan-from-inputs.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- src/music_library_sanitzer/cli.py
- src/music_library_sanitzer/pipeline/__init__.py
- src/music_library_sanitzer/pipeline/models.py
- src/music_library_sanitzer/pipeline/planner.py
- src/music_library_sanitzer/state/__init__.py
- src/music_library_sanitzer/state/paths.py
- src/music_library_sanitzer/state/runs.py
- tests/unit/test_write_plan.py
