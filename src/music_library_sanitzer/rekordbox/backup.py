from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2, rmtree

from ..errors import PreconditionFailure


_BACKUP_NAME_RE = re.compile(r"^(?P<timestamp>\d{8}-\d{6})(?:-(?P<suffix>\d+))?$")


def _current_timestamp() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y%m%d-%H%M%S")


def _parse_backup_dir_name(name: str) -> tuple[datetime, int, int] | None:
    match = _BACKUP_NAME_RE.match(name)
    if not match:
        return None
    timestamp = match.group("timestamp")
    suffix_raw = match.group("suffix")
    suffix_present = 1 if suffix_raw is not None else 0
    suffix = int(suffix_raw) if suffix_raw is not None else 0
    try:
        parsed = datetime.strptime(timestamp, "%Y%m%d-%H%M%S").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        return None
    return parsed, suffix_present, suffix


def list_backup_directories(backup_root: Path) -> list[Path]:
    try:
        entries = [path for path in backup_root.iterdir() if path.is_dir()]
    except OSError as exc:
        raise PreconditionFailure(
            f"Backup retention failed: {exc}",
            stage="backup_retention",
        ) from exc

    def sort_key(path: Path) -> tuple[datetime, int, int, str]:
        parsed = _parse_backup_dir_name(path.name)
        if parsed is not None:
            timestamp, suffix_present, suffix = parsed
            return (timestamp, suffix_present, suffix, path.name)
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        except OSError as exc:
            raise PreconditionFailure(
                f"Backup retention failed: {exc}",
                stage="backup_retention",
            ) from exc
        return (mtime, 0, 0, path.name)

    return sorted(entries, key=sort_key, reverse=True)


def prune_backup_retention(backup_root: Path, keep: int = 50) -> list[str]:
    backups = list_backup_directories(backup_root)
    if len(backups) <= keep:
        return []

    to_remove = backups[keep:]
    removed: list[str] = []
    for backup_dir in reversed(to_remove):
        try:
            rmtree(backup_dir)
        except OSError as exc:
            raise PreconditionFailure(
                f"Backup retention failed: {exc}",
                stage="backup_retention",
            ) from exc
        removed.append(backup_dir.name)

    return removed


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
