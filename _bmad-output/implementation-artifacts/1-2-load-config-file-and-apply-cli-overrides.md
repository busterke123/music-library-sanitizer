# Story 1.2: Load config file and apply CLI overrides

Status: ready-for-dev

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

- [ ] Define config model and defaults (AC: #1)
  - [ ] Add `src/music_library_sanitzer/config/model.py` with a typed config object and sensible defaults
  - [ ] Include (at minimum) placeholders for: Rekordbox library location, backup location, stage toggles, and `dry_run` default
  - [ ] Keep all config keys `snake_case` and stable for future compatibility
- [ ] Implement config loading + merge rules (AC: #1)
  - [ ] Add `src/music_library_sanitzer/config/load.py` that:
    - Loads TOML from a path
    - Applies CLI overrides
    - Validates and returns a final config object
  - [ ] Define precedence explicitly: CLI flag value > config file value > default
  - [ ] Define default config path (if `--config` not provided): `~/.music-library-sanitzer/config.toml`
  - [ ] Treat “file not found” as an error when `--config` is explicitly provided
- [ ] Wire CLI flags into Typer (AC: #1)
  - [ ] Add `--config` option to the CLI (path to TOML)
  - [ ] Add flags for key overrides (exact set can be minimal now; must prove precedence works)
  - [ ] Ensure non-interactive behavior: no prompts; errors must be explicit and actionable
- [ ] Fail-closed validation behavior (AC: #1)
  - [ ] Validate config before any run planning or writes
  - [ ] On validation failure, exit non-zero and do not create backups or write any library/state files
  - [ ] Provide a clear error message including the failing key and expected type/range
- [ ] Tests for config behavior (AC: #1)
  - [ ] Unit test: “CLI overrides config file”
  - [ ] Unit test: “config file overrides defaults”
  - [ ] Unit test: invalid config yields non-zero (or raises a typed exception mapped to exit code)
  - [ ] (If feasible) CLI integration smoke: invoke `--help` and ensure `--config` appears

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

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

