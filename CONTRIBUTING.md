# Contributing to Flint

Thank you for your interest in contributing to Flint! We welcome pull requests, bug reports, and discussion.

## Development Setup

1. Fork the repo and clone it locally.
2. Install the project in editable mode with development dependencies:
   ```bash
   pip install -e .[dev,desktop]
   ```
3. Set up pre-commit hooks (if applicable):
   ```bash
   pre-commit install
   ```

## Adding New LLM Backends

Flint is designed to be highly modular. If you want to add support for a new AI engine (e.g., vLLM, OpenAI, Anthropic):
1. Create a new subclass of `BaseBackend` in `src/flint/backends/`.
2. Implement the core async fetching and stream generation methods (`list_models`, `generate_stream`, etc).
3. Ensure you follow Python's `asyncio` best practices so the Typer CLI and PySide6 UI do not block the main loop.
4. Register your backend in `src/flint/backends/__init__.py`.

## Testing

Before submitting a PR, verify the test suite and linter pass:
```bash
pytest
flake8 src/
black --check src/
```
