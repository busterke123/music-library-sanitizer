from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .paths import resolve_state_dirs


@dataclass(frozen=True)
class ProvenanceCue:
    slot: int
    start_ms: int | None
    label: str | None
    color: str | None
    source: str | None


@dataclass(frozen=True)
class CueProvenanceIndex:
    tracks: dict[str, tuple[ProvenanceCue, ...]]
    generation_id: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "generation_id": self.generation_id,
            "tracks": {
                track_id: [asdict(cue) for cue in cues]
                for track_id, cues in self.tracks.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "CueProvenanceIndex":
        if "tracks" in data:
            tracks_data = data.get("tracks", {})
            generation_id = data.get("generation_id")
        else:
            tracks_data = data
            generation_id = None
        tracks: dict[str, tuple[ProvenanceCue, ...]] = {}
        for track_id, cues in tracks_data.items():
            parsed: list[ProvenanceCue] = []
            for cue in cues:
                if not isinstance(cue, dict):
                    continue
                parsed.append(
                    ProvenanceCue(
                        slot=cue["slot"],
                        start_ms=cue.get("start_ms"),
                        label=cue.get("label"),
                        color=cue.get("color"),
                        source=cue.get("source"),
                    )
                )
            tracks[track_id] = tuple(parsed)
        return cls(tracks=tracks, generation_id=generation_id)


def merge_provenance_indexes(
    existing: CueProvenanceIndex,
    updates: CueProvenanceIndex,
) -> CueProvenanceIndex:
    merged = dict(existing.tracks)
    merged.update(updates.tracks)
    generation_id = updates.generation_id or existing.generation_id
    return CueProvenanceIndex(tracks=merged, generation_id=generation_id)


def _provenance_path(state_dir: Path) -> Path:
    return state_dir / "provenance" / "cue_provenance.json"


def load_provenance_index(*, base_dir: Path | None = None) -> CueProvenanceIndex:
    for state_dir in resolve_state_dirs(base_dir):
        provenance_path = _provenance_path(state_dir)
        if not provenance_path.exists():
            continue
        data = json.loads(provenance_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Cue provenance index must be a JSON object.")
        return CueProvenanceIndex.from_dict(data)
    return CueProvenanceIndex(tracks={})


def persist_provenance_index(
    index: CueProvenanceIndex,
    *,
    base_dir: Path | None = None,
) -> Path:
    last_error: OSError | None = None
    payload = json.dumps(index.to_dict(), sort_keys=True, separators=(",", ":"))
    for state_dir in resolve_state_dirs(base_dir):
        try:
            provenance_path = _provenance_path(state_dir)
            provenance_path.parent.mkdir(parents=True, exist_ok=True)
            provenance_path.write_text(payload, encoding="utf-8")
            return provenance_path
        except OSError as exc:
            last_error = exc
            continue
    if last_error is not None:
        raise last_error
    raise OSError("No writable state directory found for provenance persistence.")
