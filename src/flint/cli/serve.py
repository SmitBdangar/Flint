import typer
import asyncio
from typing import Optional
from rich.console import Console

console = Console()

def serve(
    model: str = typer.Option("llama3", "--model", "-m", help="Model to serve"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind the REST API"),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host ID to bind the REST API")
):
    """
    Spin up an OpenAI-compatible REST API in front of the local model.
    """
    console.print(f" Starting OpenAI-compatible API Server on http://{host}:{port}/v1")
    console.print(f" Default model routing to: [bold cyan]{model}[/bold cyan]")
    
    # In a full implementation, this uses uvicorn and fastapi:
    # import uvicorn
    # from flint.server.app import app
    # uvicorn.run(app, host=host, port=port)
    
    console.print("[yellow]Note: this is a stub for the architecture demo.[/yellow]")
    console.print("Press Ctrl+C to exit.")
    
    # Stub wait
    try:
        asyncio.run(asyncio.sleep(3600))
    except KeyboardInterrupt:
        console.print("\nServer shutting down.")
