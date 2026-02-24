import typer
import time
import asyncio
from typing import List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from flint.backends.ollama import OllamaBackend

console = Console()

def bench(
    models: str = typer.Option(..., "--models", "-m", help="Comma separated list of models to benchmark"),
    task: str = typer.Option("summarize", "--task", "-t", help="Task type (summarize, coding, etc.)")
):
    """
    Run speed/quality benchmarks across models.
    """
    model_list = [m.strip() for m in models.split(",")]
    backend = OllamaBackend()
    
    console.print(f" Starting Benchmark: [bold]{task}[/bold] across {len(model_list)} models")
    
    # Very simple stub benchmark logic to measure tokens/sec roughly
    prompt = "Explain quantum computing in exactly 50 words."
    
    results = []

    async def _run_bench():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            
            for m in model_list:
                progress.add_task(description=f"Benchmarking {m}...", total=None)
                start_time = time.time()
                try:
                    text = await backend.generate(prompt=prompt, model_name=m)
                    
                    elapsed = time.time() - start_time
                    words = len(text.split())
                    # Rough token estimate
                    tokens = words * 1.3
                    tps = tokens / elapsed
                    
                    results.append({"model": m, "tps": round(tps, 2), "status": "Success"})
                except Exception as e:
                    results.append({"model": m, "tps": 0.0, "status": "Failed"})

        # Print results
        table = Table(title="Benchmark Results", show_header=True, header_style="bold green")
        table.add_column("Model Name", style="cyan")
        table.add_column("Est. Tokens/sec", justify="right")
        table.add_column("Status")
        
        for r in results:
            table.add_row(r["model"], f"{r['tps']} t/s" if r["tps"] > 0 else "-", r["status"])
            
        console.print(table)

    asyncio.run(_run_bench())
