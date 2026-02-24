from flint.backends.ollama import OllamaBackend
from flint.backends.lmstudio import LMStudioBackend
from flint.backends.llamacpp import LlamaCppBackend
from flint.backends.base import BaseBackend

_BACKENDS = {
    "ollama": OllamaBackend,
    "lmstudio": LMStudioBackend,
    "llamacpp": LlamaCppBackend,
}


def get_backend(name: str) -> BaseBackend:
    """
    Factory function to get a backend instance by name.
    """
    if name not in _BACKENDS:
        raise ValueError(
            f"Unknown backend: {name}. Supported backends: {', '.join(_BACKENDS.keys())}"
        )

    return _BACKENDS[name]()


def get_all_backends() -> list[BaseBackend]:
    """
    Returns an instance of all supported backends.
    """
    return [backend() for backend in _BACKENDS.values()]
