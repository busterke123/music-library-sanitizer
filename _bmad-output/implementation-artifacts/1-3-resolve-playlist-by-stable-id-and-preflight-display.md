# Story 1.3: Resolve playlist by stable ID and preflight display

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As Michel,
I want to target a playlist by stable ID and see which playlist is resolved,
So that I know I’m enriching the right set of tracks before any changes.

## Acceptance Criteria

1. **Given** I provide `--playlist-id <id>`
   **When** the tool starts a run
   **Then** it resolves the playlist to a human-readable name (if available) and a track count
   **And** it prints this preflight information before any write-related steps run.

## Tasks / Subtasks

- [x] Add `--playlist-id` to the `run` command (AC: #1)
  - [x] Require it for `run` (no prompts; explicit error if missing)
  - [x] Treat the playlist id as an opaque string (no assumptions about numeric format)

- [x] Add Rekordbox playlist resolution boundary (AC: #1)
  - [x] Create `src/music_library_sanitzer/rekordbox/playlist.py` with a small API like:
    - `resolve_playlist(library_path: Path, playlist_id: str) -> ResolvedPlaylist`
    - `ResolvedPlaylist` includes `playlist_id`, optional `name`, and `track_count` (and optionally track identifiers for future pipeline use)
  - [x] Parse the Rekordbox library export (`rekordbox.xml`) from `config.library_path` (streaming/iterative parsing preferred)
  - [x] Fail closed: on missing file / invalid XML / playlist not found, raise a typed exception and abort before any downstream work

- [x] Wire resolver into CLI and print preflight (AC: #1)
  - [x] In `src/music_library_sanitzer/cli.py:run`, after config validation but before any planning/writes, call the resolver
  - [x] Print a stable preflight block that includes:
    - playlist id
    - playlist name (if available)
    - track count

- [x] Error handling + exit code semantics (AC: #1)
  - [x] Map playlist resolution failures to a non-zero exit code (consistent with config fail-closed behavior)
  - [x] Error messages must be actionable (e.g., show the library path used and the playlist id requested)

- [x] Tests (AC: #1)
  - [x] Add a minimal Rekordbox XML fixture under `tests/fixtures/` that includes at least two playlists and a few tracks
  - [x] Unit tests for `resolve_playlist`:
    - resolves known playlist id → expected name + count
    - unknown playlist id → error
    - invalid XML → error
  - [x] E2E/CLI smoke test:
    - `python -m music_library_sanitzer --library-path <fixture_path> run --playlist-id <fixture_id>` prints the preflight block and exits 0

## Dev Notes

- This story is **preflight + targeting only**. Do not implement write planning, backups, hot cue generation, or any Rekordbox writes.
- Keep the **Rekordbox IO boundary strict**: only `music_library_sanitzer/rekordbox/` reads the library export.
- Keep the CLI **non-interactive** by default (FR1): no prompts; all required info comes from flags/config.
- Prefer streaming XML parsing (e.g., `xml.etree.ElementTree.iterparse`) because real libraries can be large.

### Previous Story Intelligence (from 1.2)

- Config/schema/merge logic lives under `music_library_sanitzer/config/`; do not re-implement merge rules in the CLI.
- Fail-closed behavior is the default pattern: validate early, exit non-zero, and avoid side effects when preconditions fail.

### Git Intelligence Summary

- Recent commits are CI/test fixes; no established patterns yet for Rekordbox parsing or playlist resolution.

### Project Structure Notes

- Target locations (authoritative): `_bmad-output/architecture.md` (Project Structure & Boundaries)
  - `src/music_library_sanitzer/cli.py`
  - `src/music_library_sanitzer/rekordbox/playlist.py`
  - (Optional helper) `src/music_library_sanitzer/errors.py` for a typed exception mapped to a stable exit code

### References

- Epic + story definition: `_bmad-output/epics.md` (Epic 1 → Story 1.3)
- Product requirements: `_bmad-output/prd.md` (FR6–FR8; fail-closed NFRs)
- Architecture boundaries & preconditions: `_bmad-output/architecture.md` (Rekordbox boundary; validate → plan → backup → write → report)
- Sprint tracking: `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Dev Agent Record

### Agent Model Used

GPT-5.2 (Codex CLI)

### Debug Log References

### Completion Notes List

- Implemented required `--playlist-id` option on `run` and added e2e coverage for missing flag; hardened smoke tests for cross-platform output decoding; normalized path assertions for Windows.
- Implemented Rekordbox playlist resolver boundary with streaming XML parsing, typed error, and unit tests.
- Wired resolver into CLI with preflight output; added Rekordbox XML fixture and e2e preflight smoke test.
- Added e2e coverage for playlist resolution error path and non-zero exit.
- Code review fixes: ignore folder nodes in playlist resolution, include playlist id in invalid XML errors, and correct CLI command ordering in story.
- Tests: `python -m uv run pytest -q`

### Change Log

- 2025-12-23: Implement playlist resolution preflight, error handling, and tests for story 1.3.

### File List

- _bmad-output/implementation-artifacts/1-3-resolve-playlist-by-stable-id-and-preflight-display.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- src/music_library_sanitzer/cli.py
- src/music_library_sanitzer/errors.py
- src/music_library_sanitzer/rekordbox/__init__.py
- src/music_library_sanitzer/rekordbox/playlist.py
- tests/fixtures/rekordbox.xml
- tests/e2e/test_smoke.py
- tests/unit/test_rekordbox_playlist.py
- tests/unit/test_config.py
