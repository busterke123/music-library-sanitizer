# Tests

## Setup (local)

1. Create a virtualenv (recommended):
   - `python -m venv .venv`
   - `source .venv/bin/activate`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Configure env:
   - `cp .env.example .env`
   - Edit `BASE_URL` if your CLI needs it (optional)

## Run E2E tests

- `pytest -m e2e`

## Notes

- E2E for this project means running the CLI end-to-end (via subprocess) against a test Rekordbox library fixture.
- Keep tests isolated; any created data should be cleaned up in teardown.
