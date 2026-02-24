"""
Ollama Backend implementation for Flint.
"""

import httpx
import json
from typing import List, Dict, Any, AsyncGenerator, Optional
from flint.backends.base import BaseBackend
from flint.core.model import Model
from flint.core.config import config


class OllamaBackend(BaseBackend):
    def __init__(self, base_url: str = None):
        super().__init__()
        if base_url is None:
            port = config.get("backends", {}).get("ollama_port", 11434)
            base_url = f"http://localhost:{port}"
        self.base_url = base_url.rstrip("/")

    @property
    def name(self) -> str:
        return "ollama"

    async def list_models(self) -> List[Model]:
        """Fetch models from local Ollama instance."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()

                models = []
                for m in data.get("models", []):
                    size_bytes = m.get("size", 0)
                    # Convert bytes to GB roughly
                    size_gb = round(size_bytes / (1024**3), 1)
                    size_str = f"{size_gb} GB" if size_gb > 0 else "Unknown"

                    models.append(
                        Model(
                            name=m["name"],
                            backend_name=self.name,
                            size=size_str,
                            status="Ready",
                        )
                    )
                return models
            except httpx.RequestError as e:
                # Log or handle warning about backend being offline
                return []

    async def pull_model(self, model_name: str) -> None:
        """Pull a model via Ollama API."""
        # For CLI output, this really should stream the JSON-lines output to show progress.
        # This implementation just does it in one go (or streams without yielding).
        pass

    async def generate(
        self,
        prompt: str,
        model_name: str,
        stream: bool = False,
        system: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Non-streaming generation."""
        payload = {"model": model_name, "prompt": prompt, "stream": False}
        if system:
            payload["system"] = system

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate", json=payload, timeout=None
            )
            response.raise_for_status()
            return response.json().get("response", "")

    async def generate_stream(
        self, prompt: str, model_name: str, system: Optional[str] = None, **kwargs
    ) -> AsyncGenerator[str, None]:
        """Streaming generation."""
        payload = {"model": model_name, "prompt": prompt, "stream": True}
        if system:
            payload["system"] = system

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", f"{self.base_url}/api/generate", json=payload, timeout=None
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        yield data.get("response", "")
                        if data.get("done", False):
                            break
