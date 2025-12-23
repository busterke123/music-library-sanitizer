from dataclasses import dataclass
from pathlib import Path

DEFAULT_CONFIG_PATH = Path("~/.music-library-sanitzer/config.toml")
DEFAULT_LIBRARY_PATH = Path("~/Music/Rekordbox/rekordbox.xml")
DEFAULT_BACKUP_PATH = Path("~/.music-library-sanitzer/backups")


@dataclass(frozen=True)
class Config:
    library_path: Path
    backup_path: Path
    stage_hot_cues: bool
    stage_energy: bool
    dry_run: bool
