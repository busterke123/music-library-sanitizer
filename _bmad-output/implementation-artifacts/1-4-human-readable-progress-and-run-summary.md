# Story 1.4: Human-readable progress and run summary

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As Michel,
I want clear progress and a concise run summary,
So that I can trust the tool is working and understand the outcome quickly.

## Acceptance Criteria

1. **Given** a run is processing multiple tracks  
   **When** the tool performs analysis and planning  
   **Then** it emits human-readable progress indicating work is advancing  
   **And** at the end it prints a summary with counts: processed, updated, unchanged, skipped, failed.

## Tasks / Subtasks

- [x] Add progress reporting to `run` (AC: #1)
  - [x] After the playlist preflight, show progress while iterating the playlist’s tracks
  - [x] Prefer a progress bar with `rich` (already a dependency) for large playlists
  - [x] Keep output stable enough for tests (tests strip ANSI; avoid terminal-dependent behavior)

- [x] Define a minimal outcome/count model for summaries (AC: #1)
  - [x] Use a small fixed set for per-track status: `updated`, `unchanged`, `skipped`, `failed`
  - [x] Compute run-level counts including `processed` and per-status counts
  - [x] For now (no planner/writer yet), treat successfully processed tracks as `unchanged` and `updated=0`

- [x] Print a concise run summary block (AC: #1)
  - [x] Print after progress completes (end of run)
  - [x] Include exactly: processed, updated, unchanged, skipped, failed
  - [x] Keep formatting stable (header + key/value lines) so later `--json` can mirror the same counts

- [x] Fail-closed behavior for reporting (AC: #1)
  - [x] If playlist resolution fails, exit non-zero with an actionable message (no summary block)
  - [x] If any per-track analysis/planning step fails, record as `failed` with a reason; do not perform any write-related steps

- [x] Tests (AC: #1)
  - [x] Extend E2E test to assert the final summary block exists and counts match the fixture playlist size
  - [x] Do not assert transient progress rendering; assert only on final summary text
  - [x] Add unit tests for count computation if extracted into helper functions

## Dev Notes

- This story is about **human-readable observability** only (FR25, FR28). It does not introduce JSON output (`--json`) or new exit code taxonomy (Story 1.5).
- Maintain the precondition order from `_bmad-output/architecture.md`:
  - validate config + playlist id → (analysis/planning) → (later: backup → write) → report
- Keep the existing “Playlist Preflight” block intact (Story 1.3) and add progress + summary after it.

### Previous Story Intelligence (from 1.3)

- `run --playlist-id` resolves via `src/music_library_sanitzer/rekordbox/playlist.py` and prints a stable preflight block.
- Rekordbox parsing uses streaming XML; playlist ids are treated as opaque strings.

### Git Intelligence Summary

- E2E tests strip ANSI escape codes; ensure summary text is present in plain text even if `rich` adds formatting.
- Errors should remain actionable and include playlist id and library path where relevant.

### Project Structure Notes

- CLI output belongs in `src/music_library_sanitzer/cli.py` (CLI boundary).
- Avoid prematurely creating unused modules; keep summary/count helpers small and deterministic.

### References

- Epic + story definition: `_bmad-output/epics.md` (Epic 1 → Story 1.4)
- Product requirements: `_bmad-output/prd.md` (FR25 progress; FR28 summary counts)
- Architecture boundaries & preconditions: `_bmad-output/architecture.md` (validate → plan → backup → write → report)
- Sprint tracking: `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Dev Agent Record

### Agent Model Used

GPT-5.2 (Codex CLI)

### Debug Log References

### Completion Notes List

- Added run summary model and wired progress + summary output to `run`; added e2e summary assertions and unit coverage for counts.
- Code review fixes: ensure track counts remain accurate when track ids are missing and validate summary statuses; added unit coverage.
- Tests: `python -m uv run pytest -q`

### File List

- _bmad-output/implementation-artifacts/1-4-human-readable-progress-and-run-summary.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- src/music_library_sanitzer/cli.py
- src/music_library_sanitzer/run_summary.py
- tests/e2e/test_smoke.py
- tests/unit/test_run_summary.py


