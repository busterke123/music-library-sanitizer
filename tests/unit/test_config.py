from pathlib import Path

import pytest

from music_library_sanitzer.config.load import ConfigError, ConfigOverrides, load_config


def test_config_file_overrides_defaults(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
library_path = \"/tmp/rekordbox.xml\"
backup_path = \"/tmp/backups\"
stage_hot_cues = false
dry_run = true
""".strip()
        + "\n",
        encoding="utf-8",
    )

    config = load_config(config_path, ConfigOverrides())

    assert config.library_path.as_posix().endswith("/tmp/rekordbox.xml")
    assert config.backup_path.as_posix().endswith("/tmp/backups")
    assert config.stage_hot_cues is False
    assert config.dry_run is True


def test_cli_overrides_config_file(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
library_path = \"/tmp/from-file.xml\"
backup_path = \"/tmp/backups\"
stage_hot_cues = true
dry_run = false
""".strip()
        + "\n",
        encoding="utf-8",
    )

    overrides = ConfigOverrides(
        library_path=Path("/tmp/from-cli.xml"),
        dry_run=True,
    )
    config = load_config(config_path, overrides)

    assert config.library_path.as_posix().endswith("/tmp/from-cli.xml")
    assert config.dry_run is True


def test_invalid_config_type_raises(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
dry_run = \"yes\"
""".strip()
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError):
        load_config(config_path, ConfigOverrides())
