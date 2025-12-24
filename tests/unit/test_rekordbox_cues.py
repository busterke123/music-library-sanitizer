from pathlib import Path
from textwrap import dedent

from music_library_sanitzer.rekordbox.cues import read_existing_hot_cues
from music_library_sanitzer.rekordbox.playlist import ResolvedPlaylist
from music_library_sanitzer.pipeline.planner import build_write_plan
from music_library_sanitzer.config.model import Config


def _write_xml(path: Path, content: str) -> Path:
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")
    return path


def test_read_existing_hot_cues_parses_hotcues() -> None:
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    xml_path = fixtures / "rekordbox-hot-cues.xml"

    cues_by_track, failures = read_existing_hot_cues(xml_path, ["TRK-1", "TRK-2"])

    assert failures == {}
    assert cues_by_track["TRK-1"][0].slot == 1
    assert cues_by_track["TRK-1"][0].start_ms == 1000
    assert cues_by_track["TRK-1"][0].label == "Intro"
    assert cues_by_track["TRK-1"][0].color == "red"
    assert cues_by_track["TRK-2"][0].slot == 1


def test_read_existing_hot_cues_missing_track_entry(tmp_path: Path) -> None:
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

    cues_by_track, failures = read_existing_hot_cues(xml_path, ["TRK-1", "TRK-2"])

    assert cues_by_track["TRK-1"] == ()
    assert failures["TRK-2"] == "missing_track_entry"


def test_read_existing_hot_cues_malformed_data(tmp_path: Path) -> None:
    xml_path = _write_xml(
        tmp_path / "rekordbox.xml",
        """
        <?xml version="1.0" encoding="UTF-8"?>
        <REKORDBOX>
          <COLLECTION>
            <TRACK TrackID="TRK-1">
              <HOTCUE Start="1000" Name="Intro" />
            </TRACK>
          </COLLECTION>
        </REKORDBOX>
        """,
    )

    cues_by_track, failures = read_existing_hot_cues(xml_path, ["TRK-1"])

    assert "TRK-1" not in cues_by_track
    assert failures["TRK-1"] == "malformed_cue_data"


def test_build_write_plan_includes_existing_cues() -> None:
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    xml_path = fixtures / "rekordbox-hot-cues.xml"
    config = Config(
        library_path=xml_path,
        backup_path=Path("/tmp/backups"),
        stage_hot_cues=True,
        stage_energy=False,
        dry_run=True,
    )
    playlist = ResolvedPlaylist(
        playlist_id="PL-EXISTING",
        name="Existing Cues",
        track_count=2,
        track_ids=("TRK-1", "TRK-2"),
    )

    plan = build_write_plan(config, playlist)

    assert plan.tracks[0].existing_cues[0].slot == 1
    assert plan.tracks[0].existing_cues[0].label == "Intro"
    assert plan.tracks[1].existing_cues[0].start_ms == 1500


def test_build_write_plan_marks_failed_on_missing_track_id(tmp_path: Path) -> None:
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
        dry_run=True,
    )
    playlist = ResolvedPlaylist(
        playlist_id="PL-MISSING",
        name=None,
        track_count=1,
        track_ids=(None,),
    )

    plan = build_write_plan(config, playlist)

    assert plan.tracks[0].planned_action.action == "failed"
    assert plan.tracks[0].planned_action.reason == "missing_track_id"
