import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


@pytest.mark.e2e
def test_cli_module_exists() -> None:
    if importlib.util.find_spec("music_library_sanitzer") is None:
        pytest.skip("Package not implemented yet (expected early in the project).")


@pytest.mark.e2e
def test_cli_help_runs() -> None:
    if importlib.util.find_spec("music_library_sanitzer") is None:
        pytest.skip("Package not implemented yet (expected early in the project).")

    result = subprocess.run(
        [sys.executable, "-m", "music_library_sanitzer", "--help"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0, result.stderr
    output = strip_ansi(result.stdout or "")
    assert "run" in output
    assert "--config" in output


@pytest.mark.e2e
def test_console_entrypoint_help_runs() -> None:
    if importlib.util.find_spec("music_library_sanitzer") is None:
        pytest.skip("Package not implemented yet (expected early in the project).")

    entrypoint = shutil.which("music-library-sanitzer")
    if entrypoint is None:
        pytest.skip("Console entrypoint not available in PATH for this environment.")

    result = subprocess.run(
        [entrypoint, "--help"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0, result.stderr
    output = strip_ansi(result.stdout or "")
    assert "run" in output
    assert "--config" in output

@pytest.mark.e2e
def test_run_requires_playlist_id() -> None:
    if importlib.util.find_spec("music_library_sanitzer") is None:
        pytest.skip("Package not implemented yet (expected early in the project).")

    result = subprocess.run(
        [sys.executable, "-m", "music_library_sanitzer", "run"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode != 0
    output = strip_ansi((result.stderr or "") + (result.stdout or ""))
    assert "Missing option '--playlist-id'" in output


@pytest.mark.e2e
def test_run_preflight_output() -> None:
    if importlib.util.find_spec("music_library_sanitzer") is None:
        pytest.skip("Package not implemented yet (expected early in the project).")

    fixture_path = Path(__file__).resolve().parents[1] / "fixtures" / "rekordbox.xml"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "music_library_sanitzer",
            "--library-path",
            str(fixture_path),
            "run",
            "--playlist-id",
            "PL-ALPHA",
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0, result.stderr
    output = strip_ansi((result.stderr or "") + (result.stdout or ""))
    assert "Playlist Preflight" in output
    assert "Playlist ID: PL-ALPHA" in output
    assert "Playlist Name: Alpha Set" in output
    assert "Track Count: 2" in output
    assert "Run Summary" in output
    assert "Processed: 2" in output
    assert "Updated: 0" in output
    assert "Unchanged: 2" in output
    assert "Skipped: 0" in output
    assert "Failed: 0" in output


@pytest.mark.e2e
def test_run_playlist_resolution_error_nonzero_exit() -> None:
    if importlib.util.find_spec("music_library_sanitzer") is None:
        pytest.skip("Package not implemented yet (expected early in the project).")

    fixture_path = Path(__file__).resolve().parents[1] / "fixtures" / "rekordbox.xml"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "music_library_sanitzer",
            "--library-path",
            str(fixture_path),
            "run",
            "--playlist-id",
            "PL-MISSING",
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode != 0
    output = strip_ansi((result.stderr or "") + (result.stdout or ""))
    assert "Playlist resolution error" in output
    assert "PL-MISSING" in output
