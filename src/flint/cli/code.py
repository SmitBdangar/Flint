import typer
import asyncio
import os
import re
from pathlib import Path
from rich.console import Console
from flint.backends import get_backend

console = Console()

def extract_code_block(text: str) -> str:
    """
    Extracts the first markdown code block from the given text.
    If no block is found, returns the raw text trimmed.
    """
    pattern = r"```[\w]*\n(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def code(
    file_path: Path = typer.Argument(..., help="Path to the file to modify"),
    instruction: str = typer.Argument(..., help="Instruction for what to change"),
    backend_name: str = typer.Option("ollama", "--backend", "-b", help="Backend to use (ollama, lmstudio, llamacpp)"),
    model_name: str = typer.Option(..., "--model", "-m", help="Model to use (e.g., qwen2.5:0.5b)")
):
    """
    Autonomous inline coder. Reads a file and overwrites it with AI modifications.
    """
    if not file_path.exists() or not file_path.is_file():
        console.print(f"❌ [bold red]Error:[/bold red] The file '{file_path}' does not exist.")
        raise typer.Exit(1)

    try:
        backend = get_backend(backend_name)
    except ValueError as e:
        console.print(f"❌ [bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()

    console.print(f"🤖 [bold cyan]flint code[/bold cyan]: Modifying [green]{file_path.name}[/green] via {backend.name} ({model_name})...")

    system_prompt = (
        "You are an expert software developer. "
        "You have been asked to modify an existing file based on instructions.\n"
        "OUTPUT ONLY THE FINAL MODIFIED CODE in a single markdown code block.\n"
        "DO NOT output any explanations, greetings, or other text before or after the code block. "
        "Your output must be completely ready to overwrite the original file."
    )

    user_prompt = f"File Contents:\n```\n{file_content}\n```\n\nInstruction: {instruction}"

    async def _run():
        try:
            # We don't stream here because we want to parse the final output block cleanly
            # and write it to disk all at once.
            response = await backend.generate(
                prompt=user_prompt,
                model_name=model_name,
                system=system_prompt,
                stream=False
            )
            
            new_code = extract_code_block(response)
            
            # Simple safety check: if the model returned nothing or just garbage
            if not new_code:
                 console.print("❌ [bold red]Error:[/bold red] The model returned an empty script.")
                 raise typer.Exit(1)

            # Overwrite file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_code)
                
            console.print(f"✅ Success! In-place modification written to [bold green]{file_path}[/bold green].")
            
        except Exception as e:
            console.print(f"\n[red]Error generating code:[/red] {e}")
            raise typer.Exit(1)

    asyncio.run(_run())
