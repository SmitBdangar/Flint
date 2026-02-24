import typer
from rich.console import Console

try:
    from memory.vector_store import VectorStore
except ImportError:
    VectorStore = None

app = typer.Typer(help="Manage and query the local codebase vector memory.")
console = Console()

@app.command()
def index(
    directory: str = typer.Argument(".", help="The directory to index."),
):
    """Index a directory into the local vector store."""
    if VectorStore is None:
        console.print("[red]VectorStore dependencies are missing. Please ensure chromadb and tiktoken are installed.[/red]")
        raise typer.Exit(1)
        
    console.print(f"Indexing directory: [bold]{directory}[/bold]")
    store = VectorStore()
    store.index_directory(directory)
    console.print("[green]Indexing complete![/green]")

@app.command()
def search(
    query: str = typer.Argument(..., help="The search query."),
    k: int = typer.Option(5, "--results", "-k", help="Number of results to return.")
):
    """Search the vector store for relevant code context."""
    if VectorStore is None:
        console.print("[red]VectorStore dependencies are missing.[/red]")
        raise typer.Exit(1)
        
    store = VectorStore()
    results = store.search(query, k=k)
    
    if not results:
        console.print("No results found.")
        return
        
    console.print(f"\n[bold]Top {len(results)} matches for '{query}':[/bold]\n")
    for i, res in enumerate(results, 1):
        meta = res.get('metadata', {})
        console.print(f"[bold cyan]{i}. File:[/bold cyan] {meta.get('file', 'Unknown')}")
        
        # Print a snippet of the document
        doc = res.get('document', '')
        snippet = doc[:300] + "..." if len(doc) > 300 else doc
        console.print(f"{snippet}\n")
