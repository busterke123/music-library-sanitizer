from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from ..config.model import Config


@dataclass(frozen=True)
class ConfigSnapshot:
    library_path: str
    backup_path: str
    stage_hot_cues: bool
    stage_energy: bool
    dry_run: bool

    @classmethod
    def from_config(cls, config: Config) -> "ConfigSnapshot":
        return cls(
            library_path=config.library_path.as_posix(),
            backup_path=config.backup_path.as_posix(),
            stage_hot_cues=config.stage_hot_cues,
            stage_energy=config.stage_energy,
            dry_run=config.dry_run,
        )


@dataclass(frozen=True)
class PlannedAction:
    action: str
    reason: str | None


@dataclass(frozen=True)
class CuePlan:
    slot: int
    start_ms: int | None
    label: str | None
    color: str | None
    source: str | None


@dataclass(frozen=True)
class ExistingCue:
    slot: int
    start_ms: int | None
    label: str | None
    color: str | None
    source: str | None


@dataclass(frozen=True)
class TrackPlan:
    track_index: int
    track_id: str | None
    planned_action: PlannedAction
    cues: tuple[CuePlan, ...]
    existing_cues: tuple[ExistingCue, ...] = ()


@dataclass(frozen=True)
class WritePlan:
    plan_version: int
    inputs_hash: str
    playlist_id: str
    playlist_name: str | None
    track_count: int
    config: ConfigSnapshot
    tracks: tuple[TrackPlan, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
