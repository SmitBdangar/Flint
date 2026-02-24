"""
Model abstraction for Flint.
"""

from typing import Optional, Dict


class Model:
    """
    Represents a local LLM across any backend.
    """

    def __init__(
        self,
        name: str,
        backend_name: Optional[str] = None,
        size: Optional[str] = None,
        quantization: Optional[str] = None,
        status: str = "Ready",
        metadata: Optional[Dict] = None,
    ):
        self.name = name
        self.backend_name = backend_name or "ollama"  # Default to Ollama for now
        self.size = size
        self.quantization = quantization
        self.status = status
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        return f"<Model name={self.name} backend={self.backend_name}>"

    # TODO: Helper methods, e.g., to run generation directly from model obj
    # def run(self, prompt: str):
    #     backend = get_backend(self.backend_name)
    #     return backend.generate(prompt, self.name)
