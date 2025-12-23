# CI

This repo uses GitHub Actions (`.github/workflows/e2e.yml`) to run E2E tests via `pytest -m e2e`.

## What runs when

- Push / PR to `main`: single E2E run
- Scheduled (weekly) + PRs: burn-in loop (10x) to detect flaky E2E tests

## Running locally (CI mirror)

```bash
./scripts/ci-local.sh
```

## Debugging CI failures

- Download the `test-results` artifact to inspect `test-results/junit.xml`
- For burn-in failures, download `burn-in-results` and see which iteration failed (`junit-burn-in-*.xml`)

