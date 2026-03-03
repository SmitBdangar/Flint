"""
Prompt abstraction for Flint.
Handles variable interpolation and file loading.
"""

import os
from string import Template
from typing import Dict, Any, Optional
from pathlib import Path

PROMPT_REGISTRY_DIR = Path(os.path.expanduser("~/.flint/prompts"))


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
        Load a prompt from:
        1. The given filesystem path (if it exists)
        2. The ~/.flint/prompts/ registry (by name, with or without .txt extension)
        """
        path = Path(name_or_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return cls(template=content, name=path.stem)

        # FIX: Added registry lookup — check ~/.flint/prompts/<name>.txt
        registry_path = PROMPT_REGISTRY_DIR / name_or_path
        if not registry_path.suffix:
            registry_path = registry_path.with_suffix(".txt")
        if registry_path.exists():
            with open(registry_path, "r", encoding="utf-8") as f:
                content = f.read()
            return cls(template=content, name=name_or_path)

        raise FileNotFoundError(
            f"Prompt template not found at '{name_or_path}' and "
            f"not in the registry at '{PROMPT_REGISTRY_DIR}'"
        )

    def save(self, name: str) -> None:
        """
        Save the prompt to the Flint registry (~/.flint/prompts/<name>.txt).
        """
        # FIX: was a no-op stub — now writes to disk
        PROMPT_REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
        dest = PROMPT_REGISTRY_DIR / f"{name}.txt"
        dest.write_text(self.template, encoding="utf-8")

    def __repr__(self) -> str:
        name_str = f" name='{self.name}'" if self.name else ""
        return f"<Prompt{name_str} length={len(self.template)}>"
