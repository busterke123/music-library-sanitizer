from pathlib import Path

import typer
from rich.progress import track

from .config.load import ConfigError, ConfigOverrides, load_config
from .config.model import DEFAULT_CONFIG_PATH
from .errors import PlaylistResolutionError
from .rekordbox.playlist import resolve_playlist
from .run_summary import RunCounts, RunStatus, summarize_counts


app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Scriptable CLI for enriching a Rekordbox library.",
)


@app.callback()
def _main(
    ctx: typer.Context,
    config: Path | None = typer.Option(
        None,
        "--config",
        help=f"Path to config file (default: {DEFAULT_CONFIG_PATH}).",
    ),
    library_path: Path | None = typer.Option(
        None,
        "--library-path",
        help="Override Rekordbox library path.",
    ),
    backup_path: Path | None = typer.Option(
        None,
        "--backup-path",
        help="Override backup directory path.",
    ),
    stage_hot_cues: bool | None = typer.Option(
        None,
        "--stage-hot-cues/--no-stage-hot-cues",
        help="Enable or disable the hot cues stage.",
    ),
    stage_energy: bool | None = typer.Option(
        None,
        "--stage-energy/--no-stage-energy",
        help="Enable or disable the energy stage placeholder.",
    ),
    dry_run: bool | None = typer.Option(
        None,
        "--dry-run/--no-dry-run",
        help="Override dry-run default.",
    ),
) -> None:
    """Scriptable CLI for enriching a Rekordbox library."""
    if ctx.resilient_parsing:
        return
    overrides = ConfigOverrides(
        library_path=library_path,
        backup_path=backup_path,
        stage_hot_cues=stage_hot_cues,
        stage_energy=stage_energy,
        dry_run=dry_run,
    )
    explicit = config is not None
    try:
        resolved = load_config(config, overrides, explicit=explicit)
    except ConfigError as exc:
        typer.echo(f"Config error: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    ctx.obj = {"config": resolved}


@app.command()
def run(
    ctx: typer.Context,
    playlist_id: str = typer.Option(
        ...,
        "--playlist-id",
        help="Stable Rekordbox playlist identifier to resolve.",
    ),
) -> None:
    """Placeholder command (foundation-only story)."""
    config = ctx.obj["config"]
    try:
        resolved = resolve_playlist(config.library_path, playlist_id)
    except PlaylistResolutionError as exc:
        typer.echo(f"Playlist resolution error: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    typer.echo("Playlist Preflight")
    typer.echo("==================")
    typer.echo(f"Playlist ID: {resolved.playlist_id}")
    if resolved.name:
        typer.echo(f"Playlist Name: {resolved.name}")
    else:
        typer.echo("Playlist Name: (unavailable)")
    typer.echo(f"Track Count: {resolved.track_count}")

    track_ids = resolved.track_ids
    statuses: list[RunStatus] = []
    failure_reasons: list[str] = []
    if track_ids is not None:
        iterator = enumerate(track_ids, start=1)
    else:
        iterator = enumerate(range(resolved.track_count), start=1)

    for index, track_id in track(
        iterator, description="Processing tracks", disable=resolved.track_count == 0
    ):
        try:
            statuses.append("unchanged")
        except Exception as exc:  # pragma: no cover - defensive for future analysis
            statuses.append("failed")
            if track_ids is not None:
                failure_reasons.append(f"Track {track_id}: {exc}")
            else:
                failure_reasons.append(f"Track #{index}: {exc}")

    if failure_reasons:
        for reason in failure_reasons:
            typer.echo(f"Track error: {reason}", err=True)

    counts: RunCounts = summarize_counts(statuses)
    typer.echo("")
    typer.echo("Run Summary")
    typer.echo("===========")
    typer.echo(f"Processed: {counts.processed}")
    typer.echo(f"Updated: {counts.updated}")
    typer.echo(f"Unchanged: {counts.unchanged}")
    typer.echo(f"Skipped: {counts.skipped}")
    typer.echo(f"Failed: {counts.failed}")

    raise typer.Exit(code=0)
