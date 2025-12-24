from __future__ import annotations

import hashlib
import json
from dataclasses import replace

from .models import (
    ConfigSnapshot,
    CuePlan,
    ExistingCue,
    PlannedAction,
    TrackPlan,
    WritePlan,
)
from ..config.model import Config
from ..rekordbox.cues import read_existing_hot_cues
from ..rekordbox.playlist import ResolvedPlaylist
from ..state.provenance import CueProvenanceIndex, ProvenanceCue, load_provenance_index


PLAN_VERSION = 1


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
            "plan_version": PLAN_VERSION,
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


def _planned_existing_signature(
    cue: CuePlan,
) -> tuple[int, int | None, str | None, str | None]:
    return (cue.slot, cue.start_ms, cue.label, cue.color)


def _existing_signature(
    cue: ExistingCue,
) -> tuple[int, int | None, str | None, str | None]:
    return (cue.slot, cue.start_ms, cue.label, cue.color)


def provenance_fingerprint(index: CueProvenanceIndex) -> str:
    payload = json.dumps(index.to_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def generation_id(config_snapshot: ConfigSnapshot) -> str:
    payload = json.dumps(
        {
            "config": {
                "library_path": config_snapshot.library_path,
                "backup_path": config_snapshot.backup_path,
                "stage_hot_cues": config_snapshot.stage_hot_cues,
                "stage_energy": config_snapshot.stage_energy,
                "dry_run": config_snapshot.dry_run,
            },
            "plan_version": PLAN_VERSION,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def current_generation_id(config: Config) -> str:
    return generation_id(ConfigSnapshot.from_config(config))


def extract_provenance_from_plan(
    plan: WritePlan,
    *,
    generation_id: str | None,
) -> CueProvenanceIndex:
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
    return CueProvenanceIndex(tracks=tracks, generation_id=generation_id)


def apply_idempotency(
    track_plans: list[TrackPlan],
    provenance: CueProvenanceIndex,
    *,
    regeneration_trigger: bool,
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
        if track.existing_cues:
            planned = {_planned_existing_signature(cue) for cue in track.cues}
            existing = {_existing_signature(cue) for cue in track.existing_cues}
            if planned and planned.issubset(existing):
                updated.append(
                    replace(
                        track,
                        planned_action=PlannedAction(
                            action="noop",
                            reason="existing_cues_match",
                        ),
                        cues=(),
                    )
                )
                continue
        existing = provenance.tracks.get(track.track_id)
        if not existing:
            updated.append(track)
            continue
        if regeneration_trigger and provenance.generation_id is None:
            updated.append(
                replace(
                    track,
                    planned_action=PlannedAction(
                        action="noop",
                        reason="provenance_unverified",
                    ),
                    cues=(),
                )
            )
            continue
        if not regeneration_trigger:
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
                updated.append(
                    replace(
                        track,
                        planned_action=PlannedAction(
                            action="noop",
                            reason="no_regeneration_trigger",
                        ),
                        cues=(),
                    )
                )
            continue

        allowed_slots = {cue.slot for cue in existing}
        filtered_cues = tuple(
            cue
            for cue in track.cues
            if cue.slot in allowed_slots and cue.source is not None
        )
        if not filtered_cues:
            updated.append(
                replace(
                    track,
                    planned_action=PlannedAction(
                        action="noop",
                        reason="no_tool_cues_to_update",
                    ),
                    cues=(),
                )
            )
            continue

        planned = sorted((_cue_signature(cue) for cue in filtered_cues))
        recorded = sorted(
            _provenance_signature(cue)
            for cue in existing
            if cue.slot in {cue.slot for cue in filtered_cues}
        )
        if planned == recorded:
            updated.append(
                replace(
                    track,
                    planned_action=PlannedAction(action="noop", reason="unchanged"),
                    cues=(),
                )
            )
        else:
            updated.append(replace(track, cues=filtered_cues))
    return tuple(updated)


def build_write_plan(config: Config, playlist: ResolvedPlaylist) -> WritePlan:
    config_snapshot = ConfigSnapshot.from_config(config)
    provenance = load_provenance_index()
    provenance_hash = provenance_fingerprint(provenance)
    inputs_hash = _inputs_hash(config_snapshot, playlist, provenance_hash)
    existing_cues, cue_failures = read_existing_hot_cues(
        config.library_path, playlist.track_ids
    )
    track_plans: list[TrackPlan] = []

    for index, track_id in enumerate(playlist.track_ids, start=1):
        if track_id is None:
            planned_action = PlannedAction(
                action="failed",
                reason="missing_track_id",
            )
            track_existing_cues = ()
        elif track_id in cue_failures:
            planned_action = PlannedAction(
                action="failed",
                reason=cue_failures[track_id],
            )
            track_existing_cues = ()
        else:
            planned_action = PlannedAction(action="noop", reason=None)
            track_existing_cues = existing_cues.get(track_id, ())

        track_plans.append(
            TrackPlan(
                track_index=index,
                track_id=track_id,
                planned_action=planned_action,
                cues=(),
                existing_cues=track_existing_cues,
            )
        )

    current_generation_id = generation_id(config_snapshot)
    regeneration_trigger = bool(
        provenance.tracks
        and (
            provenance.generation_id is None
            or provenance.generation_id != current_generation_id
        )
    )
    normalized_tracks = apply_idempotency(
        track_plans,
        provenance,
        regeneration_trigger=regeneration_trigger,
    )

    return WritePlan(
        plan_version=PLAN_VERSION,
        inputs_hash=inputs_hash,
        playlist_id=playlist.playlist_id,
        playlist_name=playlist.name,
        track_count=playlist.track_count,
        config=config_snapshot,
        tracks=normalized_tracks,
    )
