import typer
import asyncio
from rich.console import Console
from rich.table import Table
from flint.backends.ollama import OllamaBackend
from flint.core.model import Model

console = Console()

def pull(model_name: str = typer.Argument(..., help="Name of the model to pull (e.g., llama3)")):
    """
    Pull a model from the default backend (Ollama).
    """
    backend = OllamaBackend()
    console.print(f"📥 Pulling model [bold cyan]{model_name}[/bold cyan] via {backend.name}...")
    # NOTE: In v0.1 this just uses the underlying Ollama CLI or API directly
    # A complete implementation would stream progress.
    # For now, we stub it out.
    import subprocess
    result = subprocess.run(["ollama", "pull", model_name], capture_output=False)
    if result.returncode == 0:
        console.print(f"✅ Successfully pulled [bold green]{model_name}[/bold green].")
    else:
        console.print(f"❌ Failed to pull [bold red]{model_name}[/bold red]. Is Ollama running?")
        raise typer.Exit(1)


def list_models():
    """
    List downloaded local models across backends.
    """
    backend = OllamaBackend()
    
    async def _list():
        models = await backend.list_models()
        
        table = Table(title="Local AI Models (Flint)", show_header=True, header_style="bold magenta")
        table.add_column("Model Name", style="cyan")
        table.add_column("Backend", style="green")
        table.add_column("Size", justify="right")
        table.add_column("Status", style="yellow")
        
        if not models:
            console.print("No models found. Try `flint pull llama3`.")
            return

        for m in models:
            table.add_row(m.name, m.backend_name, m.size, m.status)
            
        console.print(table)
        
    asyncio.run(_list())


def run(
    model_name: str = typer.Argument(..., help="Model to run"),
    prompt: str = typer.Argument(None, help="Prompt to send. If empty, starts interactive mode.")
):
    """
    Run a model with a prompt or start an interactive chat.
    """
    backend = OllamaBackend()
    
    async def _run():
        if prompt:
            console.print(f"🤖 [bold cyan]{model_name}[/bold cyan]: ", end="")
            # Streaming output
            try:
                async for chunk in backend.generate_stream(prompt, model_name):
                    console.print(chunk, end="")
                console.print()  # newline
            except Exception as e:
                console.print(f"\n[red]Error:[/red] {e}")
                
        else:
            console.print(f"💬 Starting interactive chat with [bold cyan]{model_name}[/bold cyan]. Type 'exit' to quit.")
            while True:
                user_input = typer.prompt("You")
                if user_input.lower() in ['exit', 'quit']:
                    break
                
                console.print(f"🤖 [bold cyan]{model_name}[/bold cyan]: ", end="")
                try:
                    async for chunk in backend.generate_stream(user_input, model_name):
                        console.print(chunk, end="")
                    console.print()
                except Exception as e:
                    console.print(f"\n[red]Error:[/red] {e}")
                    
    asyncio.run(_run())
