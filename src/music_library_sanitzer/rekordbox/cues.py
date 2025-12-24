from __future__ import annotations

from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

from ..errors import CueReadError
from ..pipeline.models import ExistingCue


_TRACK_ID_KEYS = ("Key", "TrackID", "ID", "Id")
_CUE_SLOT_KEYS = ("Num", "Slot", "Index")
_CUE_START_KEYS = ("Start", "StartMs", "StartPosition")
_CUE_LABEL_KEYS = ("Name", "Label")
_CUE_COLOR_KEYS = ("Color", "Colour")
_CUE_SOURCE_KEYS = ("Source", "Type")


def _first_attr(elem: ET.Element, keys: Iterable[str]) -> str | None:
    for key in keys:
        value = elem.attrib.get(key)
        if value:
            return value
    return None


def _parse_optional_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise CueReadError("malformed_cue_data") from exc


def _parse_hotcue_elem(cue_elem: ET.Element) -> ExistingCue:
    slot_raw = _first_attr(cue_elem, _CUE_SLOT_KEYS)
    if slot_raw is None:
        raise CueReadError("malformed_cue_data")
    try:
        slot = int(slot_raw)
    except ValueError as exc:
        raise CueReadError("malformed_cue_data") from exc
    start_ms = _parse_optional_int(_first_attr(cue_elem, _CUE_START_KEYS))
    label = _first_attr(cue_elem, _CUE_LABEL_KEYS)
    color = _first_attr(cue_elem, _CUE_COLOR_KEYS)
    source = _first_attr(cue_elem, _CUE_SOURCE_KEYS)
    return ExistingCue(
        slot=slot,
        start_ms=start_ms,
        label=label,
        color=color,
        source=source,
    )


def read_existing_hot_cues(
    library_path: Path,
    track_ids: Iterable[str | None],
) -> tuple[dict[str, tuple[ExistingCue, ...]], dict[str, str]]:
    if not library_path.exists():
        raise CueReadError(f"Rekordbox library not found: {library_path}")

    requested = {track_id for track_id in track_ids if track_id}
    if not requested:
        return {}, {}

    cues_by_track: dict[str, tuple[ExistingCue, ...]] = {}
    failures: dict[str, str] = {}
    found: set[str] = set()

    current_track_id: str | None = None
    current_cues: list[ExistingCue] | None = None
    current_failed = False

    try:
        for event, elem in ET.iterparse(library_path, events=("start", "end")):
            if event == "start" and elem.tag == "TRACK":
                track_id = _first_attr(elem, _TRACK_ID_KEYS)
                if track_id and track_id in requested:
                    current_track_id = track_id
                    current_cues = []
                    current_failed = False
                else:
                    current_track_id = None
                    current_cues = None
                    current_failed = False
                continue

            if event == "end" and elem.tag == "HOTCUE":
                if current_track_id and current_cues is not None and not current_failed:
                    try:
                        current_cues.append(_parse_hotcue_elem(elem))
                    except CueReadError as exc:
                        failures[current_track_id] = str(exc)
                        current_failed = True
                elem.clear()
                continue

            if event == "end" and elem.tag == "TRACK":
                if current_track_id:
                    found.add(current_track_id)
                    if not current_failed and current_cues is not None:
                        cues_by_track[current_track_id] = tuple(current_cues)
                elem.clear()
                current_track_id = None
                current_cues = None
                current_failed = False
                continue

            if event == "end":
                elem.clear()
    except ET.ParseError as exc:
        raise CueReadError(
            f"Invalid Rekordbox XML at {library_path}: {exc}"
        ) from exc

    for track_id in requested - found:
        failures[track_id] = "missing_track_entry"

    return cues_by_track, failures
