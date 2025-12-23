import importlib.util
import subprocess
import sys

import pytest


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
