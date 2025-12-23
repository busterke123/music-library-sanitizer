#!/usr/bin/env bash
set -euo pipefail

python_cmd="${PYTHON:-python3}"

base_ref="${BASE_REF:-origin/main}"
head_ref="${HEAD_REF:-HEAD}"

changed_files="$(
  git diff --name-only "${base_ref}...${head_ref}" || true
)"

if echo "${changed_files}" | grep -Eq '^(tests/|music_library_sanitzer/|requirements\.txt|pytest\.ini)'; then
  echo "Changes affect tests/runtime; running E2E."
  "${python_cmd}" -m pytest -m e2e
  exit 0
fi

echo "No test-affecting changes detected; skipping E2E."
