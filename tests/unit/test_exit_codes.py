from music_library_sanitzer.exit_codes import ExitCode, exit_code_for_counts
from music_library_sanitzer.run_summary import RunCounts


def test_exit_code_values() -> None:
    assert ExitCode.SUCCESS.value == 0
    assert ExitCode.PARTIAL_SUCCESS.value == 1
    assert ExitCode.FAILURE.value == 2


def test_exit_code_for_counts_success() -> None:
    counts = RunCounts(processed=2, updated=0, unchanged=2, skipped=0, failed=0)
    assert exit_code_for_counts(counts) is ExitCode.SUCCESS


def test_exit_code_for_counts_partial_success_skipped() -> None:
    counts = RunCounts(processed=2, updated=0, unchanged=1, skipped=1, failed=0)
    assert exit_code_for_counts(counts) is ExitCode.PARTIAL_SUCCESS


def test_exit_code_for_counts_partial_success_failed() -> None:
    counts = RunCounts(processed=2, updated=0, unchanged=1, skipped=0, failed=1)
    assert exit_code_for_counts(counts) is ExitCode.PARTIAL_SUCCESS
