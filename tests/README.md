# Tests

## Setup (local)

1. Install dependencies (creates `.venv` automatically):
   - `uv sync`
2. Configure env:
   - `cp .env.example .env`
   - Edit `BASE_URL` if your CLI needs it (optional)

## Run E2E tests

- `uv run pytest -m e2e`

## Notes

- E2E for this project means running the CLI end-to-end (via subprocess) against a test Rekordbox library fixture.
- Keep tests isolated; any created data should be cleaned up in teardown.
