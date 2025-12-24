from pathlib import Path

import pytest

from music_library_sanitzer.config.model import Config
from music_library_sanitzer.errors import PreconditionFailure
from music_library_sanitzer.pipeline.models import (
    ConfigSnapshot,
    CuePlan,
    PlannedAction,
    TrackPlan,
    WritePlan,
)
from music_library_sanitzer.rekordbox.playlist import ResolvedPlaylist


def _sample_plan() -> WritePlan:
    snapshot = ConfigSnapshot(
        library_path="/tmp/library.xml",
        backup_path="/tmp/backups",
        stage_hot_cues=True,
        stage_energy=False,
        dry_run=True,
    )
    return WritePlan(
        plan_version=1,
        inputs_hash="hash",
        playlist_id="PL-ALPHA",
        playlist_name="Alpha Set",
        track_count=2,
        config=snapshot,
        tracks=(
            TrackPlan(
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
            ),
            TrackPlan(
                track_index=2,
                track_id="TRK-2",
                planned_action=PlannedAction(action="noop", reason=None),
                cues=(),
            ),
        ),
    )


def test_format_planned_changes_includes_track_details() -> None:
    import music_library_sanitzer.cli as cli

    plan = _sample_plan()
    lines = cli._format_planned_changes(plan)

    assert "Dry Run Planned Changes" in lines
    assert "Playlist ID: PL-ALPHA" in lines
    assert "Track #1 (TRK-1): update (add_cue); cues:" in lines
    assert "- slot=1, start_ms=1000, label=Intro, color=red, source=planner" in lines
    assert "Track #2 (TRK-2): noop; cues: none" not in lines


def test_statuses_from_plan_maps_actions() -> None:
    import music_library_sanitzer.cli as cli

    plan = _sample_plan()
    statuses, reasons = cli._statuses_from_plan(plan)

    assert statuses == ["updated", "unchanged"]
    assert reasons == []


def test_execute_run_dry_run_builds_plan_and_skips_processing() -> None:
    import music_library_sanitzer.cli as cli

    config = Config(
        library_path=Path("/tmp/library.xml"),
        backup_path=Path("/tmp/backups"),
        stage_hot_cues=True,
        stage_energy=False,
        dry_run=True,
    )
    playlist = ResolvedPlaylist(
        playlist_id="PL-ALPHA",
        name="Alpha Set",
        track_count=1,
        track_ids=("TRK-1",),
    )

    calls = {"build": False, "render": False, "side_effects": False}

    def fake_build_write_plan(_: Config, __: ResolvedPlaylist) -> WritePlan:
        calls["build"] = True
        return _sample_plan()

    def fake_render_dry_run(_: WritePlan) -> None:
        calls["render"] = True

    def fake_run_write_side_effects(
        _: Config, __: cli.PreconditionResult
    ) -> None:
        calls["side_effects"] = True

    original_build = cli.build_write_plan_for_preconditions
    original_render = cli._render_dry_run
    original_side_effects = cli._run_write_side_effects
    cli.build_write_plan_for_preconditions = fake_build_write_plan
    cli._render_dry_run = fake_render_dry_run
    cli._run_write_side_effects = fake_run_write_side_effects
    try:
        statuses, reasons = cli._execute_dry_run(config, playlist)
    finally:
        cli.build_write_plan_for_preconditions = original_build
        cli._render_dry_run = original_render
        cli._run_write_side_effects = original_side_effects

    assert statuses == ["updated", "unchanged"]
    assert reasons == []


def test_execute_dry_run_fails_closed_on_malformed_xml(tmp_path: Path) -> None:
    import music_library_sanitzer.cli as cli

    xml_path = tmp_path / "rekordbox.xml"
    xml_path.write_text("<REKORDBOX>", encoding="utf-8")
    config = Config(
        library_path=xml_path,
        backup_path=Path("/tmp/backups"),
        stage_hot_cues=True,
        stage_energy=False,
        dry_run=True,
    )
    playlist = ResolvedPlaylist(
        playlist_id="PL-BROKEN",
        name="Broken XML",
        track_count=1,
        track_ids=("TRK-1",),
    )

    with pytest.raises(PreconditionFailure):
        cli._execute_dry_run(config, playlist)


def test_statuses_from_plan_includes_failed_reasons() -> None:
    import music_library_sanitzer.cli as cli

    snapshot = ConfigSnapshot(
        library_path="/tmp/library.xml",
        backup_path="/tmp/backups",
        stage_hot_cues=True,
        stage_energy=False,
        dry_run=True,
    )
    plan = WritePlan(
        plan_version=1,
        inputs_hash="hash",
        playlist_id="PL-ALPHA",
        playlist_name="Alpha Set",
        track_count=1,
        config=snapshot,
        tracks=(
            TrackPlan(
                track_index=1,
                track_id="TRK-1",
                planned_action=PlannedAction(
                    action="failed",
                    reason="missing_track_entry",
                ),
                cues=(),
            ),
        ),
    )

    statuses, reasons = cli._statuses_from_plan(plan)

    assert statuses == ["failed"]
    assert reasons == ["Track #1: missing_track_entry"]
