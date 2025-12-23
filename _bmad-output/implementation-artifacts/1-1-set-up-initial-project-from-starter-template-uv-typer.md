# Story 1.1: Set up initial project from starter template (uv + Typer)

Status: done

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

- [x] Scaffold project with `uv` (AC: #1)
  - [x] Run `uv init music-library-sanitzer` (or align existing repo with equivalent `pyproject.toml` + `uv.lock`)
  - [x] Ensure `.python-version` (or equivalent) is present/consistent with chosen runtime
  - [x] Ensure packaging supports `src/` layout and installs `music_library_sanitzer` module
- [x] Add baseline dependencies via `uv` (AC: #1)
  - [x] `uv add typer rich`
  - [x] `uv add --dev pytest ruff mypy`
  - [x] Decide whether `requirements.txt` remains (if kept, document it as export-only; otherwise remove to avoid drift)
- [x] Create the architecture-aligned directory structure (AC: #1)
  - [x] Create `src/music_library_sanitzer/` package with `__init__.py` and `__main__.py`
  - [x] Add `src/music_library_sanitzer/cli.py` with Typer app and placeholder `run` command
  - [x] Wire console entrypoint so `music-library-sanitzer --help` works (via `pyproject.toml` scripts)
  - [x] Ensure `python -m music_library_sanitzer --help` also works
- [x] Establish minimal test + lint baseline (AC: #1)
  - [x] Keep/adjust existing `pytest.ini` and `tests/` layout to match the new package name
  - [x] Add at least one smoke test that invokes CLI help and asserts `run` appears
  - [x] Ensure `ruff` and `pytest` run locally (CI wiring can be handled in later stories)

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

GPT-5.2 (Codex CLI)

### Debug Log References

### Completion Notes List

- Initialized uv-based Python package with `src/` layout + `uv.lock`
- Added Typer/Rich runtime deps and pytest/ruff/mypy dev deps (plus `python-dotenv` for existing test harness)
- Implemented Typer CLI scaffold with `run` placeholder; verified `music-library-sanitzer --help` and `python -m music_library_sanitzer --help`
- Updated e2e smoke test to assert `run` appears; ran `pytest` + `ruff check .`
- Code review fixes: aligned Python version to 3.12, added console entrypoint test, refreshed uv lock, updated test docs, and removed tracked `.DS_Store`

### File List

- .gitignore
- .python-version
- _bmad-output/implementation-artifacts/1-1-set-up-initial-project-from-starter-template-uv-typer.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- pyproject.toml
- src/music_library_sanitzer/__init__.py
- src/music_library_sanitzer/__main__.py
- src/music_library_sanitzer/cli.py
- tests/README.md
- tests/e2e/test_smoke.py
- uv.lock
- (deleted) requirements.txt
- (deleted) .DS_Store
