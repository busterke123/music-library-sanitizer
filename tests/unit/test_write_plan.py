from pathlib import Path
from textwrap import dedent

import music_library_sanitzer.cli as cli
from music_library_sanitzer.config.model import Config
from music_library_sanitzer.pipeline.planner import build_write_plan
from music_library_sanitzer.rekordbox.playlist import ResolvedPlaylist
from music_library_sanitzer.state.runs import persist_write_plan


def _write_xml(path: Path, content: str) -> Path:
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")
    return path


def test_write_plan_deterministic_serialization(tmp_path: Path) -> None:
    xml_path = _write_xml(
        tmp_path / "rekordbox.xml",
        """
        <?xml version="1.0" encoding="UTF-8"?>
        <REKORDBOX>
          <COLLECTION></COLLECTION>
        </REKORDBOX>
        """,
    )
    config = Config(
        library_path=xml_path,
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


def test_plan_includes_planned_actions_and_cues(tmp_path: Path) -> None:
    xml_path = _write_xml(
        tmp_path / "rekordbox.xml",
        """
        <?xml version="1.0" encoding="UTF-8"?>
        <REKORDBOX>
          <COLLECTION>
            <TRACK TrackID="TRK-1"></TRACK>
          </COLLECTION>
        </REKORDBOX>
        """,
    )
    config = Config(
        library_path=xml_path,
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
    assert plan.tracks[1].planned_action.action == "failed"
    assert plan.tracks[1].planned_action.reason == "missing_track_id"


def test_persist_write_plan_writes_json(tmp_path: Path) -> None:
    xml_path = _write_xml(
        tmp_path / "rekordbox.xml",
        """
        <?xml version="1.0" encoding="UTF-8"?>
        <REKORDBOX>
          <COLLECTION>
            <TRACK TrackID="TRK-1"></TRACK>
            <TRACK TrackID="TRK-2"></TRACK>
          </COLLECTION>
        </REKORDBOX>
        """,
    )
    config = Config(
        library_path=xml_path,
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


def test_planner_runs_before_processing(tmp_path: Path) -> None:
    xml_path = _write_xml(
        tmp_path / "rekordbox.xml",
        """
        <?xml version="1.0" encoding="UTF-8"?>
        <REKORDBOX>
          <COLLECTION>
            <TRACK TrackID="TRK-1"></TRACK>
          </COLLECTION>
        </REKORDBOX>
        """,
    )
    config = Config(
        library_path=xml_path,
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

    def fake_run_write_preconditions(_: Config, __: str) -> cli.PreconditionResult:
        planned["value"] = True
        plan = build_write_plan(config, playlist)
        return cli.PreconditionResult(resolved=playlist, plan=plan)

    original_run = cli.run_write_preconditions
    original_backup = cli.create_backup
    original_side_effects = cli._run_write_side_effects
    cli.run_write_preconditions = fake_run_write_preconditions
    cli.create_backup = lambda *_: Path("/tmp/backups/placeholder.xml")
    cli._run_write_side_effects = lambda *_: None
    try:
        _, statuses, _ = cli._execute_write_run(config, playlist.playlist_id)
    finally:
        cli.run_write_preconditions = original_run
        cli.create_backup = original_backup
        cli._run_write_side_effects = original_side_effects

    assert planned["value"] is True
    assert statuses == ["unchanged"]
