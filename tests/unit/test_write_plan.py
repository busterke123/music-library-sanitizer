from pathlib import Path

from music_library_sanitzer.cli import _plan_then_process
from music_library_sanitzer.config.model import Config
from music_library_sanitzer.pipeline.planner import build_write_plan
from music_library_sanitzer.rekordbox.playlist import ResolvedPlaylist
from music_library_sanitzer.state.runs import persist_write_plan


def test_write_plan_deterministic_serialization() -> None:
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
        track_count=2,
        track_ids=("TRK-1", "TRK-2"),
    )

    first = build_write_plan(config, playlist).to_json()
    second = build_write_plan(config, playlist).to_json()

    assert first == second


def test_plan_includes_planned_actions_and_cues() -> None:
    config = Config(
        library_path=Path("/tmp/library.xml"),
        backup_path=Path("/tmp/backups"),
        stage_hot_cues=True,
        stage_energy=False,
        dry_run=False,
    )
    playlist = ResolvedPlaylist(
        playlist_id="PL-MISSING-IDS",
        name=None,
        track_count=2,
        track_ids=("TRK-1", None),
    )

    plan = build_write_plan(config, playlist)
    assert plan.tracks[0].planned_action.action == "noop"
    assert plan.tracks[0].cues == ()
    assert plan.tracks[1].planned_action.action == "skip"


def test_persist_write_plan_writes_json(tmp_path: Path) -> None:
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
        track_count=2,
        track_ids=("TRK-1", "TRK-2"),
    )

    plan = build_write_plan(config, playlist)
    plan_path = persist_write_plan(plan, base_dir=tmp_path)

    assert plan_path.read_text(encoding="utf-8") == plan.to_json()


def test_planner_runs_before_processing() -> None:
    config = Config(
        library_path=Path("/tmp/library.xml"),
        backup_path=Path("/tmp/backups"),
        stage_hot_cues=True,
        stage_energy=False,
        dry_run=False,
    )
    playlist = ResolvedPlaylist(
        playlist_id="PL-ORDER",
        name="Order Check",
        track_count=1,
        track_ids=("TRK-1",),
    )

    planned = {"value": False}

    def fake_build_write_plan(_: Config, __: ResolvedPlaylist) -> None:
        planned["value"] = True

    def fake_compute_track_statuses(
        _: ResolvedPlaylist,
    ) -> tuple[list[str], list[str]]:
        assert planned["value"] is True
        return (["unchanged"], [])

    import music_library_sanitzer.cli as cli

    original_build = cli._build_write_plan
    original_compute = cli._compute_track_statuses
    cli._build_write_plan = fake_build_write_plan
    cli._compute_track_statuses = fake_compute_track_statuses
    try:
        _plan_then_process(config, playlist)
    finally:
        cli._build_write_plan = original_build
        cli._compute_track_statuses = original_compute
