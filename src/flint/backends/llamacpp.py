"""
llama.cpp Backend implementation for Flint.
"""

import httpx
import json
from typing import List, AsyncGenerator, Optional
from flint.backends.base import BaseBackend
from flint.core.model import Model


class LlamaCppBackend(BaseBackend):
    def __init__(self, base_url: str = "http://localhost:8080/v1"):
        self.base_url = base_url.rstrip("/")

    @property
    def name(self) -> str:
        return "llamacpp"

    async def list_models(self) -> List[Model]:
        """Fetch models from local llama.cpp instance."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/models")
                response.raise_for_status()
                data = response.json()

                models = []
                for m in data.get("data", []):
                    models.append(
                        Model(
                            name=m["id"],
                            backend_name=self.name,
                            size="Unknown",
                            status="Ready",
                        )
                    )
                return models
            except (httpx.RequestError, httpx.HTTPStatusError):
                return []

    async def pull_model(self, model_name: str) -> None:
        """Pulling via API isn't natively supported by llama.cpp server out of the box in the same way."""
        raise NotImplementedError(
            "llama.cpp backend does not support model pulling via API. Please download models manually."
        )

    async def generate(
        self,
        prompt: str,
        model_name: str,
        stream: bool = False,
        system: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Non-streaming generation."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {"model": model_name, "messages": messages, "stream": False}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions", json=payload, timeout=None
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def generate_stream(
        self, prompt: str, model_name: str, system: Optional[str] = None, **kwargs
    ) -> AsyncGenerator[str, None]:
        """Streaming generation."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {"model": model_name, "messages": messages, "stream": True}

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", f"{self.base_url}/chat/completions", json=payload, timeout=None
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        json_str = line[6:]
                        if json_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(json_str)
                            if data.get("choices") and data["choices"][0].get(
                                "delta", {}
                            ).get("content"):
                                yield data["choices"][0]["delta"]["content"]
                        except json.JSONDecodeError:
                            continue
