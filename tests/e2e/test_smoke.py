import importlib.util
import re
import shutil
import subprocess
import sys

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
    )
    assert result.returncode == 0, result.stderr
    output = strip_ansi(result.stdout)
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
    )
    assert result.returncode == 0, result.stderr
    output = strip_ansi(result.stdout)
    assert "run" in output
    assert "--config" in output
