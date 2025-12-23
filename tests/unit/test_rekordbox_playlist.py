from pathlib import Path
from textwrap import dedent

import pytest

from music_library_sanitzer.errors import PlaylistResolutionError
from music_library_sanitzer.rekordbox.playlist import resolve_playlist


def _write_xml(path: Path, content: str) -> Path:
    path.write_text(dedent(content).strip() + "\n", encoding="utf-8")
    return path


def test_resolve_playlist_success(tmp_path: Path) -> None:
    xml_path = _write_xml(
        tmp_path / "rekordbox.xml",
        """
        <?xml version="1.0" encoding="UTF-8"?>
        <REKORDBOX>
          <PLAYLISTS>
            <NODE Type="1" Id="PL1" Name="Warmup">
              <TRACK Key="1" />
              <TRACK Key="2" />
            </NODE>
            <NODE Type="1" Id="PL2" Name="Closing">
              <TRACK Key="3" />
            </NODE>
          </PLAYLISTS>
        </REKORDBOX>
        """,
    )

    resolved = resolve_playlist(xml_path, "PL1")

    assert resolved.playlist_id == "PL1"
    assert resolved.name == "Warmup"
    assert resolved.track_count == 2
    assert resolved.track_ids == ("1", "2")


def test_resolve_playlist_unknown_id_raises(tmp_path: Path) -> None:
    xml_path = _write_xml(
        tmp_path / "rekordbox.xml",
        """
        <?xml version="1.0" encoding="UTF-8"?>
        <REKORDBOX>
          <PLAYLISTS>
            <NODE Type="1" Id="PL1" Name="Warmup">
              <TRACK Key="1" />
            </NODE>
          </PLAYLISTS>
        </REKORDBOX>
        """,
    )

    with pytest.raises(PlaylistResolutionError):
        resolve_playlist(xml_path, "UNKNOWN")


def test_resolve_playlist_invalid_xml_raises(tmp_path: Path) -> None:
    xml_path = _write_xml(
        tmp_path / "rekordbox.xml",
        """
        <REKORDBOX>
          <PLAYLISTS>
            <NODE Type="1" Id="PL1">
        """,
    )

    with pytest.raises(PlaylistResolutionError):
        resolve_playlist(xml_path, "PL1")


def test_resolve_playlist_missing_track_ids_preserves_entries(tmp_path: Path) -> None:
    xml_path = _write_xml(
        tmp_path / "rekordbox.xml",
        """
        <?xml version="1.0" encoding="UTF-8"?>
        <REKORDBOX>
          <PLAYLISTS>
            <NODE Type="1" Id="PL1" Name="Warmup">
              <TRACK />
              <TRACK Key="2" />
            </NODE>
          </PLAYLISTS>
        </REKORDBOX>
        """,
    )

    resolved = resolve_playlist(xml_path, "PL1")

    assert resolved.track_count == 2
    assert resolved.track_ids == (None, "2")


def test_resolve_playlist_ignores_folder_nodes(tmp_path: Path) -> None:
    xml_path = _write_xml(
        tmp_path / "rekordbox.xml",
        """
        <?xml version="1.0" encoding="UTF-8"?>
        <REKORDBOX>
          <PLAYLISTS>
            <NODE Type="0" Id="PL-FOLDER" Name="Folder">
              <NODE Type="1" Id="PL-ACTUAL" Name="Actual">
                <TRACK Key="1" />
              </NODE>
            </NODE>
          </PLAYLISTS>
        </REKORDBOX>
        """,
    )

    with pytest.raises(PlaylistResolutionError):
        resolve_playlist(xml_path, "PL-FOLDER")
