import typer


app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Scriptable CLI for enriching a Rekordbox library.",
)


@app.callback()
def _main() -> None:
    """Scriptable CLI for enriching a Rekordbox library."""


@app.command()
def run() -> None:
    """Placeholder command (foundation-only story)."""
    raise typer.Exit(code=0)
