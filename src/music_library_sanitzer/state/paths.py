from __future__ import annotations

import os
from pathlib import Path


def resolve_state_dirs(base_dir: Path | None = None) -> list[Path]:
    if base_dir is not None:
        return [base_dir]
    env_override = os.getenv("MLS_STATE_DIR")
    if env_override:
        return [Path(env_override).expanduser()]
    return [
        Path("~/.music-library-sanitzer/state").expanduser(),
        Path.cwd() / ".music-library-sanitzer" / "state",
    ]
