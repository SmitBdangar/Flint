"""
OpenAI-Compatible REST API Server for Flint.
Wraps any configured local backend and exposes a /v1/chat/completions endpoint.
"""
import asyncio
import json
from typing import Optional, List

import typer
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from rich.console import Console

from flint.backends import get_backend
from flint.core.config import config

console = Console()

# ── Pydantic models for the OpenAI-compatible API ──────────────────────────
class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: bool = False
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


def build_app(default_model: str, backend_name: str) -> FastAPI:
    """Build the FastAPI ASGI app."""
    app = FastAPI(title="Flint Local AI Server", version="1.0.0")
    backend = get_backend(backend_name)

    @app.get("/v1/models")
    async def list_models():
        models = await backend.list_models()
        return {
            "object": "list",
            "data": [{"id": m.name, "object": "model"} for m in models],
        }

    @app.post("/v1/chat/completions")
    async def chat_completions(req: ChatCompletionRequest):
        model_name = req.model if req.model else default_model

        # Build the prompt as a simple concatenation for backends that take a
        # single prompt string (Ollama), or forward messages for OpenAI-style
        # backends (llamacpp/lmstudio).
        system_msg = next(
            (m.content for m in req.messages if m.role == "system"), None
        )
        # Concatenate all non-system messages into one user prompt
        user_parts = [m.content for m in req.messages if m.role != "system"]
        prompt = "\n".join(user_parts)

        if req.stream:
            # ── SSE streaming response ─────────────────────────────────────
            async def event_stream():
                try:
                    async for chunk in backend.generate_stream(
                        prompt=prompt,
                        model_name=model_name,
                        system=system_msg,
                    ):
                        payload = {
                            "object": "chat.completion.chunk",
                            "model": model_name,
                            "choices": [
                                {
                                    "delta": {"role": "assistant", "content": chunk},
                                    "finish_reason": None,
                                    "index": 0,
                                }
                            ],
                        }
                        yield f"data: {json.dumps(payload)}\n\n"
                    # Send final [DONE] sentinel
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            return StreamingResponse(
                event_stream(), media_type="text/event-stream"
            )
        else:
            # ── Non-streaming response ─────────────────────────────────────
            try:
                text = await backend.generate(
                    prompt=prompt,
                    model_name=model_name,
                    system=system_msg,
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

            return JSONResponse(
                {
                    "object": "chat.completion",
                    "model": model_name,
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": text},
                            "finish_reason": "stop",
                        }
                    ],
                }
            )

    return app


# ── Typer CLI command ────────────────────────────────────────────────────────
def serve(
    model: str = typer.Option(
        None, "--model", "-m", help="Default model to use for requests."
    ),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind the REST API."),
    host: str = typer.Option(
        "127.0.0.1", "--host", "-h", help="Host to bind the REST API."
    ),
    backend_name: str = typer.Option(
        "ollama",
        "--backend",
        "-b",
        help="Backend to use (ollama, lmstudio, llamacpp).",
    ),
):
    """
    Spin up an OpenAI-compatible REST API in front of a local model.
    Exposes: GET /v1/models and POST /v1/chat/completions
    """
    default_model = model or config.get("defaults", {}).get("model") or "llama3"

    console.print(
        f" [bold green]Flint API Server[/bold green] starting on "
        f"[bold cyan]http://{host}:{port}/v1[/bold cyan]"
    )
    console.print(f" Default model: [bold cyan]{default_model}[/bold cyan]  |  Backend: [green]{backend_name}[/green]")
    console.print(" Press [bold]Ctrl+C[/bold] to stop.\n")

    try:
        # Validate backend before starting the server
        get_backend(backend_name)
    except ValueError as e:
        console.print(f" [bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)

    # Build and serve the ASGI app
    app = build_app(default_model=default_model, backend_name=backend_name)
    uvicorn.run(app, host=host, port=port, log_level="warning")
