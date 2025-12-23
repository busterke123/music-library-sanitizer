from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2

from ..errors import PreconditionFailure


def _current_timestamp() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y%m%d-%H%M%S")


def create_backup(library_path: Path, backup_root: Path) -> Path:
    if not library_path.is_file():
        raise PreconditionFailure(
            f"Rekordbox library file not found: {library_path}.",
            stage="create_backup",
        )

    try:
        backup_root.mkdir(parents=True, exist_ok=True)
        timestamp = _current_timestamp()
        backup_dir = backup_root / timestamp
        if backup_dir.exists():
            counter = 1
            while True:
                candidate = backup_root / f"{timestamp}-{counter}"
                if not candidate.exists():
                    backup_dir = candidate
                    break
                counter += 1
        backup_dir.mkdir()
        backup_file = backup_dir / library_path.name
        copy2(library_path, backup_file)
    except OSError as exc:
        raise PreconditionFailure(
            f"Backup creation failed: {exc}",
            stage="create_backup",
        ) from exc

    return backup_file
