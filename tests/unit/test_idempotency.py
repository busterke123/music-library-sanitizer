from pathlib import Path

from music_library_sanitzer.pipeline.models import CuePlan, PlannedAction, TrackPlan
from music_library_sanitzer.pipeline.planner import apply_idempotency
from music_library_sanitzer.state.provenance import (
    CueProvenanceIndex,
    ProvenanceCue,
    load_provenance_index,
    persist_provenance_index,
)


def test_apply_idempotency_marks_noop_for_matching_provenance() -> None:
    track = TrackPlan(
        track_index=1,
        track_id="TRK-1",
        planned_action=PlannedAction(action="update", reason="add_cue"),
        cues=(
            CuePlan(
                slot=1,
                start_ms=1000,
                label="Intro",
                color="red",
                source="planner",
            ),
        ),
    )
    provenance = CueProvenanceIndex(
        tracks={
            "TRK-1": (
                ProvenanceCue(
                    slot=1,
                    start_ms=1000,
                    label="Intro",
                    color="red",
                    source="planner",
                ),
            )
        }
    )

    updated = apply_idempotency([track], provenance)

    assert updated[0].planned_action.action == "noop"
    assert updated[0].planned_action.reason == "unchanged"
    assert updated[0].cues == ()


def test_apply_idempotency_keeps_changes_when_mismatch() -> None:
    track = TrackPlan(
        track_index=1,
        track_id="TRK-1",
        planned_action=PlannedAction(action="update", reason="add_cue"),
        cues=(
            CuePlan(
                slot=1,
                start_ms=1000,
                label="Intro",
                color="red",
                source="planner",
            ),
        ),
    )
    provenance = CueProvenanceIndex(
        tracks={
            "TRK-1": (
                ProvenanceCue(
                    slot=1,
                    start_ms=2000,
                    label="Intro",
                    color="red",
                    source="planner",
                ),
            )
        }
    )

    updated = apply_idempotency([track], provenance)

    assert updated[0].planned_action.action == "update"
    assert updated[0].cues == track.cues


def test_provenance_index_roundtrip(tmp_path: Path) -> None:
    index = CueProvenanceIndex(
        tracks={
            "TRK-1": (
                ProvenanceCue(
                    slot=1,
                    start_ms=500,
                    label=None,
                    color=None,
                    source=None,
                ),
            )
        }
    )

    persist_provenance_index(index, base_dir=tmp_path)
    loaded = load_provenance_index(base_dir=tmp_path)

    assert loaded == index
