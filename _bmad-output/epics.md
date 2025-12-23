---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - _bmad-output/prd.md
  - _bmad-output/architecture.md
---

# music-library-sanitzer - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for music-library-sanitzer, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Michel can run enrichment non-interactively via CLI flags (no prompts by default).
FR2: Michel can provide a configuration file for defaults.
FR3: Michel can override configuration values via CLI flags.
FR4: Michel can run the tool in `--dry-run` mode to preview intended changes without writing.
FR5: Michel can request a machine-readable JSON summary of a run.
FR6: Michel can target enrichment to a single Rekordbox playlist via a stable playlist ID.
FR7: The system can resolve a playlist ID to the set of tracks included in that playlist at run time.
FR8: The system can report the resolved playlist (ID and human-readable name, if available) before applying changes.
FR9: The system can read the necessary Rekordbox library data to determine current hot cues for targeted tracks.
FR10: The system can write hot cues back into the Rekordbox library for targeted tracks.
FR11: The system can apply a write policy that prevents overwriting user-created cues.
FR12: The system can overwrite hot cues only when they were previously created by this tool (provenanced).
FR13: The system can detect whether an existing hot cue was created by this tool (provenance check).
FR14: The system can create a backup of the Rekordbox library before any write is performed.
FR15: If backup creation fails, the system aborts the run before making any changes to the Rekordbox library.
FR16: The system can store backups by default in `~/.music-library-sanitzer/backups` (with configurable override).
FR17: The system can retain the **50 most recent** backups and remove older backups beyond this limit.
FR18: Michel can list available backups (at minimum: timestamp and identifier).
FR19: Michel can restore the Rekordbox library from a selected backup.
FR20: After a restore, the system can confirm restore completion (verification/reporting).
FR21: The system can generate hot cue candidates for each eligible track in the playlist.
FR22: The system can decide which cue slots to fill based on the configured policy and existing cues.
FR23: The system can write the chosen cues in a way that they are visible and usable inside Rekordbox.
FR24: The system can report which tracks would be changed (and how) in `--dry-run`.
FR25: The system can output human-readable run progress and completion status to the console.
FR26: The system can produce a per-track outcome (e.g., updated, unchanged, skipped, failed).
FR27: The system can list skipped/flagged tracks and a reason for each (e.g., analysis failed, unsupported file).
FR28: The system can output a summary including counts: processed, updated, unchanged, skipped, failed.
FR29: The system can return distinct exit codes for: success, partial success (some skips/failures), and failure.
FR30: Re-running enrichment with the same inputs and configuration produces consistent results (no random drift).
FR31: The system can avoid duplicating or thrashing tool-created cues across re-runs (idempotent behavior).
FR32: The system can update previously tool-created cues when regeneration is needed (within the overwrite policy).
FR33: The system can support multiple enrichment stages as a pipeline (e.g., cues now; energy/vocals later).
FR34: The system can enable/disable pipeline stages via configuration.
FR35: The system can record provenance per generated artifact to support future safe updates and debugging.
FR36: The system can add new enrichment stages in the future without changing existing CLI workflows for running a playlist.
FR37: The system can support optional external providers via adapters (enabled/disabled by config).
FR38: When providers are used, the system can cache results to reduce repeat calls (capability requirement, not implementation).

### NonFunctional Requirements

NFR1: Provide progress feedback during runs so the user can tell the process is advancing (no strict runtime SLA for MVP).
NFR2: Fail closed: on any unexpected condition, abort before writing to the Rekordbox library.
NFR3: Never partially write changes if preconditions are not met (e.g., backup creation fails, cannot validate write plan, cannot access library safely).
NFR4: Preserve library integrity as the highest priority with clear error reporting on abort.
NFR5: Minimize exposure of local library data; any network usage must be intentional, bounded, and observable.
NFR6: Avoid sending unnecessary personal/local file information to external services (least data necessary).
NFR7: When network calls are enabled, behave respectfully toward external services (rate limiting/caching) and degrade gracefully (abort before writes if provider dependency is required for a safe plan; otherwise skip provider-dependent enrichment and report clearly).

### Additional Requirements

- Starter template: initialize as a Python project using `uv` and build the CLI with Typer (with Rich for output); use `pytest` for tests and `ruff`/`mypy` for lint/type-checking as the project grows.
- Persist local state as flat files under `~/.music-library-sanitzer/` (no DB), including run history, write plan/outcomes, provenance index, and provider cache when enabled.
- Safety precondition order for any write run: validate config + playlist id → build deterministic write plan → create backup (must succeed) → apply writes (policy enforced) → report outcomes; abort before writing if any precondition fails.
- Define clear module boundaries (CLI/config/state/rekordbox IO/pipeline/providers) and keep Rekordbox read/write isolated behind a dedicated layer.
- Project structure expectation (package layout under `src/music_library_sanitzer/` with modules for config, state, rekordbox IO, pipeline stages, providers, and errors).
- Exit code semantics must align with PRD (success vs partial success vs failure); never report success when a fail-closed precondition fails.

### FR Coverage Map

### FR Coverage Map

FR1: Epic 1 - Non-interactive CLI execution
FR2: Epic 1 - Config file support
FR3: Epic 1 - CLI overrides config
FR4: Epic 2 - Dry-run preview mode
FR5: Epic 5 - JSON summary output
FR6: Epic 1 - Target playlist by stable ID
FR7: Epic 1 - Resolve playlist tracks at runtime
FR8: Epic 1 - Report resolved playlist before applying changes
FR9: Epic 4 - Read Rekordbox data for current cues
FR10: Epic 4 - Write hot cues to Rekordbox
FR11: Epic 4 - Prevent overwriting user-created cues
FR12: Epic 4 - Overwrite only tool-created cues
FR13: Epic 4 - Detect tool-created cues (provenance check)
FR14: Epic 3 - Create backup before any write
FR15: Epic 3 - Abort run if backup creation fails
FR16: Epic 3 - Default backup location
FR17: Epic 3 - Backup retention (keep 50)
FR18: Epic 3 - List backups
FR19: Epic 3 - Restore from backup
FR20: Epic 3 - Verify/report restore completion
FR21: Epic 4 - Generate hot cue candidates per track
FR22: Epic 4 - Decide cue slots to fill based on policy/existing cues
FR23: Epic 4 - Write cues so they are usable in Rekordbox
FR24: Epic 2 - Report planned per-track changes in dry-run
FR25: Epic 1 - Human-readable progress and completion status
FR26: Epic 4 & Epic 5 - Per-track outcome
FR27: Epic 4 & Epic 5 - Skipped/flagged tracks with reasons
FR28: Epic 1 & Epic 5 - Summary counts
FR29: Epic 1 & Epic 5 - Exit codes for success/partial/failure
FR30: Epic 2 - Determinism across re-runs
FR31: Epic 2 - Idempotency (no thrashing)
FR32: Epic 2 - Update tool-created cues when regeneration needed
FR33: Epic 6 - Multi-stage enrichment pipeline support
FR34: Epic 6 - Enable/disable pipeline stages via config
FR35: Epic 4 - Record provenance per generated artifact
FR36: Epic 6 - Add new stages without changing CLI workflow
FR37: Epic 6 - Optional external providers via adapters
FR38: Epic 6 - Provider caching capability

## Epic List

### Epic 1: Run playlist enrichment safely (core CLI workflow)
Michel can target a Rekordbox playlist and run enrichment confidently with a scriptable CLI, clear progress, and consistent run summaries.
**FRs covered:** FR1, FR2, FR3, FR6, FR7, FR8, FR25, FR28, FR29

### Epic 2: Plan changes before writing (deterministic write planning + dry run)
Michel can preview exactly what would change, and trust that re-running with the same inputs yields consistent and idempotent results.
**FRs covered:** FR4, FR24, FR30, FR31, FR32

### Epic 3: Protect Rekordbox library integrity (backup/restore + fail-closed execution)
Michel can safely write changes with a verified backup/restore safety net and strict “fail closed” behavior before any write occurs.
**FRs covered:** FR14, FR15, FR16, FR17, FR18, FR19, FR20

### Epic 4: Generate and write hot cues with provenance + overwrite policy
Michel gets usable hot cues in Rekordbox without overwriting manual cues, and the tool can safely recognize and update only its own cues later.
**FRs covered:** FR9, FR10, FR11, FR12, FR13, FR21, FR22, FR23, FR26, FR27, FR35

### Epic 5: Reporting & automation outputs (JSON summary + track outcomes)
Michel can automate runs and archive outcomes with machine-readable summaries and per-track status details.
**FRs covered:** FR5, FR26, FR27, FR28, FR29

### Epic 6: Extensible enrichment pipeline (future stages + providers)
Michel can expand the tool over time by enabling/disabling stages and optional provider adapters without changing the core CLI run workflow.
**FRs covered:** FR33, FR34, FR36, FR37, FR38

## Epic 1: Run playlist enrichment safely (core CLI workflow)

Michel can target a Rekordbox playlist and run enrichment confidently with a scriptable CLI, clear progress, and consistent run summaries.

### Story 1.1: Set up initial project from starter template (uv + Typer)

As Michel,
I want the project scaffolded using the chosen starter approach,
So that development starts from a clean, maintainable baseline.

**Implements:** FR1, Additional requirement (Starter template: `uv` + Typer + Rich; `pytest`/`ruff`/`mypy` dev tooling)

**Acceptance Criteria:**

**Given** I have Python tooling available
**When** I initialize the project using `uv` and add Typer and Rich
**Then** the project has a runnable CLI entrypoint
**And** `music-library-sanitzer --help` works and shows a `run` command placeholder.

### Story 1.2: Load config file and apply CLI overrides

As Michel,
I want configuration defaults loaded from a config file with CLI overrides,
So that I can set stable defaults but still adjust per run.

**Implements:** FR2, FR3

**Acceptance Criteria:**

**Given** a config file exists with defaults (e.g., library path, backup path, stage toggles)
**When** I run the CLI with `--config` and also provide overriding flags
**Then** the effective configuration uses CLI values over file values
**And** invalid configuration is rejected with a non-zero exit code and no writes.

### Story 1.3: Resolve playlist by stable ID and preflight display

As Michel,
I want to target a playlist by stable ID and see which playlist is resolved,
So that I know I’m enriching the right set of tracks before any changes.

**Implements:** FR6, FR7, FR8

**Acceptance Criteria:**

**Given** I provide `--playlist-id <id>`
**When** the tool starts a run
**Then** it resolves the playlist to a human-readable name (if available) and a track count
**And** it prints this preflight information before any write-related steps run.

### Story 1.4: Human-readable progress and run summary

As Michel,
I want clear progress and a concise run summary,
So that I can trust the tool is working and understand the outcome quickly.

**Implements:** FR25, FR28

**Acceptance Criteria:**

**Given** a run is processing multiple tracks
**When** the tool performs analysis and planning
**Then** it emits human-readable progress indicating work is advancing
**And** at the end it prints a summary with counts: processed, updated, unchanged, skipped, failed.

### Story 1.5: Exit code semantics for scripting

As Michel,
I want distinct exit codes for success, partial success, and failure,
So that I can automate enrichment in scripts safely.

**Implements:** FR29

**Acceptance Criteria:**

**Given** a run completes with all tracks handled successfully
**When** the tool exits
**Then** it returns the “success” exit code
**And** it returns “partial success” when there are any skipped/failed tracks
**And** it returns “failure” when a fail-closed precondition fails before writes.

## Epic 2: Plan changes before writing (deterministic write planning + dry run)

Michel can preview exactly what would change, and trust that re-running with the same inputs yields consistent and idempotent results.

### Story 2.1: Build a deterministic write plan from inputs

As Michel,
I want the tool to compute a deterministic write plan before any write occurs,
So that I can trust reruns won’t drift and that changes are intentional.

**Implements:** FR30, FR31

**Acceptance Criteria:**

**Given** the same playlist tracks and the same effective configuration
**When** I run the tool twice
**Then** the computed write plan is identical (same per-track planned actions and cue content)
**And** the plan is created before any backup/write steps begin.

### Story 2.2: Dry-run mode shows intended changes without writing

As Michel,
I want a `--dry-run` mode that previews intended changes,
So that I can verify the plan without risking my library.

**Implements:** FR4, FR24

**Acceptance Criteria:**

**Given** I run `music-library-sanitzer run --playlist-id <id> --dry-run`
**When** the tool completes
**Then** it reports which tracks would be changed and how (planned cue additions/updates)
**And** it performs zero writes to the Rekordbox library and creates no backup.

### Story 2.3: Idempotency rules prevent cue thrashing on reruns

As Michel,
I want reruns to avoid duplicating or thrashing tool-created cues,
So that repeated enrichment is safe and stable.

**Implements:** FR31

**Acceptance Criteria:**

**Given** a successful previous run created tool-provenanced cues
**When** I rerun the tool with unchanged inputs
**Then** the plan results in “unchanged” outcomes for those tracks
**And** it does not create duplicate cues or move cues between slots unexpectedly.

### Story 2.4: Regeneration updates only tool-created cues when needed

As Michel,
I want the tool to update previously tool-created cues when regeneration is needed,
So that improvements can be applied without touching my manual cues.

**Implements:** FR32, FR12

**Acceptance Criteria:**

**Given** a track has tool-created cues from a prior run
**When** a regeneration trigger occurs (e.g., config change or algorithm update)
**Then** the plan may update only tool-created cues according to the overwrite policy
**And** it never overwrites user-created cues.

## Epic 3: Protect Rekordbox library integrity (backup/restore + fail-closed execution)

Michel can safely write changes with a verified backup/restore safety net and strict “fail closed” behavior before any write occurs.

### Story 3.1: Enforce fail-closed preconditions before any write

As Michel,
I want the tool to abort before writing on unexpected conditions,
So that my Rekordbox library integrity is protected.

**Implements:** NFR2, NFR3, NFR4, Additional requirement (Safety precondition order)

**Acceptance Criteria:**

**Given** the tool is running in write mode (not `--dry-run`)
**When** any precondition fails (e.g., cannot validate config, cannot resolve playlist, cannot build plan)
**Then** the tool aborts before writing any changes
**And** it returns a failure exit code with a clear error message.

### Story 3.2: Create a pre-write backup for write runs

As Michel,
I want an automatic backup created before any write is applied,
So that I can recover if something goes wrong.

**Implements:** FR14, FR15, FR16

**Acceptance Criteria:**

**Given** the tool has a non-empty write plan
**When** a write run begins
**Then** it creates a backup at the configured location (default `~/.music-library-sanitzer/backups`)
**And** if backup creation fails, the run aborts before any write.

### Story 3.3: Backup retention keeps the 50 most recent backups

As Michel,
I want old backups cleaned up automatically,
So that disk usage stays bounded.

**Implements:** FR17

**Acceptance Criteria:**

**Given** more than 50 backups exist in the backup directory
**When** a new backup is created successfully
**Then** the tool removes older backups to keep only the 50 most recent
**And** it reports which backups were removed (at least in logs).

### Story 3.4: List available backups

As Michel,
I want to list backups with timestamps/identifiers,
So that I can choose a restore point.

**Implements:** FR18

**Acceptance Criteria:**

**Given** backups exist
**When** I run a CLI command to list backups
**Then** it outputs at minimum a timestamp and an identifier for each backup
**And** it returns a success exit code.

### Story 3.5: Restore from backup and report verification

As Michel,
I want to restore the Rekordbox library from a selected backup with verification/reporting,
So that I can recover confidently.

**Implements:** FR19, FR20

**Acceptance Criteria:**

**Given** I select a specific backup identifier
**When** I run the restore command
**Then** the tool restores the library from that backup
**And** it reports completion and any verification signals (e.g., file presence/size/hash checks).

## Epic 4: Generate and write hot cues with provenance + overwrite policy

Michel gets usable hot cues in Rekordbox without overwriting manual cues, and the tool can safely recognize and update only its own cues later.

### Story 4.1: Read current hot cues for targeted tracks

As Michel,
I want the tool to read existing hot cues for tracks in the target playlist,
So that it can plan changes safely and avoid overwriting my manual work.

**Implements:** FR9

**Acceptance Criteria:**

**Given** a playlist is resolved to a set of tracks
**When** the tool loads track state for planning
**Then** it reads each track’s existing hot cue slots and values
**And** it surfaces read failures as per-track failures (or aborts if fail-closed applies).

### Story 4.2: Generate hot cue candidates per eligible track

As Michel,
I want hot cue candidates generated per track,
So that the tool can enrich tracks that are missing high-impact cues.

**Implements:** FR21

**Acceptance Criteria:**

**Given** an eligible audio track in the playlist
**When** the hot cue generation stage runs
**Then** it produces a set of cue candidates sufficient to fill configured slots
**And** it can mark tracks as skipped/failed with a reason when generation cannot be performed.

### Story 4.3: Slot selection policy chooses which cues to fill/update

As Michel,
I want the tool to choose cue slots to fill based on policy and existing cues,
So that it respects my library and applies changes predictably.

**Implements:** FR11, FR22

**Acceptance Criteria:**

**Given** existing cues are present on a track
**When** building the per-track write plan
**Then** the tool selects only allowed slots to fill
**And** it never selects a slot containing a user-created cue for overwrite.

### Story 4.4: Provenance tagging and detection for tool-created cues

As Michel,
I want the tool to recognize cues it previously created,
So that it can safely update only those cues later.

**Implements:** FR12, FR13, FR35

**Acceptance Criteria:**

**Given** the tool writes a hot cue
**When** it persists run state
**Then** it records provenance sufficient to identify that cue later
**And** on subsequent runs it can detect whether an existing cue is tool-created.

### Story 4.5: Apply write plan to Rekordbox library with policy enforcement

As Michel,
I want the tool to write planned hot cues into Rekordbox safely,
So that results are visible and usable inside Rekordbox without risking my manual cues.

**Implements:** FR10, FR23, FR11, FR12

**Acceptance Criteria:**

**Given** a backup was created successfully and a deterministic write plan exists
**When** the tool applies writes
**Then** only planned cues are written
**And** policy enforcement prevents overwriting user-created cues
**And** updated cues are visible in Rekordbox after the run.

### Story 4.6: Produce per-track outcomes with reasons

As Michel,
I want per-track outcomes (updated/unchanged/skipped/failed) with reasons,
So that I can spot-check and triage problematic tracks.

**Implements:** FR26, FR27

**Acceptance Criteria:**

**Given** a run processes multiple tracks
**When** it completes
**Then** each track has an outcome status
**And** skipped/failed tracks include a human-readable reason.

## Epic 5: Reporting & automation outputs (JSON summary + track outcomes)

Michel can automate runs and archive outcomes with machine-readable summaries and per-track status details.

### Story 5.1: Emit a JSON run summary for automation

As Michel,
I want a machine-readable JSON summary of the run,
So that I can automate, archive, and analyze outcomes over time.

**Implements:** FR5, FR26, FR27, FR28, FR29

**Acceptance Criteria:**

**Given** I run with `--json` enabled
**When** the run completes
**Then** the tool outputs a JSON document including playlist id, run id, counts, and exit code classification
**And** the JSON includes per-track outcomes (status + reason where applicable).

### Story 5.2: Keep human logs and JSON outputs consistent

As Michel,
I want human-readable logs and JSON output to reflect the same underlying outcomes,
So that troubleshooting is straightforward.

**Implements:** FR28, FR29

**Acceptance Criteria:**

**Given** the same run
**When** I compare console summary counts to JSON counts
**Then** they match
**And** the run exit code classification aligns with those outcomes.

## Epic 6: Extensible enrichment pipeline (future stages + providers)

Michel can expand the tool over time by enabling/disabling stages and optional provider adapters without changing the core CLI run workflow.

### Story 6.1: Define pipeline stage framework and stage toggles

As Michel,
I want enrichment implemented as a pipeline with stages that can be enabled/disabled,
So that the tool can grow beyond hot cues without redesigning the CLI.

**Implements:** FR33, FR34

**Acceptance Criteria:**

**Given** configuration includes stage toggles
**When** I run the tool with a stage disabled
**Then** that stage does not execute
**And** the run still produces a valid plan/outcome for the enabled stages.

### Story 6.2: Add a new stage without changing the run workflow

As Michel,
I want the ability to add a new enrichment stage later without changing how I run the tool,
So that future features don’t break my automation.

**Implements:** FR36

**Acceptance Criteria:**

**Given** a new stage is implemented and registered
**When** I run the tool with that stage enabled
**Then** it executes within the same `run --playlist-id` workflow
**And** it contributes planned actions and outcomes in the same reporting structure.

### Story 6.3: Provider adapter interface and opt-in network behavior

As Michel,
I want provider integrations to be optional and controlled,
So that network usage is intentional and does not risk unsafe writes.

**Implements:** FR37, NFR5, NFR6, NFR7

**Acceptance Criteria:**

**Given** providers are disabled by default
**When** I run the tool without enabling providers
**Then** no network calls are performed
**And** when providers are enabled, the tool clearly indicates network usage is active.

### Story 6.4: Provider caching capability for repeated runs

As Michel,
I want provider calls to be cacheable,
So that repeated runs don’t hammer external services and run faster over time.

**Implements:** FR38, NFR7

**Acceptance Criteria:**

**Given** providers are enabled and caching is configured/available
**When** I run enrichment twice over the same inputs
**Then** repeated provider lookups can be served from cache where applicable
**And** failures in optional providers degrade gracefully according to the fail-closed rules.
