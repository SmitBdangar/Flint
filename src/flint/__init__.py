"""
Flint: A local-first developer toolkit for AI models.
"""

__version__ = "0.1.0"

from flint.core.model import Model
from flint.core.prompt import Prompt
from flint.core.chain import Chain

__all__ = ["Model", "Prompt", "Chain"]
