from pathlib import Path

import typer
from rich.progress import track

from .config.load import ConfigError, ConfigOverrides, load_config
from .config.model import Config, DEFAULT_CONFIG_PATH
from .errors import PlaylistResolutionError
from .exit_codes import ExitCode, exit_code_for_counts
from .pipeline.models import CuePlan, TrackPlan, WritePlan
from .pipeline.planner import (
    build_write_plan,
    current_generation_id,
    extract_provenance_from_plan,
)
from .rekordbox.playlist import resolve_playlist
from .rekordbox.playlist import ResolvedPlaylist
from .run_summary import RunCounts, RunStatus, summarize_counts
from .state.provenance import (
    load_provenance_index,
    merge_provenance_indexes,
    persist_provenance_index,
)
from .state.runs import persist_write_plan


app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Scriptable CLI for enriching a Rekordbox library. Exit codes: 0 success, 1 partial success, 2 failure (fail-closed preconditions).",
)


def _build_write_plan(config: Config, resolved: ResolvedPlaylist) -> WritePlan:
    try:
        plan = build_write_plan(config, resolved)
        persist_write_plan(plan)
        generation_id = current_generation_id(config)
        updates = extract_provenance_from_plan(
            plan,
            generation_id=generation_id,
        )
        existing = load_provenance_index()
        merged = merge_provenance_indexes(existing, updates)
        if merged.generation_id != existing.generation_id or updates.tracks:
            persist_provenance_index(merged)
        return plan
    except Exception as exc:  # pragma: no cover - defensive for persistence errors
        typer.echo(f"Write plan error: {exc}", err=True)
        raise typer.Exit(code=ExitCode.FAILURE) from exc


def _compute_track_statuses(
    resolved: ResolvedPlaylist,
) -> tuple[list[RunStatus], list[str]]:
    statuses: list[RunStatus] = []
    failure_reasons: list[str] = []

    for index, track_id in track(
        enumerate(resolved.track_ids, start=1),
        description="Processing tracks",
        disable=resolved.track_count == 0,
    ):
        try:
            if track_id is not None:
                statuses.append("unchanged")
            else:
                statuses.append("skipped")
                failure_reasons.append(f"Track #{index}: missing track id")
        except Exception as exc:  # pragma: no cover - defensive for future analysis
            statuses.append("failed")
            failure_reasons.append(f"Track #{index}: {exc}")

    return statuses, failure_reasons


def _plan_then_process(
    config: Config,
    resolved: ResolvedPlaylist,
) -> tuple[list[RunStatus], list[str]]:
    _build_write_plan(config, resolved)
    return _compute_track_statuses(resolved)


def _format_cue_plan(cue: CuePlan) -> str:
    details = [f"slot={cue.slot}"]
    if cue.start_ms is not None:
        details.append(f"start_ms={cue.start_ms}")
    if cue.label is not None:
        details.append(f"label={cue.label}")
    if cue.color is not None:
        details.append(f"color={cue.color}")
    if cue.source is not None:
        details.append(f"source={cue.source}")
    return ", ".join(details)


def _is_planned_change(action: str) -> bool:
    return action not in {"noop", "skip"}


def _format_track_plan(track: TrackPlan) -> list[str]:
    track_label = f"Track #{track.track_index}"
    if track.track_id:
        track_label = f"{track_label} ({track.track_id})"
    action = track.planned_action.action
    if track.planned_action.reason:
        action = f"{action} ({track.planned_action.reason})"
    if not track.cues:
        return [f"{track_label}: {action}; cues: none"]

    lines = [f"{track_label}: {action}; cues:"]
    lines.extend(f"- {_format_cue_plan(cue)}" for cue in track.cues)
    return lines


def _format_planned_changes(plan: WritePlan) -> list[str]:
    lines = [
        "Dry Run Planned Changes",
        "=======================",
        f"Playlist ID: {plan.playlist_id}",
        f"Track Count: {plan.track_count}",
    ]
    if plan.playlist_name:
        lines.insert(3, f"Playlist Name: {plan.playlist_name}")
    else:
        lines.insert(3, "Playlist Name: (unavailable)")
    lines.append("")
    planned_changes = [
        track
        for track in plan.tracks
        if _is_planned_change(track.planned_action.action)
    ]
    if not planned_changes:
        lines.append("No planned changes.")
        return lines
    for track in planned_changes:
        lines.extend(_format_track_plan(track))
    return lines


def _render_dry_run(plan: WritePlan) -> None:
    for line in _format_planned_changes(plan):
        typer.echo(line)


def _statuses_from_plan(plan: WritePlan) -> tuple[list[RunStatus], list[str]]:
    statuses: list[RunStatus] = []
    failure_reasons: list[str] = []
    for track in plan.tracks:
        action = track.planned_action.action
        if action == "skip":
            statuses.append("skipped")
            if track.planned_action.reason:
                failure_reasons.append(
                    f"Track #{track.track_index}: {track.planned_action.reason}"
                )
            else:
                failure_reasons.append(f"Track #{track.track_index}: skipped")
        elif action == "noop":
            statuses.append("unchanged")
        else:
            statuses.append("updated")
    return statuses, failure_reasons


def _execute_run(
    config: Config,
    resolved: ResolvedPlaylist,
) -> tuple[list[RunStatus], list[str]]:
    if config.dry_run:
        plan = _build_write_plan(config, resolved)
        _render_dry_run(plan)
        return _statuses_from_plan(plan)
    return _plan_then_process(config, resolved)


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
        raise typer.Exit(code=ExitCode.FAILURE) from exc

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
        raise typer.Exit(code=ExitCode.FAILURE) from exc
    statuses, failure_reasons = _execute_run(config, resolved)

    typer.echo("Playlist Preflight")
    typer.echo("==================")
    typer.echo(f"Playlist ID: {resolved.playlist_id}")
    if resolved.name:
        typer.echo(f"Playlist Name: {resolved.name}")
    else:
        typer.echo("Playlist Name: (unavailable)")
    typer.echo(f"Track Count: {resolved.track_count}")

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

    exit_code = exit_code_for_counts(counts)
    raise typer.Exit(code=exit_code)
