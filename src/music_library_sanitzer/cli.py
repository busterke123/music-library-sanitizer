from pathlib import Path

import typer

from .config.load import ConfigError, ConfigOverrides, load_config
from .config.model import DEFAULT_CONFIG_PATH


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
def run(ctx: typer.Context) -> None:
    """Placeholder command (foundation-only story)."""
    raise typer.Exit(code=0)
