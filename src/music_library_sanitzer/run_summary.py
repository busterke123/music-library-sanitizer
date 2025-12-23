from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

RunStatus = Literal["updated", "unchanged", "skipped", "failed"]


@dataclass(frozen=True)
class RunCounts:
    processed: int
    updated: int
    unchanged: int
    skipped: int
    failed: int


def summarize_counts(statuses: Iterable[RunStatus]) -> RunCounts:
    updated = 0
    unchanged = 0
    skipped = 0
    failed = 0

    for status in statuses:
        if status == "updated":
            updated += 1
        elif status == "unchanged":
            unchanged += 1
        elif status == "skipped":
            skipped += 1
        elif status == "failed":
            failed += 1
        else:
            raise ValueError(f"Unknown run status: {status}")

    processed = updated + unchanged + skipped + failed
    return RunCounts(
        processed=processed,
        updated=updated,
        unchanged=unchanged,
        skipped=skipped,
        failed=failed,
    )
