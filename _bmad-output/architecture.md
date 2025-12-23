---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - _bmad-output/prd.md
  - _bmad-output/analysis/research/technical-music-library-data-enrichment-research-2025-12-22.md
workflowType: 'architecture'
lastStep: 8
status: 'complete'
completedAt: '2025-12-22T21:43:00+01:00'
project_name: 'music-library-sanitzer'
user_name: 'Arne.driesen'
date: '2025-12-22T21:07:17+01:00'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
The product is a non-interactive, scriptable CLI that enriches a Rekordbox library by generating hot cues for tracks within a single target playlist (selected via stable playlist ID). The system must support dry-run planning, JSON summaries, per-track outcomes, and clear exit codes. It must be designed as an extensible enrichment pipeline with provenance so future stages (energy/vocals) and optional provider integrations can be added without destabilizing the core workflow.

**Non-Functional Requirements:**
The system must prioritize library integrity above all else: it must fail closed and abort before writing on unexpected conditions. Network calls are permitted but must be intentional and minimize exposure of local data. There is no strict runtime SLA, but runs must provide progress so the user can tell work is advancing.

**Scale & Complexity:**
- Primary domain: CLI tool operating on local library data with optional external providers
- Complexity level: medium (single-user CLI, but high-risk data writes + backup/restore + provenance + idempotency)
- Estimated architectural components: 6–8 (CLI interface, config, playlist resolution, analysis pipeline, write planner, writer, backup/restore manager, reporting)

### Technical Constraints & Dependencies

- Must read and write the Rekordbox library format safely.
- Must create a backup before any write and retain 50 most recent backups at `~/.music-library-sanitzer/backups` by default.
- Must support provenance to identify tool-created cues and safely overwrite only those.
- Optional external providers require adapters with caching/rate limiting and safe failure behavior.

### Cross-Cutting Concerns Identified

- Data safety & fail-closed execution
- Backup/restore with retention and verifiable restore
- Determinism & idempotency across re-runs
- Provenance for tool-created artifacts
- Clear observability: per-track outcomes, summaries, exit codes
- Optional provider hygiene without risking writes

## Starter Template Evaluation

### Primary Technology Domain

Python CLI tool with local data processing and optional external provider integrations.

### Starter Options Considered

1) uv project initialization (`uv init`) + modern pyproject-based workflow
- Pros: fast, minimal, modern project scaffolding; easy dependency management (`uv add`)
- Cons: requires installing uv on dev machines

2) cookiecutter-hypermodern-python
- Pros: very comprehensive
- Cons: published usage pins an older template checkout; too heavy for this MVP and less “current baseline”

### Selected Starter: uv + Typer

**Rationale for Selection:**
Lean, maintainable foundation for a Python CLI with strong developer ergonomics and good testability, without over-scaffolding.

**Initialization Command:**

```bash
uv init music-library-sanitzer
cd music-library-sanitzer
uv add typer rich
uv add --dev pytest ruff mypy
```

**Architectural Decisions Provided by Starter:**

**Language & Runtime:**
- Python project scaffold with `pyproject.toml` and `main.py`

**Build Tooling / Dependency Management:**
- Dependency management via `uv add` updating `pyproject.toml`

**Testing Framework:**
- `pytest` as the baseline test runner

**Code Organization:**
- Simple application layout to evolve into pipeline modules (backup/restore, library IO, analysis, write-plan, writer)

**Development Experience:**
- `ruff` for linting/formatting; type checking via `mypy` (optional early, useful as pipeline grows)

## Core Architectural Decisions

### Data Architecture

**Decision:** Persist local state as flat files (JSON) under `~/.music-library-sanitzer/` (no DB).  
**Rationale:** Keeps the platform MVP simple while still supporting provenance, repeatability, auditing, and future stages/providers.

**Local State Layout:**
- Config: `~/.music-library-sanitzer/config.toml`
- Runs: `~/.music-library-sanitzer/state/runs/` (one folder per run id; stores write plan + outcomes)
- Provenance: `~/.music-library-sanitzer/state/provenance/` (indexes to identify tool-created cues for safe overwrite rules)
- Provider cache: `~/.music-library-sanitzer/state/cache/` (enabled automatically when providers are enabled)
- Backups: `~/.music-library-sanitzer/backups/` (pre-write backups; keep 50 most recent)

**Persisted Data:**
- Run history (run id, timestamp, playlist id, tool version, config hash)
- Write plan + outcomes (per track: planned cues, applied cues, status, errors)
- Provenance index (for “overwrite only tool-created cues” policy)
- Provider cache entries (optional providers; cached when enabled)

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:** naming, file layout, config keys, state JSON schemas, logging, error/exit-code conventions, and safety preconditions for “write” operations.

### Naming Patterns

**Python Naming Conventions:**
- Use `snake_case` for modules, files, functions, variables, and config keys.
- Use `PascalCase` for classes and exception types.

**State/JSON Naming Conventions:**
- Persisted JSON (run plans, outcomes, provenance, caches) uses `snake_case` field names.

### Structure Patterns

**Project Organization (Python CLI):**
- Separate “core pipeline” from “IO side effects”:
  - analysis/generation code is pure where possible (deterministic inputs → deterministic outputs)
  - library writes, backups, and provider calls are isolated behind interfaces/adapters

**State Directory Structure (Authoritative):**
- Config: `~/.music-library-sanitzer/config.toml`
- Runs: `~/.music-library-sanitzer/state/runs/<run_id>/`
- Provenance: `~/.music-library-sanitzer/state/provenance/`
- Provider cache: `~/.music-library-sanitzer/state/cache/`
- Backups: `~/.music-library-sanitzer/backups/` (keep 50)

### Format Patterns

**Write Plan Format (Deterministic):**
- A run produces a deterministic “write plan” artifact (JSON) before any writes.
- `--dry-run` outputs the plan and per-track intended changes without writing.

**Outcome Reporting Format:**
- Track-level outcomes use a small fixed set of statuses: `updated`, `unchanged`, `skipped`, `failed`.
- Every `skipped`/`failed` record includes a machine-readable reason/code and a human-readable message.

### Logging & Reporting Patterns

- Default logs are human-friendly (single-user CLI ergonomics).
- Machine-readable output is available via JSON summary output (for scripting, archiving, and later tooling).

### Error Handling & Exit Codes

- Use a custom exception hierarchy for predictable fail-closed behavior and consistent error messages.
- Map failures to stable error codes and distinct exit codes:
  - `0`: success
  - non-zero: partial success / failure (per PRD); never return success when any “fail closed” precondition fails

### Safety Preconditions (Fail Closed)

- All “write” actions must follow the same precondition order:
  1) validate config and target playlist id
  2) build deterministic write plan
  3) create backup (must succeed)
  4) apply writes (only within overwrite policy)
  5) report outcomes
- If any precondition fails, abort before writing.

## Project Structure & Boundaries

### Complete Project Directory Structure

```text
music-library-sanitzer/
├── README.md
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
├── src/
│   └── music_library_sanitzer/
│       ├── __init__.py
│       ├── __main__.py              # `python -m music_library_sanitzer`
│       ├── cli.py                   # Typer app + commands
│       ├── config/
│       │   ├── __init__.py
│       │   ├── model.py             # config schema (typed)
│       │   └── load.py              # load/merge TOML + flags
│       ├── state/
│       │   ├── __init__.py
│       │   ├── paths.py             # ~/.music-library-sanitzer layout
│       │   ├── runs.py              # run_id, plan/outcome persistence
│       │   ├── provenance.py         # tool-created cue index
│       │   └── cache.py             # provider cache (opt)
│       ├── rekordbox/
│       │   ├── __init__.py
│       │   ├── library_reader.py    # read library + cues
│       │   ├── library_writer.py    # write cues (policy enforced)
│       │   ├── playlist.py          # resolve playlist_id -> track list
│       │   └── backup.py            # backup/restore + retention
│       ├── pipeline/
│       │   ├── __init__.py
│       │   ├── models.py            # TrackRef, Cue, WritePlan, Outcome
│       │   ├── planner.py           # build deterministic write plan
│       │   ├── executor.py          # run preconditions + apply plan
│       │   └── stages/
│       │       ├── __init__.py
│       │       └── hot_cues.py      # stage: generate hot cues
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── base.py              # adapter interface
│       │   └── rate_limit.py        # shared outbound controls (future)
│       └── errors.py                # exception hierarchy + error codes
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

### Architectural Boundaries

**CLI Boundary:**
- `music_library_sanitzer/cli.py` owns command parsing, configuration overrides, and user-facing outputs (human logs + JSON summaries).

**Configuration Boundary:**
- `music_library_sanitzer/config/` owns config schema and merge logic (TOML defaults + CLI overrides), emitting a validated config object for the rest of the system.

**State Boundary (Flat Files):**
- `music_library_sanitzer/state/` is the only layer that reads/writes `~/.music-library-sanitzer/state/**`.
- Pipelines and providers consume state via these modules, not by touching filesystem paths directly.

**Rekordbox Boundary (High-Risk IO):**
- `music_library_sanitzer/rekordbox/` is the only layer that reads/writes the Rekordbox library.
- Backup/restore and retention live here; other modules depend on it via explicit functions/services.

**Pipeline Boundary (Deterministic Core):**
- `music_library_sanitzer/pipeline/` owns deterministic planning and orchestrated execution.
- The write plan is produced before any write, and the executor enforces the fail-closed precondition sequence.

**Providers Boundary (Optional, Controlled Network):**
- `music_library_sanitzer/providers/` owns outbound provider adapters and shared controls (e.g., rate limiting/caching behavior), and integrates only through pipeline stages.

### Requirements-to-Structure Mapping

- CLI Execution & Control → `music_library_sanitzer/cli.py`, `music_library_sanitzer/config/`
- Playlist Targeting & Scope → `music_library_sanitzer/rekordbox/playlist.py`, `music_library_sanitzer/pipeline/models.py`
- Backup/Restore & Safety → `music_library_sanitzer/rekordbox/backup.py`, `music_library_sanitzer/pipeline/executor.py`, `music_library_sanitzer/errors.py`
- Hot Cue Generation → `music_library_sanitzer/pipeline/stages/hot_cues.py`, `music_library_sanitzer/pipeline/planner.py`
- Reporting/Exit codes → `music_library_sanitzer/cli.py`, `music_library_sanitzer/state/runs.py`
- Determinism/Idempotency → `music_library_sanitzer/pipeline/planner.py`, `music_library_sanitzer/state/provenance.py`, `music_library_sanitzer/rekordbox/library_writer.py`
- Extensibility (stages) → `music_library_sanitzer/pipeline/stages/`, `music_library_sanitzer/providers/`
- Provider integration → `music_library_sanitzer/providers/`, `music_library_sanitzer/state/cache.py`

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
The chosen stack and decisions are compatible: Python CLI + `uv` project management + Typer for CLI, with a fail-closed execution model and pre-write backups. Flat-file state supports provenance and repeatable runs without introducing database complexity.

**Pattern Consistency:**
Naming (`snake_case`), deterministic write plans, and a strict precondition order for writes (validate → plan → backup → write → report) align directly with safety and repeatability requirements.

**Structure Alignment:**
The proposed `src/` layout and module boundaries isolate high-risk IO (Rekordbox reads/writes, backup/restore) from deterministic planning/pipeline code, reducing the chance of accidental side effects and agent drift.

### Requirements Coverage Validation ✅

**Functional Requirements Coverage:**
All FR categories have explicit architectural homes:
- CLI/configuration and output formats
- Playlist targeting by stable playlist ID
- Backup/restore with retention and verification/reporting
- Hot cue generation via pipeline stages
- Determinism/idempotency via write planning + provenance
- Optional providers via adapters + cache layer

**Non-Functional Requirements Coverage:**
- Fail-closed behavior enforced by executor preconditions and abort-before-write rule.
- Network usage isolated to provider adapters; cache layer reduces repeated calls and supports bounded behavior.
- No strict runtime SLA; progress reporting supported through CLI + run outcome recording.

### Implementation Readiness Validation ✅

**Decision Completeness:**
Core decisions are explicit enough to implement consistently (starter toolchain, state layout, backup policy, provenance-driven overwrite rules).

**Structure Completeness:**
Project tree and boundaries are concrete and map to requirements; `src/` layout is recommended as the default packaging structure.

**Pattern Completeness:**
Conflict points most likely to cause drift (naming, schemas, error handling, write safety ordering) are specified.

### Gap Analysis Results

- **Minor (Nice-to-have):** Define explicit numeric exit code mapping (e.g., 0/1/2) and a canonical JSON schema for write plans/outcomes; can be refined early in implementation.

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] Project context analyzed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped

**✅ Architectural Decisions**
- [x] Stack and foundations specified
- [x] Data/state strategy decided
- [x] Provider strategy bounded

**✅ Implementation Patterns**
- [x] Naming conventions established
- [x] Safety preconditions defined
- [x] Error/exit-code approach specified

**✅ Project Structure**
- [x] Complete directory structure defined
- [x] Boundaries established
- [x] Requirements mapped to structure

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

## Architecture Completion Summary

### Workflow Completion

**Architecture Decision Workflow:** COMPLETED ✅  
**Total Steps Completed:** 8  
**Date Completed:** 2025-12-22T21:43:00+01:00  
**Document Location:** `_bmad-output/architecture.md`

### Final Architecture Deliverables

- Stack + starter: Python + `uv` + Typer, with test/lint/type tooling baseline
- Core decisions: flat-file state + TOML config + backup/restore + provenance-driven safe overwrites
- Patterns: snake_case conventions, deterministic write plan, fail-closed preconditions
- Structure: concrete module layout with clear boundaries and FR-to-structure mapping
- Validation: coherence and requirements coverage checks completed

### Implementation Handoff

**First Implementation Priority:**
Initialize the project using the documented `uv init` command and scaffold the directory structure under `src/music_library_sanitzer/` to match the architecture.

**Create/Update project context?**
Would you like to create a `project-context.md` file to capture the critical rules (naming, safety preconditions, backup policy, state layout, exit codes) for future AI agents? (Y/N)
