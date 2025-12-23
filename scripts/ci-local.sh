#!/usr/bin/env bash
set -euo pipefail

python_cmd="${PYTHON:-python3}"

echo "Running E2E locally (CI mirror)"
$python_cmd -m pip install --upgrade pip
$python_cmd -m pip install -r requirements.txt

BASE_URL="${BASE_URL:-http://localhost:8000}"
export BASE_URL

mkdir -p test-results
$python_cmd -m pytest -m e2e --junitxml=test-results/junit.xml

echo "Local E2E passed"

