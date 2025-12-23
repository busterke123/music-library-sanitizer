from pathlib import Path

import pytest
import typer

from music_library_sanitzer.config.model import Config
from music_library_sanitzer.errors import PreconditionFailure
from music_library_sanitzer.exit_codes import ExitCode


def _dummy_context(config: Config):
    class Dummy:
        obj = {"config": config}

    return Dummy()


def test_precondition_failure_maps_to_exit_code_failure(monkeypatch) -> None:
    import music_library_sanitzer.cli as cli

    config = Config(
        library_path=Path("/tmp/library.xml"),
        backup_path=Path("/tmp/backups"),
        stage_hot_cues=True,
        stage_energy=False,
        dry_run=False,
    )

    def fake_run_write_preconditions(_: Config, __: str):
        raise PreconditionFailure("Precondition failed")

    monkeypatch.setattr(cli, "run_write_preconditions", fake_run_write_preconditions)

    with pytest.raises(typer.Exit) as excinfo:
        cli.run(_dummy_context(config), playlist_id="PL-ALPHA")

    assert excinfo.value.exit_code == ExitCode.FAILURE


def test_precondition_failure_skips_write_side_effects(monkeypatch) -> None:
    import music_library_sanitzer.cli as cli

    config = Config(
        library_path=Path("/tmp/library.xml"),
        backup_path=Path("/tmp/backups"),
        stage_hot_cues=True,
        stage_energy=False,
        dry_run=False,
    )
    called = {"side_effects": False}

    def fake_run_write_preconditions(_: Config, __: str):
        raise PreconditionFailure("Precondition failed")

    def fake_run_write_side_effects(
        _: Config, __: cli.PreconditionResult
    ) -> None:
        called["side_effects"] = True

    monkeypatch.setattr(cli, "run_write_preconditions", fake_run_write_preconditions)
    monkeypatch.setattr(cli, "_run_write_side_effects", fake_run_write_side_effects)

    with pytest.raises(typer.Exit):
        cli.run(_dummy_context(config), playlist_id="PL-ALPHA")

    assert called["side_effects"] is False
