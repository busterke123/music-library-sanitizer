# CI secrets checklist

This pipeline currently does not require any GitHub Actions secrets.

If you later add integration tests that require credentials, store them as GitHub Actions secrets:

- Repository Settings → Secrets and variables → Actions
- Prefer least-privilege tokens and short-lived credentials where possible

