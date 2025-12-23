import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import typer

from music_library_sanitzer.config.model import Config
from music_library_sanitzer.errors import PreconditionFailure
from music_library_sanitzer.exit_codes import ExitCode
from music_library_sanitzer.pipeline.executor import PreconditionResult
from music_library_sanitzer.pipeline.models import (
    ConfigSnapshot,
    PlannedAction,
    TrackPlan,
    WritePlan,
)
from music_library_sanitzer.rekordbox.playlist import ResolvedPlaylist


def _dummy_context(config: Config):
    class Dummy:
        obj = {"config": config}

    return Dummy()


def _sample_plan() -> WritePlan:
    snapshot = ConfigSnapshot(
        library_path="/tmp/library.xml",
        backup_path="/tmp/backups",
        stage_hot_cues=True,
        stage_energy=False,
        dry_run=False,
    )
    return WritePlan(
        plan_version=1,
        inputs_hash="hash",
        playlist_id="PL-ALPHA",
        playlist_name="Alpha Set",
        track_count=1,
        config=snapshot,
        tracks=(
            TrackPlan(
                track_index=1,
                track_id=None,
                planned_action=PlannedAction(action="update", reason="add_cue"),
                cues=(),
            ),
        ),
    )


def test_create_backup_copies_library_file(tmp_path, monkeypatch) -> None:
    from music_library_sanitzer.rekordbox import backup

    library_path = tmp_path / "rekordbox.xml"
    library_path.write_text("library", encoding="utf-8")
    backup_root = tmp_path / "backups"

    monkeypatch.setattr(backup, "_current_timestamp", lambda: "20250101-010203")

    backup_file = backup.create_backup(library_path, backup_root)

    assert backup_file == backup_root / "20250101-010203" / "rekordbox.xml"
    assert backup_file.exists()
    assert backup_file.read_text(encoding="utf-8") == "library"


def test_create_backup_appends_suffix_on_collision(tmp_path, monkeypatch) -> None:
    from music_library_sanitzer.rekordbox import backup

    library_path = tmp_path / "rekordbox.xml"
    library_path.write_text("library", encoding="utf-8")
    backup_root = tmp_path / "backups"

    monkeypatch.setattr(backup, "_current_timestamp", lambda: "20250101-010203")

    first = backup.create_backup(library_path, backup_root)
    second = backup.create_backup(library_path, backup_root)

    assert first.parent.name == "20250101-010203"
    assert second.parent.name == "20250101-010203-1"


def test_list_backup_directories_orders_newest_first_with_suffix(tmp_path) -> None:
    from music_library_sanitzer.rekordbox import backup

    backup_root = tmp_path / "backups"
    backup_root.mkdir()

    (backup_root / "20241231-235959").mkdir()
    (backup_root / "20250101-010203").mkdir()
    (backup_root / "20250101-010203-1").mkdir()

    names = [path.name for path in backup.list_backup_directories(backup_root)]

    assert names[0] == "20250101-010203-1"
    assert names[1] == "20250101-010203"
    assert names[-1] == "20241231-235959"


def test_list_backup_directories_orders_zero_padded_suffix_after_base(
    tmp_path,
) -> None:
    from music_library_sanitzer.rekordbox import backup

    backup_root = tmp_path / "backups"
    backup_root.mkdir()

    (backup_root / "20250101-010203").mkdir()
    (backup_root / "20250101-010203-00").mkdir()

    names = [path.name for path in backup.list_backup_directories(backup_root)]

    assert names[0] == "20250101-010203-00"
    assert names[1] == "20250101-010203"


def test_list_backup_directories_falls_back_to_mtime_for_unparseable(
    tmp_path,
) -> None:
    from music_library_sanitzer.rekordbox import backup

    backup_root = tmp_path / "backups"
    backup_root.mkdir()

    parseable = backup_root / "20250101-010203"
    unparseable = backup_root / "backup-foo"
    parseable.mkdir()
    unparseable.mkdir()

    base_time = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
    os.utime(parseable, (base_time.timestamp(), base_time.timestamp()))
    os.utime(
        unparseable,
        (
            (base_time + timedelta(seconds=10)).timestamp(),
            (base_time + timedelta(seconds=10)).timestamp(),
        ),
    )

    names = [path.name for path in backup.list_backup_directories(backup_root)]

    assert names[0] == "backup-foo"
    assert names[1] == "20250101-010203"


def test_prune_backup_retention_keeps_newest_50(tmp_path) -> None:
    from music_library_sanitzer.rekordbox import backup

    backup_root = tmp_path / "backups"
    backup_root.mkdir()
    base = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    names = []
    for index in range(55):
        name = (base + timedelta(seconds=index)).strftime("%Y%m%d-%H%M%S")
        (backup_root / name).mkdir()
        names.append(name)

    removed = backup.prune_backup_retention(backup_root, keep=50)

    assert removed == names[:5]
    remaining = {path.name for path in backup_root.iterdir() if path.is_dir()}
    assert len(remaining) == 50
    assert remaining == set(names[5:])


def test_prune_backup_retention_noop_when_under_limit(tmp_path) -> None:
    from music_library_sanitzer.rekordbox import backup

    backup_root = tmp_path / "backups"
    backup_root.mkdir()
    (backup_root / "20250101-010203").mkdir()
    (backup_root / "20250101-010204").mkdir()

    removed = backup.prune_backup_retention(backup_root, keep=50)

    assert removed == []
    assert len(list(backup_root.iterdir())) == 2


def test_prune_backup_retention_failure_raises_precondition_failure(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from music_library_sanitzer.rekordbox import backup

    backup_root = tmp_path / "backups"
    backup_root.mkdir()
    (backup_root / "20250101-010203").mkdir()
    (backup_root / "20250101-010204").mkdir()

    def boom(_: Path) -> None:
        raise OSError("nope")

    monkeypatch.setattr(backup, "rmtree", boom)

    with pytest.raises(PreconditionFailure) as excinfo:
        backup.prune_backup_retention(backup_root, keep=1)

    assert excinfo.value.stage == "backup_retention"


def test_create_backup_missing_library_file_raises_precondition_failure(
    tmp_path: Path,
) -> None:
    from music_library_sanitzer.rekordbox.backup import create_backup

    backup_root = tmp_path / "backups"

    with pytest.raises(PreconditionFailure) as excinfo:
        create_backup(tmp_path / "missing.xml", backup_root)

    assert excinfo.value.stage == "create_backup"


def test_backup_failure_exits_failure_and_skips_write_effects(monkeypatch) -> None:
    import music_library_sanitzer.cli as cli

    config = Config(
        library_path=Path("/tmp/library.xml"),
        backup_path=Path("/tmp/backups"),
        stage_hot_cues=True,
        stage_energy=False,
        dry_run=False,
    )
    resolved = ResolvedPlaylist(
        playlist_id="PL-ALPHA",
        name="Alpha Set",
        track_count=0,
        track_ids=(),
    )
    preconditions = PreconditionResult(resolved=resolved, plan=_sample_plan())
    called = {"apply": False}

    def fake_run_write_preconditions(_: Config, __: str):
        return preconditions

    def fake_create_backup(_: Path, __: Path) -> Path:
        raise PreconditionFailure("Backup failed", stage="create_backup")

    def fake_apply_write_side_effects(
        _: Config, __: PreconditionResult
    ) -> None:
        called["apply"] = True

    monkeypatch.setattr(cli, "run_write_preconditions", fake_run_write_preconditions)
    monkeypatch.setattr(cli, "create_backup", fake_create_backup)
    monkeypatch.setattr(cli, "_apply_write_side_effects", fake_apply_write_side_effects)

    with pytest.raises(typer.Exit) as excinfo:
        cli.run(_dummy_context(config), playlist_id="PL-ALPHA")

    assert excinfo.value.exit_code == ExitCode.FAILURE
    assert called["apply"] is False


def test_backup_skipped_when_no_planned_changes(monkeypatch) -> None:
    import music_library_sanitzer.cli as cli

    config = Config(
        library_path=Path("/tmp/library.xml"),
        backup_path=Path("/tmp/backups"),
        stage_hot_cues=True,
        stage_energy=False,
        dry_run=False,
    )
    resolved = ResolvedPlaylist(
        playlist_id="PL-ALPHA",
        name="Alpha Set",
        track_count=1,
        track_ids=(None,),
    )
    snapshot = ConfigSnapshot(
        library_path="/tmp/library.xml",
        backup_path="/tmp/backups",
        stage_hot_cues=True,
        stage_energy=False,
        dry_run=False,
    )
    no_change_plan = WritePlan(
        plan_version=1,
        inputs_hash="hash",
        playlist_id="PL-ALPHA",
        playlist_name="Alpha Set",
        track_count=1,
        config=snapshot,
        tracks=(
            TrackPlan(
                track_index=1,
                track_id=None,
                planned_action=PlannedAction(action="skip", reason="empty"),
                cues=(),
            ),
        ),
    )
    preconditions = PreconditionResult(resolved=resolved, plan=no_change_plan)
    called = {"backup": False}

    def fake_run_write_preconditions(_: Config, __: str):
        return preconditions

    def fake_create_backup(_: Path, __: Path) -> Path:
        called["backup"] = True
        return Path("/tmp/backups/placeholder.xml")

    monkeypatch.setattr(cli, "run_write_preconditions", fake_run_write_preconditions)
    monkeypatch.setattr(cli, "create_backup", fake_create_backup)

    with pytest.raises(typer.Exit):
        cli.run(_dummy_context(config), playlist_id="PL-ALPHA")

    assert called["backup"] is False


def test_run_write_side_effects_logs_pruned_backups(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    import music_library_sanitzer.cli as cli

    config = Config(
        library_path=tmp_path / "rekordbox.xml",
        backup_path=tmp_path / "backups",
        stage_hot_cues=True,
        stage_energy=False,
        dry_run=False,
    )
    resolved = ResolvedPlaylist(
        playlist_id="PL-ALPHA",
        name="Alpha Set",
        track_count=1,
        track_ids=("TR-1",),
    )
    preconditions = PreconditionResult(resolved=resolved, plan=_sample_plan())
    order: list[str] = []

    def fake_create_backup(_: Path, __: Path) -> Path:
        order.append("backup")
        return tmp_path / "backups" / "20250101-010203" / "rekordbox.xml"

    def fake_prune_backup_retention(_: Path) -> list[str]:
        assert order == ["backup"]
        order.append("prune")
        return ["20240101-000000", "20240102-000000"]

    monkeypatch.setattr(cli, "create_backup", fake_create_backup)
    monkeypatch.setattr(cli, "prune_backup_retention", fake_prune_backup_retention)
    monkeypatch.setattr(cli, "_apply_write_side_effects", lambda *_: None)

    cli._run_write_side_effects(config, preconditions)

    output = capsys.readouterr().out
    assert "Pruned backups: 20240101-000000, 20240102-000000" in output
