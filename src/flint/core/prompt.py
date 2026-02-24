"""
Prompt abstraction for Flint.
Handles variable interpolation and file loading.
"""

import os
from string import Template
from typing import Dict, Any, Optional
from pathlib import Path


class Prompt:
    """
    Represents a prompt template that can be populated with variables.
    Currently uses simple python string formatting or Template for safety.
    """

    def __init__(self, template: str, name: Optional[str] = None):
        """
        Initialize a Prompt.

        Args:
            template: The string template (e.g., "Summarize this: {{text}}")
                      For now, we will support python's new style formatting: {text}
            name: Optional name for saving/loading from registry.
        """
        self.template = template
        self.name = name

    def format(self, **kwargs: Any) -> str:
        """
        Interpolate the variables into the template.
        Supports {variable_name} syntax.
        """
        # A robust version might use Jinja2. For v0.1, simple f-string style formatting via format() is fine,
        # or string.Template if we want to be safer against missing keys.
        # Let's use str.format but handle missing keys gracefully or just let it raise KeyError.
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing variable for prompt formatting: {e}")

    @classmethod
    def load(cls, name_or_path: str) -> "Prompt":
        """
        Load a prompt from a local file or the Flint prompt registry.
        (v0.1: just loads from a local file path if it exists).
        """
        path = Path(name_or_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return cls(template=content, name=path.stem)

        # In a real implementation, we would lookup from ~/.flint/prompts/
        raise FileNotFoundError(f"Prompt template not found at {name_or_path}")

    def save(self, name: str) -> None:
        """
        Save the prompt to the Flint registry.
        """
        # To be implemented for Prompt Registry feature
        pass

    def __repr__(self) -> str:
        name_str = f" name='{self.name}'" if self.name else ""
        return f"<Prompt{name_str} length={len(self.template)}>"
