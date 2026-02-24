import typer
from rich.console import Console
from flint.cli import model, prompt, serve, bench, code, git, memory
from flint import __version__

app = typer.Typer(
    name="flint",
    help=" Flint: The missing layer for local AI models.",
    no_args_is_help=True,
    add_completion=False,
)

console = Console()

# Add sub-commands
app.add_typer(prompt.app, name="prompt", help="Manage and run prompt templates.")
app.add_typer(memory.app, name="memory")

# Add top-level commands from modules
app.command(name="pull")(model.pull)
app.command(name="list")(model.list_models)
app.command(name="run")(model.run)
app.command(name="serve")(serve.serve)
app.command(name="bench")(bench.bench)
app.command(name="code")(code.code)
app.command(name="commit")(git.generate_commit)
app.command(name="review")(git.code_review)


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show the application's version and exit.",
    )
):
    """
    Flint CLI
    """
    if version:
        console.print(f"Flint version: [bold green]{__version__}[/bold green]")
        raise typer.Exit()


if __name__ == "__main__":
    app()
