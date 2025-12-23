from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..config.model import Config
from ..errors import PlaylistResolutionError, PreconditionFailure
from ..rekordbox.playlist import ResolvedPlaylist, resolve_playlist
from ..state.provenance import (
    load_provenance_index,
    merge_provenance_indexes,
    persist_provenance_index,
)
from ..state.runs import persist_write_plan
from .models import WritePlan
from .planner import build_write_plan, current_generation_id, extract_provenance_from_plan


@dataclass(frozen=True)
class PreconditionResult:
    resolved: ResolvedPlaylist
    plan: WritePlan


def build_write_plan_for_preconditions(
    config: Config,
    resolved: ResolvedPlaylist,
) -> WritePlan:
    plan = build_write_plan(config, resolved)
    persist_write_plan(plan)
    return plan


def persist_provenance_after_write(
    config: Config,
    plan: WritePlan,
) -> None:
    generation_id = current_generation_id(config)
    updates = extract_provenance_from_plan(
        plan,
        generation_id=generation_id,
    )
    existing = load_provenance_index()
    merged = merge_provenance_indexes(existing, updates)
    if merged.generation_id != existing.generation_id or updates.tracks:
        persist_provenance_index(merged)


def _validate_write_config(config: Config) -> None:
    if config.dry_run:
        raise PreconditionFailure(
            "Invalid config for write run: dry-run is enabled.",
            stage="validate_config",
        )
    if not isinstance(config.library_path, Path) or not isinstance(
        config.backup_path, Path
    ):
        raise PreconditionFailure(
            "Invalid config: library_path and backup_path must be Paths.",
            stage="validate_config",
        )
    if not config.library_path.is_absolute():
        raise PreconditionFailure(
            f"Invalid config: library_path must be absolute ({config.library_path}).",
            stage="validate_config",
        )
    if not config.backup_path.is_absolute():
        raise PreconditionFailure(
            f"Invalid config: backup_path must be absolute ({config.backup_path}).",
            stage="validate_config",
        )


def run_write_preconditions(
    config: Config,
    playlist_id: str,
) -> PreconditionResult:
    _validate_write_config(config)

    try:
        resolved = resolve_playlist(config.library_path, playlist_id)
    except PlaylistResolutionError as exc:
        raise PreconditionFailure(
            f"Playlist resolution error: {exc}",
            stage="resolve_playlist",
        ) from exc

    try:
        plan = build_write_plan_for_preconditions(config, resolved)
    except Exception as exc:
        raise PreconditionFailure(
            f"Write plan error: {exc}",
            stage="build_plan",
        ) from exc

    return PreconditionResult(resolved=resolved, plan=plan)
