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
        },
        generation_id="gen-1",
    )

    updated = apply_idempotency([track], provenance, regeneration_trigger=False)

    assert updated[0].planned_action.action == "noop"
    assert updated[0].planned_action.reason == "unchanged"
    assert updated[0].cues == ()


def test_apply_idempotency_blocks_changes_without_trigger() -> None:
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

    updated = apply_idempotency([track], provenance, regeneration_trigger=False)

    assert updated[0].planned_action.action == "noop"
    assert updated[0].planned_action.reason == "no_regeneration_trigger"
    assert updated[0].cues == ()


def test_apply_idempotency_allows_updates_with_trigger() -> None:
    track = TrackPlan(
        track_index=1,
        track_id="TRK-1",
        planned_action=PlannedAction(action="update", reason="add_cue"),
        cues=(
            CuePlan(
                slot=1,
                start_ms=1500,
                label="Intro",
                color="red",
                source="planner",
            ),
            CuePlan(
                slot=2,
                start_ms=2000,
                label="Drop",
                color="blue",
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
        },
        generation_id="gen-1",
    )

    updated = apply_idempotency([track], provenance, regeneration_trigger=True)

    assert updated[0].planned_action.action == "update"
    assert updated[0].cues == (
        CuePlan(
            slot=1,
            start_ms=1500,
            label="Intro",
            color="red",
            source="planner",
        ),
    )


def test_apply_idempotency_drops_non_tool_slots_on_regen() -> None:
    track = TrackPlan(
        track_index=1,
        track_id="TRK-1",
        planned_action=PlannedAction(action="update", reason="add_cue"),
        cues=(
            CuePlan(
                slot=3,
                start_ms=2500,
                label="Outro",
                color="green",
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
        },
        generation_id="gen-1",
    )

    updated = apply_idempotency([track], provenance, regeneration_trigger=True)

    assert updated[0].planned_action.action == "noop"
    assert updated[0].planned_action.reason == "no_tool_cues_to_update"
    assert updated[0].cues == ()


def test_apply_idempotency_requires_verified_provenance() -> None:
    track = TrackPlan(
        track_index=1,
        track_id="TRK-1",
        planned_action=PlannedAction(action="update", reason="add_cue"),
        cues=(
            CuePlan(
                slot=1,
                start_ms=1500,
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
        },
        generation_id=None,
    )

    updated = apply_idempotency([track], provenance, regeneration_trigger=True)

    assert updated[0].planned_action.action == "noop"
    assert updated[0].planned_action.reason == "provenance_unverified"
    assert updated[0].cues == ()


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
        },
        generation_id="gen-1",
    )

    persist_provenance_index(index, base_dir=tmp_path)
    loaded = load_provenance_index(base_dir=tmp_path)

    assert loaded == index


def test_build_write_plan_does_not_persist_provenance_before_write(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("MLS_STATE_DIR", str(tmp_path))
    try:
        from music_library_sanitzer.pipeline.executor import (
            build_write_plan_for_preconditions,
        )
        from music_library_sanitzer.config.model import Config
        from music_library_sanitzer.rekordbox.playlist import ResolvedPlaylist

        config = Config(
            library_path=Path("/tmp/library.xml"),
            backup_path=Path("/tmp/backups"),
            stage_hot_cues=True,
            stage_energy=False,
            dry_run=False,
        )
        playlist = ResolvedPlaylist(
            playlist_id="PL-ALPHA",
            name="Alpha Set",
            track_count=1,
            track_ids=("TRK-1",),
        )

        build_write_plan_for_preconditions(config, playlist)
        provenance_path = tmp_path / "provenance" / "cue_provenance.json"
        assert provenance_path.exists() is False
        loaded = load_provenance_index(base_dir=tmp_path)
        assert loaded.generation_id is None
        assert loaded.tracks == {}
    finally:
        monkeypatch.setenv("MLS_STATE_DIR", "")
