"""
Base backend interface for Flint.
"""
from typing import List, AsyncGenerator, Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseBackend(ABC):
    """
    Abstract base class for all Flint backends (Ollama, llama.cpp, etc.)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the backend (e.g., 'ollama')"""
        pass

    @abstractmethod
    async def list_models(self) -> List["Model"]: # type: ignore # Handle circular import in types later if needed
        """List all available models in the backend."""
        pass

    @abstractmethod
    async def pull_model(self, model_name: str) -> None:
        """Pull a model from the backend's default source (if applicable)."""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model_name: str,
        stream: bool = False,
        system: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text from the model.
        If stream=True, this should technically be handled differently (e.g., streaming async generator, but for simplicity of this signature, we might return strings or yield).
        For now, let's assume it returns the full string if stream=False.
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        model_name: str,
        system: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Generate text from the model as an async stream.
        """
        pass
