---
workflow: testarch-test-design
mode: system-level
generatedAt: "2025-12-22T22:00:00+01:00"
project: music-library-sanitzer
---

# System-Level Test Design

**Date:** 2025-12-22
**Author:** Arne.driesen
**Scope:** System-level testability review (Phase 3)

## Testability Assessment

- **Controllability: CONCERNS**
  - Strengths: CLI pipeline lends itself to deterministic unit/integration tests; plan→backup→write ordering is explicitly defined.
  - Risks: Rekordbox library IO is inherently stateful and file-format dependent; needs a controllable test fixture strategy (golden files, temp copies, and hermetic writes).
  - Requirement: Provide test fixtures for Rekordbox DB/library representation and a “sandbox” write target (never write to a real library in tests).
- **Observability: PASS (with conditions)**
  - Strengths: PRD requires per-track outcomes, JSON summary, and distinct exit codes; these are directly assertable in tests.
  - Condition: Define stable JSON schemas for write plans and run summaries early (then lock with contract tests).
- **Reliability: CONCERNS**
  - Strengths: Fail-closed and pre-write backup policy is clear.
  - Risks: Partial writes/corruption risk if the writer is not atomic or if crash occurs mid-write; needs atomic write strategy + explicit verification steps.

## Architecturally Significant Requirements (ASRs)

Risk score = Probability (1–3) × Impact (1–3). Scores ≥6 require mitigation.

| ASR ID | Category | Requirement (from PRD/Architecture) | Probability | Impact | Score | Notes / Testability Angle |
| --- | --- | --- | --- | --- | --- | --- |
| ASR-001 | DATA | Fail-closed: abort before writing on unexpected condition | 2 | 3 | 6 | Requires negative-path integration tests; validate “no write occurred”. |
| ASR-002 | DATA | Backup required before any write; abort if backup fails | 2 | 3 | 6 | Requires integration tests that simulate backup failure + assert no write. |
| ASR-003 | TECH | Determinism + idempotency across reruns | 2 | 3 | 6 | Needs golden “same inputs → same plan” tests; enforce stable ordering and schemas. |
| ASR-004 | SEC | Network usage opt-in, bounded, observable; minimize data exposure | 2 | 3 | 6 | Needs tests asserting providers disabled → no outbound calls; enabled → explicit indicator + caching. |
| ASR-005 | OPS | Clear exit codes and machine-readable JSON output | 2 | 2 | 4 | Enables CI gating and automation; requires contract tests for exit code mapping + JSON schema. |
| ASR-006 | PERF | Progress feedback; no strict SLA but runs must be observable | 2 | 2 | 4 | Baseline performance tests/benchmarks for representative playlist sizes. |

## Test Levels Strategy

This is a Python CLI with risky local writes; bias toward lower-level tests and keep E2E focused.

- **Unit: 60%**
  - Planner logic, policy enforcement (no overwrite of user cues), provenance tagging/detection rules, configuration parsing, schema validation.
- **Integration: 35%**
  - File-system interactions (backup retention, atomic write behavior), Rekordbox library read/write against fixture copies, pipeline executor preconditions, provider adapter boundaries with fake servers.
- **E2E (CLI): 5%**
  - Critical CLI flows only: `run --playlist-id` happy path on fixture library, `--dry-run`, `--json` output, backup/restore commands, and fail-closed scenarios.

## NFR Testing Approach

- **Security (SEC)**
  - Default-off providers: tests enforce “no network” in default config (monkeypatch socket / use a deny-all transport).
  - Least data necessary: if providers enabled, validate request payload redaction rules.
  - Secret handling: ensure tokens/keys come from env/config and never appear in logs or JSON summaries.
- **Performance (PERF)**
  - Benchmark key pipelines on representative library sizes (e.g., 30-track playlist) and track regressions.
  - Optional: k6 not applicable; use Python benchmarking (pytest-benchmark) if needed.
- **Reliability (DATA/OPS)**
  - Crash-safety/atomicity tests for writes: verify either fully applied or not applied at all (no partial/corrupt outputs).
  - Determinism tests: same input fixture + config produces identical write plan hashes.
  - Idempotency tests: rerun with same inputs results in “unchanged” outcomes and stable provenance behavior.
- **Maintainability (TECH/OPS)**
  - Enforce coverage thresholds and lint/type checks in CI (ruff/mypy) once the codebase exists.
  - Keep test quality rules: no brittle sleeps, explicit assertions, isolated fixtures, auto-cleanup.

## Test Environment Requirements

- **Fixture libraries**: canonical Rekordbox library fixtures stored as test assets (read-only originals + per-test temp copies).
- **FS sandboxing**: tests must write only under temp dirs; never touch real `~/.music-library-sanitzer` unless explicitly running an integration suite.
- **Provider simulation**: local fake HTTP server for provider adapters; deterministic responses + rate-limit scenarios.
- **Platform coverage**: macOS is primary (Rekordbox), but aim for Linux CI for pure logic tests; file-format tests may need OS-specific gating.

## Testability Concerns (Gate-Relevant)

- **Atomic write strategy undefined** → CONCERNS until the writer guarantees no partial/corrupt library states.
- **Rekordbox library fixture strategy undefined** → CONCERNS until there’s a safe, versioned set of fixtures and validation tooling.
- **JSON schema + exit code mapping not locked** → CONCERNS until contract tests exist.

## Recommendations for Sprint 0

1. Establish canonical JSON schemas: write plan, per-track outcome, run summary; add schema validation in code + contract tests.
2. Implement a safe test fixture harness for Rekordbox libraries (copy-on-write fixtures + integrity checks).
3. Implement and test the fail-closed precondition order: validate → plan → backup → write → report.
4. Add CI gates (once code exists): unit + integration tests, linting, type checking, and coverage threshold.

## References

- PRD: `_bmad-output/prd.md`
- Architecture: `_bmad-output/architecture.md`
- Epics: `_bmad-output/epics.md`
- Knowledge fragments: `risk-governance.md`, `nfr-criteria.md`, `test-levels-framework.md`, `test-quality.md`
