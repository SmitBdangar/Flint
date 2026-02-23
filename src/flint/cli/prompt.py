import typer
import asyncio
from typing import List
from rich.console import Console
from flint.core.prompt import Prompt
from flint.backends.ollama import OllamaBackend

app = typer.Typer()
console = Console()

@app.command("save")
def save_prompt(name: str, file_path: str):
    """
    Save a prompt template to the registry.
    """
    # Simply load from file and pretend to save it for now
    try:
        p = Prompt.load(file_path)
        p.save(name)
        console.print(f"✅ Saved prompt template [bold green]{name}[/bold green] from {file_path}")
    except FileNotFoundError:
        console.print(f"❌ Could not find file {file_path}")
        raise typer.Exit(1)

@app.command("run")
def run_prompt(
    name: str = typer.Argument(..., help="Name of the prompt or path to file"),
    model: str = typer.Option("llama3", "--model", "-m", help="Model to use"),
    var: List[str] = typer.Option([], "--var", "-v", help="Variables for interpolation (e.g. -v attr=value)")
):
    """
    Execute a saved prompt template.
    """
    kwargs = {}
    for v in var:
        if "=" in v:
            key, val = v.split("=", 1)
            kwargs[key] = val
            
    try:
        p = Prompt.load(name)
        formatted_prompt = p.format(**kwargs)
    except Exception as e:
        console.print(f"❌ Failed to load/format prompt: {e}")
        raise typer.Exit(1)
        
    backend = OllamaBackend()
    
    async def _run():
        console.print(f"🤖 Running [bold cyan]{model}[/bold cyan] with prompt '{name}'...")
        try:
            async for chunk in backend.generate_stream(formatted_prompt, model):
                console.print(chunk, end="")
            console.print()
        except Exception as e:
            console.print(f"\n[red]Error:[/red] {e}")
            
    asyncio.run(_run())
