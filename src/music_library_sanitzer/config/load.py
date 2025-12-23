from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import tomllib

from .model import Config, DEFAULT_BACKUP_PATH, DEFAULT_CONFIG_PATH, DEFAULT_LIBRARY_PATH


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class ConfigOverrides:
    library_path: Path | None = None
    backup_path: Path | None = None
    stage_hot_cues: bool | None = None
    stage_energy: bool | None = None
    dry_run: bool | None = None


_ALLOWED_KEYS = {
    "library_path",
    "backup_path",
    "stage_hot_cues",
    "stage_energy",
    "dry_run",
}


def _normalize_path(path: Path, *, base_dir: Path) -> Path:
    expanded = path.expanduser()
    if expanded.is_absolute():
        return expanded.resolve()
    return (base_dir / expanded).resolve()


def _load_toml(path: Path) -> Mapping[str, Any]:
    with path.open("rb") as handle:
        try:
            data = tomllib.load(handle)
        except tomllib.TOMLDecodeError as exc:
            raise ConfigError(f"Invalid TOML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError("Config file must contain a TOML table at the top level.")
    return data


def _validate_keys(data: Mapping[str, Any]) -> None:
    unknown = set(data.keys()) - _ALLOWED_KEYS
    if unknown:
        raise ConfigError(
            "Unknown config keys: "
            + ", ".join(sorted(unknown))
            + ". Allowed keys: "
            + ", ".join(sorted(_ALLOWED_KEYS))
        )


def _read_path_value(value: Any, key: str, *, base_dir: Path) -> Path:
    if not isinstance(value, str):
        raise ConfigError(f"Invalid type for '{key}': expected string path.")
    return _normalize_path(Path(value), base_dir=base_dir)


def _read_bool_value(value: Any, key: str) -> bool:
    if not isinstance(value, bool):
        raise ConfigError(f"Invalid type for '{key}': expected boolean.")
    return value


def load_config(
    config_path: Path | None,
    overrides: ConfigOverrides,
    *,
    explicit: bool = True,
) -> Config:
    resolved_path = _normalize_path(
        config_path or DEFAULT_CONFIG_PATH, base_dir=Path.cwd()
    )
    data: Mapping[str, Any] = {}
    config_base_dir = resolved_path.parent

    if resolved_path.exists():
        data = _load_toml(resolved_path)
        _validate_keys(data)
    elif explicit:
        raise ConfigError(f"Config file not found: {resolved_path}")

    defaults = Config(
        library_path=_normalize_path(DEFAULT_LIBRARY_PATH, base_dir=Path.cwd()),
        backup_path=_normalize_path(DEFAULT_BACKUP_PATH, base_dir=Path.cwd()),
        stage_hot_cues=True,
        stage_energy=False,
        dry_run=False,
    )

    if "library_path" in data:
        file_library_path = _read_path_value(
            data["library_path"], "library_path", base_dir=config_base_dir
        )
    else:
        file_library_path = defaults.library_path

    if "backup_path" in data:
        file_backup_path = _read_path_value(
            data["backup_path"], "backup_path", base_dir=config_base_dir
        )
    else:
        file_backup_path = defaults.backup_path

    if "stage_hot_cues" in data:
        file_stage_hot_cues = _read_bool_value(data["stage_hot_cues"], "stage_hot_cues")
    else:
        file_stage_hot_cues = defaults.stage_hot_cues

    if "stage_energy" in data:
        file_stage_energy = _read_bool_value(data["stage_energy"], "stage_energy")
    else:
        file_stage_energy = defaults.stage_energy

    if "dry_run" in data:
        file_dry_run = _read_bool_value(data["dry_run"], "dry_run")
    else:
        file_dry_run = defaults.dry_run

    override_library_path = (
        _normalize_path(overrides.library_path, base_dir=Path.cwd())
        if overrides.library_path is not None
        else None
    )
    override_backup_path = (
        _normalize_path(overrides.backup_path, base_dir=Path.cwd())
        if overrides.backup_path is not None
        else None
    )

    return Config(
        library_path=override_library_path or file_library_path,
        backup_path=override_backup_path or file_backup_path,
        stage_hot_cues=(
            overrides.stage_hot_cues
            if overrides.stage_hot_cues is not None
            else file_stage_hot_cues
        ),
        stage_energy=(
            overrides.stage_energy
            if overrides.stage_energy is not None
            else file_stage_energy
        ),
        dry_run=(
            overrides.dry_run if overrides.dry_run is not None else file_dry_run
        ),
    )
