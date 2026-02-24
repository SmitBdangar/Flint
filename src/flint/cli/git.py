import typer
import asyncio
import subprocess
from rich.console import Console
from flint.backends import get_backend

console = Console()
app = typer.Typer(help="Git-integrated local AI commands.")


def _get_git_diff(staged: bool = True) -> str:
    """Helper to safely fetch git diff."""
    try:
        cmd = ["git", "diff", "--cached"] if staged else ["git", "diff"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        console.print(
            " [bold red]Error running git diff.[/bold red] Ensure this is a git repository."
        )
        raise typer.Exit(1)
    except FileNotFoundError:
        console.print(
            " [bold red]Git not found.[/bold red] Please ensure git is installed and in your PATH."
        )
        raise typer.Exit(1)


@app.command("commit")
def generate_commit(
    auto_commit: bool = typer.Option(
        False, "--auto-commit", "-a", help="Automatically commit the generated message"
    ),
    backend_name: str = typer.Option(
        "ollama", "--backend", "-b", help="Backend to use"
    ),
    model_name: str = typer.Option(
        "qwen2.5:0.5b", "--model", "-m", help="Model to use"
    ),
):
    """
    Generate a commit message based on your staged changes using a local AI model.
    """
    diff = _get_git_diff(staged=True)
    if not diff:
        # Fallback to unstaged logic if absolutely nothing is staged to be helpful
        diff_unstaged = _get_git_diff(staged=False)
        if diff_unstaged:
            console.print(
                " [yellow]You have no staged changes, but you have unstaged changes.[/yellow] Please `git add` the files you want to commit first."
            )
        else:
            console.print("[cyan]No changes found to commit.[/cyan]")
        raise typer.Exit(0)

    try:
        backend = get_backend(backend_name)
    except ValueError as e:
        console.print(f" [bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)

    console.print(f" Analyzing git diff with {backend.name} ({model_name})...")

    system_prompt = (
        "You are an expert developer. You are analyzing a git diff and writing a concise, "
        "conventional commit message for these changes.\n"
        "OUTPUT ONLY the commit message. "
        "Do not wrap it in a code block or include greetings."
    )
    user_prompt = f"```diff\n{diff}\n```\n\nGenerate the commit message."

    async def _run():
        try:
            commit_message = await backend.generate(
                prompt=user_prompt,
                model_name=model_name,
                system=system_prompt,
                stream=False,
            )
            commit_message = commit_message.strip()
            # Remove any markdown code blocks the model might have still injected
            if commit_message.startswith("```") and commit_message.endswith("```"):
                lines = commit_message.split("\n")[1:-1]
                commit_message = "\n".join(lines).strip()

            console.print("\n[bold green]Suggested Commit Message:[/bold green]")
            console.print("-" * 40)
            console.print(commit_message)
            console.print("-" * 40 + "\n")

            if auto_commit:
                result = subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    console.print(" [bold green]Successfully committed![/bold green]")
                else:
                    console.print(
                        f" [bold red]Git commit failed:[/bold red]\n{result.stderr}"
                    )
            elif typer.confirm("Would you like to commit with this message now?"):
                result = subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    console.print(" [bold green]Successfully committed![/bold green]")
                else:
                    console.print(
                        f" [bold red]Git commit failed:[/bold red]\n{result.stderr}"
                    )

        except Exception as e:
            console.print(f"\n[red]Error generating commit message:[/red] {e}")
            raise typer.Exit(1)

    asyncio.run(_run())


@app.command("review")
def code_review(
    staged_only: bool = typer.Option(
        False, "--staged-only", "-s", help="Only review staged changes"
    ),
    backend_name: str = typer.Option(
        "ollama", "--backend", "-b", help="Backend to use"
    ),
    model_name: str = typer.Option(
        "qwen2.5:0.5b", "--model", "-m", help="Model to use"
    ),
):
    """
    Perform an AI code review on your current git diff.
    """
    diff = _get_git_diff(staged=staged_only)
    if not diff:
        console.print("[cyan]No changes found to review.[/cyan]")
        raise typer.Exit(0)

    try:
        backend = get_backend(backend_name)
    except ValueError as e:
        console.print(f" [bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)

    console.print(f" Reviewing code with {backend.name} ({model_name})...\n")

    system_prompt = (
        "You are an expert senior software engineer reviewing code changes.\n"
        "Focus on pointing out potential bugs, security vulnerabilities, or anti-patterns.\n"
        "Provide constructive and concise feedback. If the code looks perfect, say so briefly.\n"
    )
    user_prompt = f"Please review this diff:\n```diff\n{diff}\n```"

    async def _run():
        try:
            async for chunk in backend.generate_stream(
                prompt=user_prompt, model_name=model_name, system=system_prompt
            ):
                console.print(chunk, end="")
            console.print("\n")
        except Exception as e:
            console.print(f"\n[red]Error generating review:[/red] {e}")
            raise typer.Exit(1)

    asyncio.run(_run())
