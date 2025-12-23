from __future__ import annotations

from pathlib import Path

from .paths import resolve_state_dirs
from ..pipeline.models import WritePlan


def persist_write_plan(plan: WritePlan, *, base_dir: Path | None = None) -> Path:
    last_error: OSError | None = None
    for state_dir in resolve_state_dirs(base_dir):
        try:
            run_dir = state_dir / "runs" / plan.inputs_hash
            run_dir.mkdir(parents=True, exist_ok=True)
            plan_path = run_dir / "write_plan.json"
            plan_path.write_text(plan.to_json(), encoding="utf-8")
            return plan_path
        except OSError as exc:
            last_error = exc
            continue
    if last_error is not None:
        raise last_error
    raise OSError("No writable state directory found for write plan persistence.")
