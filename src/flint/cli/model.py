import typer
import asyncio
from rich.console import Console
from rich.table import Table
from flint.backends.ollama import OllamaBackend
from flint.core.model import Model

console = Console()

def pull(model_name: str = typer.Argument(..., help="Name of the model to pull (e.g., llama3)"),
         backend_name: str = typer.Option("ollama", "--backend", "-b", help="Backend to use (ollama, lmstudio, llamacpp)")):
    """
    Pull a model from the specified backend.
    """
    from flint.backends import get_backend
    
    try:
        backend = get_backend(backend_name)
    except ValueError as e:
        console.print(f"❌ [bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
        
    console.print(f"📥 Pulling model [bold cyan]{model_name}[/bold cyan] via {backend.name}...")
    
    # In v0.1 we only support native pulling via Ollama CLI wrapper
    if backend.name == "ollama":
        import subprocess
        result = subprocess.run(["ollama", "pull", model_name], capture_output=False)
        if result.returncode == 0:
            console.print(f"✅ Successfully pulled [bold green]{model_name}[/bold green].")
        else:
            console.print(f"❌ Failed to pull [bold red]{model_name}[/bold red]. Is Ollama running?")
            raise typer.Exit(1)
    else:
        # Fallback to the backend's pull_model which raises NotImplementedError gracefully
        async def _pull():
            try:
                await backend.pull_model(model_name)
            except NotImplementedError as e:
                console.print(f"⚠️ [yellow]{e}[/yellow]")
        asyncio.run(_pull())


def list_models():
    """
    List downloaded local models across all supported backends.
    """
    from flint.backends import get_all_backends
    
    async def _list():
        backends = get_all_backends()
        
        # Concurrently fetch models from all backends
        tasks = [b.list_models() for b in backends]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        models = []
        for result in results:
            if isinstance(result, list):
                models.extend(result)
        
        table = Table(title="Local AI Models (Flint)", show_header=True, header_style="bold magenta")
        table.add_column("Model Name", style="cyan")
        table.add_column("Backend", style="green")
        table.add_column("Size", justify="right")
        table.add_column("Status", style="yellow")
        
        if not models:
            console.print("No models found across any backend.")
            return

        for m in models:
            table.add_row(m.name, m.backend_name, str(m.size), m.status)
            
        console.print(table)
        
    asyncio.run(_list())


def run(
    model_name: str = typer.Argument(..., help="Model to run"),
    prompt: str = typer.Argument(None, help="Prompt to send. If empty, starts interactive mode."),
    backend_name: str = typer.Option("ollama", "--backend", "-b", help="Backend to use (ollama, lmstudio, llamacpp)")
):
    """
    Run a model with a prompt or start an interactive chat.
    """
    from flint.backends import get_backend
    
    try:
        backend = get_backend(backend_name)
    except ValueError as e:
        console.print(f"❌ [bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    
    async def _run():
        if prompt:
            console.print(f"🤖 [bold cyan]{model_name}[/bold cyan] (via {backend.name}): ", end="")
            # Streaming output
            try:
                async for chunk in backend.generate_stream(prompt, model_name):
                    console.print(chunk, end="")
                console.print()  # newline
            except Exception as e:
                console.print(f"\n[red]Error:[/red] {e}")
                
        else:
            console.print(f"💬 Starting interactive chat with [bold cyan]{model_name}[/bold cyan] via {backend.name}. Type 'exit' to quit.")
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
