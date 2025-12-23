import pytest

from music_library_sanitzer.run_summary import summarize_counts


def test_summarize_counts_basic() -> None:
    counts = summarize_counts(["unchanged", "updated", "skipped", "failed", "unchanged"])

    assert counts.processed == 5
    assert counts.updated == 1
    assert counts.unchanged == 2
    assert counts.skipped == 1
    assert counts.failed == 1


def test_summarize_counts_unknown_status_raises() -> None:
    with pytest.raises(ValueError, match="Unknown run status"):
        summarize_counts(["unknown"])
