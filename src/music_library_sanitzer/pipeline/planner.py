from __future__ import annotations

import hashlib
import json
from dataclasses import replace

from .models import ConfigSnapshot, CuePlan, PlannedAction, TrackPlan, WritePlan
from ..config.model import Config
from ..rekordbox.playlist import ResolvedPlaylist
from ..state.provenance import CueProvenanceIndex, ProvenanceCue, load_provenance_index


def _inputs_hash(
    config_snapshot: ConfigSnapshot,
    playlist: ResolvedPlaylist,
    provenance_hash: str,
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
            "provenance_hash": provenance_hash,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _cue_signature(
    cue: CuePlan,
) -> tuple[int, int | None, str | None, str | None, str | None]:
    return (cue.slot, cue.start_ms, cue.label, cue.color, cue.source)


def _provenance_signature(
    cue: ProvenanceCue,
) -> tuple[int, int | None, str | None, str | None, str | None]:
    return (cue.slot, cue.start_ms, cue.label, cue.color, cue.source)


def provenance_fingerprint(index: CueProvenanceIndex) -> str:
    payload = json.dumps(index.to_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def extract_provenance_from_plan(plan: WritePlan) -> CueProvenanceIndex:
    tracks: dict[str, tuple[ProvenanceCue, ...]] = {}
    for track in plan.tracks:
        if track.track_id is None:
            continue
        if track.planned_action.action in {"noop", "skip"}:
            continue
        if not track.cues:
            continue
        tracks[track.track_id] = tuple(
            ProvenanceCue(
                slot=cue.slot,
                start_ms=cue.start_ms,
                label=cue.label,
                color=cue.color,
                source=cue.source,
            )
            for cue in track.cues
        )
    return CueProvenanceIndex(tracks=tracks)


def apply_idempotency(
    track_plans: list[TrackPlan],
    provenance: CueProvenanceIndex,
) -> tuple[TrackPlan, ...]:
    updated: list[TrackPlan] = []
    for track in track_plans:
        if track.track_id is None:
            updated.append(track)
            continue
        if track.planned_action.action in {"noop", "skip"}:
            updated.append(track)
            continue
        if not track.cues:
            updated.append(track)
            continue
        existing = provenance.tracks.get(track.track_id)
        if not existing:
            updated.append(track)
            continue
        planned = sorted((_cue_signature(cue) for cue in track.cues))
        recorded = sorted((_provenance_signature(cue) for cue in existing))
        if planned == recorded:
            updated.append(
                replace(
                    track,
                    planned_action=PlannedAction(action="noop", reason="unchanged"),
                    cues=(),
                )
            )
        else:
            updated.append(track)
    return tuple(updated)


def build_write_plan(config: Config, playlist: ResolvedPlaylist) -> WritePlan:
    config_snapshot = ConfigSnapshot.from_config(config)
    provenance = load_provenance_index()
    provenance_hash = provenance_fingerprint(provenance)
    inputs_hash = _inputs_hash(config_snapshot, playlist, provenance_hash)
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

    normalized_tracks = apply_idempotency(track_plans, provenance)

    return WritePlan(
        plan_version=1,
        inputs_hash=inputs_hash,
        playlist_id=playlist.playlist_id,
        playlist_name=playlist.name,
        track_count=playlist.track_count,
        config=config_snapshot,
        tracks=normalized_tracks,
    )
