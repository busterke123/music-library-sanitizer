from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

from ..errors import PlaylistResolutionError


_PLAYLIST_TAGS = {"NODE", "PLAYLIST"}
_TRACK_TAGS = {"TRACK", "ENTRY"}
_PLAYLIST_ID_KEYS = ("Id", "ID", "Uuid", "UUID")
_PLAYLIST_NAME_KEYS = ("Name", "NAME")
_TRACK_ID_KEYS = ("Key", "TrackID", "ID", "Id")


@dataclass(frozen=True)
class ResolvedPlaylist:
    playlist_id: str
    name: str | None
    track_count: int
    track_ids: tuple[str | None, ...]


def _first_attr(elem: ET.Element, keys: Iterable[str]) -> str | None:
    for key in keys:
        value = elem.attrib.get(key)
        if value:
            return value
    return None


def _is_playlist_element(elem: ET.Element) -> bool:
    if elem.tag == "PLAYLIST":
        return True
    if elem.tag == "NODE":
        return elem.attrib.get("Type") == "1"
    return False


def resolve_playlist(library_path: Path, playlist_id: str) -> ResolvedPlaylist:
    if not library_path.exists():
        raise PlaylistResolutionError(
            f"Rekordbox library not found: {library_path} (playlist-id={playlist_id})"
        )

    track_count = 0
    track_ids: list[str | None] = []
    matched = False
    playlist_elem: ET.Element | None = None
    playlist_name: str | None = None

    try:
        for event, elem in ET.iterparse(library_path, events=("start", "end")):
            if event == "start":
                if not matched and _is_playlist_element(elem):
                    elem_id = _first_attr(elem, _PLAYLIST_ID_KEYS)
                    if elem_id == playlist_id:
                        matched = True
                        playlist_elem = elem
                        playlist_name = _first_attr(elem, _PLAYLIST_NAME_KEYS)
                elif matched and elem.tag in _TRACK_TAGS:
                    track_count += 1
                    track_id = _first_attr(elem, _TRACK_ID_KEYS)
                    track_ids.append(track_id)

            if event == "end":
                if matched and playlist_elem is elem:
                    return ResolvedPlaylist(
                        playlist_id=playlist_id,
                        name=playlist_name,
                        track_count=track_count,
                        track_ids=tuple(track_ids),
                    )
                elem.clear()
    except ET.ParseError as exc:
        raise PlaylistResolutionError(
            f"Invalid Rekordbox XML at {library_path} (playlist-id={playlist_id}): {exc}"
        ) from exc

    raise PlaylistResolutionError(
        f"Playlist not found: {playlist_id} in {library_path}"
    )
