# Story 1.2: Load config file and apply CLI overrides

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As Michel,  
I want configuration defaults loaded from a config file with CLI overrides,  
so that I can set stable defaults but still adjust per run.

## Acceptance Criteria

1. **Given** a config file exists with defaults (e.g., library path, backup path, stage toggles)  
   **When** I run the CLI with `--config` and also provide overriding flags  
   **Then** the effective configuration uses CLI values over file values  
   **And** invalid configuration is rejected with a non-zero exit code and no writes.

## Tasks / Subtasks

- [x] Define config model and defaults (AC: #1)
  - [x] Add `src/music_library_sanitzer/config/model.py` with a typed config object and sensible defaults
  - [x] Include (at minimum) placeholders for: Rekordbox library location, backup location, stage toggles, and `dry_run` default
  - [x] Keep all config keys `snake_case` and stable for future compatibility
- [x] Implement config loading + merge rules (AC: #1)
  - [x] Add `src/music_library_sanitzer/config/load.py` that:
    - Loads TOML from a path
    - Applies CLI overrides
    - Validates and returns a final config object
  - [x] Define precedence explicitly: CLI flag value > config file value > default
  - [x] Define default config path (if `--config` not provided): `~/.music-library-sanitzer/config.toml`
  - [x] Treat “file not found” as an error when `--config` is explicitly provided
- [x] Wire CLI flags into Typer (AC: #1)
  - [x] Add `--config` option to the CLI (path to TOML)
  - [x] Add flags for key overrides (exact set can be minimal now; must prove precedence works)
  - [x] Ensure non-interactive behavior: no prompts; errors must be explicit and actionable
- [x] Fail-closed validation behavior (AC: #1)
  - [x] Validate config before any run planning or writes
  - [x] On validation failure, exit non-zero and do not create backups or write any library/state files
  - [x] Provide a clear error message including the failing key and expected type/range
- [x] Tests for config behavior (AC: #1)
  - [x] Unit test: “CLI overrides config file”
  - [x] Unit test: “config file overrides defaults”
  - [x] Unit test: invalid config yields non-zero (or raises a typed exception mapped to exit code)
  - [x] (If feasible) CLI integration smoke: invoke `--help` and ensure `--config` appears

## Dev Notes

- Architecture boundary is strict: `music_library_sanitzer/config/` owns schema + merge logic; `music_library_sanitzer/cli.py` owns parsing and calling into config, but must not re-implement merge rules.
- Keep the schema future-proof:
  - Unknown keys in TOML should be rejected (prefer fail-closed) unless you explicitly choose forward-compat behavior and document it.
  - Normalize paths early (expand `~`, resolve relative paths against CWD).
- This story is about configuration mechanics only. Do not add provider/network behavior here.

### Project Structure Notes

- Target locations (authoritative): `_bmad-output/architecture.md` (“Configuration Boundary” + project tree)
  - `src/music_library_sanitzer/config/model.py`
  - `src/music_library_sanitzer/config/load.py`
  - `src/music_library_sanitzer/cli.py` (Typer options wired here; merge logic remains in `config/`)

### References

- Epic + story definition: `_bmad-output/epics.md` (Epic 1 → Story 1.2)
- Config boundary + default config location: `_bmad-output/architecture.md` (Configuration Boundary; `~/.music-library-sanitzer/config.toml`)
- Product requirement: `_bmad-output/prd.md` (FR2/FR3: config file + CLI overrides; non-interactive CLI)

## Dev Agent Record

### Agent Model Used

GPT-5.2 (Codex CLI)

### Debug Log References

### Completion Notes List

- Added config model + defaults, TOML loader, validation, and merge rules with CLI > file > defaults precedence
- Wired CLI flags and fail-closed config validation with explicit error messages
- Added unit tests for override behavior and invalid config, plus help output check for `--config`
- Tests: `uv run pytest`; Lint: `uv run ruff check .`
- Code review fixes: wrap TOML parse errors, resolve config paths relative to config file, and skip config loading during `--help`
### File List

- _bmad-output/implementation-artifacts/1-2-load-config-file-and-apply-cli-overrides.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- src/music_library_sanitzer/cli.py
- src/music_library_sanitzer/config/__init__.py
- src/music_library_sanitzer/config/load.py
- src/music_library_sanitzer/config/model.py
- tests/e2e/test_smoke.py
- tests/unit/test_config.py
- (deleted) tests/.DS_Store
