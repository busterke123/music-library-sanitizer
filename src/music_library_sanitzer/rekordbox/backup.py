from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from shutil import copy2, rmtree

from ..errors import PreconditionFailure


_BACKUP_NAME_RE = re.compile(r"^(?P<timestamp>\d{8}-\d{6})(?:-(?P<suffix>\d+))?$")


@dataclass(frozen=True)
class BackupEntry:
    identifier: str
    timestamp: datetime
    path: Path


@dataclass(frozen=True)
class RestoreVerification:
    identifier: str
    backup_file: Path
    restored_file: Path
    backup_size: int
    restored_size: int
    restored_exists: bool
    size_match: bool


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


def _raise_backup_failure(
    exc: OSError,
    stage: str,
    action: str,
) -> None:
    raise PreconditionFailure(f"{action} failed: {exc}", stage=stage) from exc


def _iter_backup_directories(
    backup_root: Path,
    stage: str,
    action: str,
) -> list[Path]:
    try:
        return [path for path in backup_root.iterdir() if path.is_dir()]
    except FileNotFoundError as exc:
        if stage == "list_backups":
            return []
        _raise_backup_failure(exc, stage=stage, action=action)
    except OSError as exc:
        _raise_backup_failure(exc, stage=stage, action=action)
    return []


def _backup_sort_key(
    path: Path,
    stage: str,
    action: str,
) -> tuple[datetime, int, int, str]:
    parsed = _parse_backup_dir_name(path.name)
    if parsed is not None:
        timestamp, suffix_present, suffix = parsed
        return (timestamp, suffix_present, suffix, path.name)
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    except OSError as exc:
        _raise_backup_failure(exc, stage=stage, action=action)
    return (mtime, 0, 0, path.name)


def list_backup_directories(backup_root: Path) -> list[Path]:
    entries = _iter_backup_directories(
        backup_root,
        stage="backup_retention",
        action="Backup retention",
    )
    return sorted(
        entries,
        key=lambda path: _backup_sort_key(
            path,
            stage="backup_retention",
            action="Backup retention",
        ),
        reverse=True,
    )


def list_backups(backup_root: Path) -> list[BackupEntry]:
    entries = _iter_backup_directories(
        backup_root,
        stage="list_backups",
        action="Backup listing",
    )
    grouped: list[tuple[tuple[datetime, int, int, str], BackupEntry]] = []
    for path in entries:
        sort_key = _backup_sort_key(
            path,
            stage="list_backups",
            action="Backup listing",
        )
        timestamp = sort_key[0]
        grouped.append(
            (
                sort_key,
                BackupEntry(
                    identifier=path.name,
                    timestamp=timestamp,
                    path=path,
                ),
            )
        )
    grouped.sort(key=lambda item: item[0], reverse=True)
    return [entry for _, entry in grouped]


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


def restore_backup(
    library_path: Path,
    backup_root: Path,
    identifier: str,
) -> RestoreVerification:
    identifier_path = Path(identifier)
    if (
        not identifier
        or identifier in {".", ".."}
        or identifier_path.is_absolute()
        or identifier_path.name != identifier
        or identifier_path.drive
    ):
        raise PreconditionFailure(
            f"Invalid backup identifier: {identifier}",
            stage="restore_backup",
        )

    backup_root_resolved = backup_root.resolve()
    backup_dir = (backup_root / identifier).resolve()
    if backup_root_resolved not in backup_dir.parents:
        raise PreconditionFailure(
            f"Backup identifier escapes backup root: {identifier}",
            stage="restore_backup",
        )
    if not backup_dir.is_dir():
        raise PreconditionFailure(
            f"Backup directory not found: {backup_dir}",
            stage="restore_backup",
        )

    backup_file = backup_dir / library_path.name
    if not backup_file.is_file():
        raise PreconditionFailure(
            f"Backup file not found: {backup_file}",
            stage="restore_backup",
        )

    temp_fd, temp_path = tempfile.mkstemp(
        prefix=f".{library_path.name}.",
        suffix=".tmp",
        dir=library_path.parent,
    )
    os.close(temp_fd)
    temp_file = Path(temp_path)

    try:
        copy2(backup_file, temp_file)
        try:
            backup_size = backup_file.stat().st_size
            temp_size = temp_file.stat().st_size
        except OSError as exc:
            raise PreconditionFailure(
                f"Backup verification failed: {exc}",
                stage="restore_backup",
            ) from exc
        if temp_size != backup_size:
            raise PreconditionFailure(
                "Backup verification failed: size mismatch during copy.",
                stage="restore_backup",
            )
        temp_file.replace(library_path)
    except PreconditionFailure:
        raise
    except OSError as exc:
        raise PreconditionFailure(
            f"Backup restore failed: {exc}",
            stage="restore_backup",
        ) from exc
    finally:
        try:
            if temp_file.exists():
                temp_file.unlink()
        except OSError:
            pass

    try:
        restored_exists = library_path.exists()
        restored_size = library_path.stat().st_size if restored_exists else 0
    except OSError as exc:
        raise PreconditionFailure(
            f"Backup verification failed: {exc}",
            stage="restore_backup",
        ) from exc
    if not restored_exists or restored_size != backup_size:
        raise PreconditionFailure(
            "Backup verification failed: restored file mismatch.",
            stage="restore_backup",
        )

    return RestoreVerification(
        identifier=identifier,
        backup_file=backup_file,
        restored_file=library_path,
        backup_size=backup_size,
        restored_size=restored_size,
        restored_exists=restored_exists,
        size_match=restored_exists and restored_size == backup_size,
    )
