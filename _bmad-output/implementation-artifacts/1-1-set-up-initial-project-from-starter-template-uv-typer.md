# Story 1.1: Set up initial project from starter template (uv + Typer)

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As Michel,  
I want the project scaffolded using the chosen starter approach,  
so that development starts from a clean, maintainable baseline.

## Acceptance Criteria

1. **Given** I have Python tooling available  
   **When** I initialize the project using `uv` and add Typer and Rich  
   **Then** the project has a runnable CLI entrypoint  
   **And** `music-library-sanitzer --help` works and shows a `run` command placeholder.

## Tasks / Subtasks

- [ ] Scaffold project with `uv` (AC: #1)
  - [ ] Run `uv init music-library-sanitzer` (or align existing repo with equivalent `pyproject.toml` + `uv.lock`)
  - [ ] Ensure `.python-version` (or equivalent) is present/consistent with chosen runtime
  - [ ] Ensure packaging supports `src/` layout and installs `music_library_sanitzer` module
- [ ] Add baseline dependencies via `uv` (AC: #1)
  - [ ] `uv add typer rich`
  - [ ] `uv add --dev pytest ruff mypy`
  - [ ] Decide whether `requirements.txt` remains (if kept, document it as export-only; otherwise remove to avoid drift)
- [ ] Create the architecture-aligned directory structure (AC: #1)
  - [ ] Create `src/music_library_sanitzer/` package with `__init__.py` and `__main__.py`
  - [ ] Add `src/music_library_sanitzer/cli.py` with Typer app and placeholder `run` command
  - [ ] Wire console entrypoint so `music-library-sanitzer --help` works (via `pyproject.toml` scripts)
  - [ ] Ensure `python -m music_library_sanitzer --help` also works
- [ ] Establish minimal test + lint baseline (AC: #1)
  - [ ] Keep/adjust existing `pytest.ini` and `tests/` layout to match the new package name
  - [ ] Add at least one smoke test that invokes CLI help and asserts `run` appears
  - [ ] Ensure `ruff` and `pytest` run locally (CI wiring can be handled in later stories)

## Dev Notes

- This story is deliberately “foundation-only”: do not implement business logic beyond a placeholder `run` command.
- Prefer a modern `pyproject.toml`-based workflow; avoid introducing parallel dependency systems that can drift (e.g., `requirements.txt` + `pyproject.toml`) unless there’s a clear documented reason.
- Keep the CLI non-interactive by default (no prompts), consistent with FR1 and the overall “scriptable CLI” requirement.

### Project Structure Notes

- Target structure (authoritative):
  - `src/music_library_sanitzer/__main__.py` for `python -m music_library_sanitzer`
  - `src/music_library_sanitzer/cli.py` for Typer app + commands
  - Additional modules (`config/`, `state/`, `pipeline/`, `rekordbox/`, etc.) come later; stub folders are optional here unless they help future stories.

### References

- Epic + story definition: `_bmad-output/epics.md` (Epic 1 → Story 1.1)
- Starter/tooling decision and target layout: `_bmad-output/architecture.md` (Selected Starter: uv + Typer; “Complete Project Directory Structure”)
- Product intent: `_bmad-output/prd.md` (CLI-first, scriptable workflow)

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

