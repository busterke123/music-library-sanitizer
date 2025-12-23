from __future__ import annotations

from enum import IntEnum

from .run_summary import RunCounts


class ExitCode(IntEnum):
    """Process exit codes for scripting stability (CLI and future JSON output)."""

    SUCCESS = 0
    PARTIAL_SUCCESS = 1
    FAILURE = 2


def exit_code_for_counts(counts: RunCounts) -> ExitCode:
    if counts.failed > 0 or counts.skipped > 0:
        return ExitCode.PARTIAL_SUCCESS
    return ExitCode.SUCCESS
