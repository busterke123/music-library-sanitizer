from __future__ import annotations

import hashlib
import json

from .models import ConfigSnapshot, PlannedAction, TrackPlan, WritePlan
from ..config.model import Config
from ..rekordbox.playlist import ResolvedPlaylist


def _inputs_hash(
    config_snapshot: ConfigSnapshot,
    playlist: ResolvedPlaylist,
) -> str:
    payload = json.dumps(
        {
            "config": {
                "library_path": config_snapshot.library_path,
                "backup_path": config_snapshot.backup_path,
                "stage_hot_cues": config_snapshot.stage_hot_cues,
                "stage_energy": config_snapshot.stage_energy,
                "dry_run": config_snapshot.dry_run,
            },
            "playlist_id": playlist.playlist_id,
            "playlist_name": playlist.name,
            "track_ids": list(playlist.track_ids),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_write_plan(config: Config, playlist: ResolvedPlaylist) -> WritePlan:
    config_snapshot = ConfigSnapshot.from_config(config)
    inputs_hash = _inputs_hash(config_snapshot, playlist)
    track_plans: list[TrackPlan] = []

    for index, track_id in enumerate(playlist.track_ids, start=1):
        if track_id is None:
            planned_action = PlannedAction(
                action="skip",
                reason="missing_track_id",
            )
        else:
            planned_action = PlannedAction(action="noop", reason=None)

        track_plans.append(
            TrackPlan(
                track_index=index,
                track_id=track_id,
                planned_action=planned_action,
                cues=(),
            )
        )

    return WritePlan(
        plan_version=1,
        inputs_hash=inputs_hash,
        playlist_id=playlist.playlist_id,
        playlist_name=playlist.name,
        track_count=playlist.track_count,
        config=config_snapshot,
        tracks=tuple(track_plans),
    )
