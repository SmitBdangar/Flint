```
███████╗██╗     ██╗███╗   ██╗████████╗
██╔════╝██║     ██║████╗  ██║╚══██╔══╝
█████╗  ██║     ██║██╔██╗ ██║   ██║
██╔══╝  ██║     ██║██║╚██╗██║   ██║
██║     ███████╗██║██║ ╚████║   ██║
╚═╝     ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝  v1.0.0
```

**Zero-telemetry. Fully local. AI-powered development — on your machine, under your control.**

Flint is a local-first AI developer toolkit that wraps Ollama, LM Studio, and llama.cpp with a CLI, a RAG-powered codebase memory layer, inline code generation, and a desktop chat GUI — all running entirely offline.

---

## Requirements

| Dependency | Version | Notes |
|---|---|---|
| Python | >= 3.9 | |
| Ollama | >= 0.1.x | *or* LM Studio / llama.cpp (at least one required) |
| ChromaDB | >= 0.4.x | Auto-installed; uses local ONNX embeddings |
| PySide6 | >= 6.5.x | Desktop app only |

---

## Install

**From source (recommended for now):**

```bash
git clone https://github.com/SmitBdangar/Flint.git
cd Flint

# Core CLI + RAG
py -m pip install -e .

# Core + Desktop GUI
py -m pip install -e ".[desktop]"

# Core + Desktop + Dev tools
py -m pip install -e ".[dev,desktop]"
```

> **Windows note:** Use `py` instead of `python`/`pip` if those aren't on your PATH.

---

## Quick Start

```bash
# 1. Make sure Ollama is running
ollama pull llama3

# 2. Index your codebase for RAG
cd /your/project
py -m flint memory index .

# 3. Ask Flint to modify a file
py -m flint code auth.py "add input validation to the register() function" --model llama3

# 4. Review the diff and approve or reject
# Apply these changes? [y/N]
```

---

## CLI Commands

### `flint list` — List Available Models

Lists all models detected across every running backend (Ollama, LM Studio, llama.cpp).

```bash
py -m flint list
```

### `flint run` — Run / Chat with a Model

Single prompt or interactive multi-turn chat.

```bash
# Single prompt (streams output)
py -m flint run llama3 "Explain async/await in Python"

# Interactive REPL (type 'exit' to quit)
py -m flint run llama3
```

Options: `--backend ollama|lmstudio|llamacpp`

### `flint code` — Inline Code Generation

Reads a file, sends it to the model with your instruction, shows a unified diff, and only writes if you approve.

```bash
py -m flint code path/to/file.py "refactor the DB connection to use a context manager" \
    --model llama3 --backend ollama
```

### `flint memory` — Codebase RAG

Indexes source files into a local ChromaDB vector store (stored at `~/.flint/vector_db`). Embeddings are generated locally via ONNX — no network calls.

```bash
# Index a directory
py -m flint memory index /your/project

# Search the index
py -m flint memory search "how does authentication work?" --results 5
```

Respects `.gitignore` and `.flintignore`. Indexes: `.py .md .txt .js .ts .html .css .json .rs .go`

### `flint commit` — AI Commit Messages

Reads your staged `git diff` and generates a conventional commit message.

```bash
git add -A
py -m flint commit --model llama3

# Auto-commit without confirmation prompt
py -m flint commit --model llama3 --auto-commit
```

### `flint review` — AI Code Review

Reviews your current diff for bugs, security issues, and anti-patterns.

```bash
py -m flint review --model llama3

# Review only staged changes
py -m flint review --staged-only
```

### `flint serve` — OpenAI-Compatible REST API

Wraps any local backend behind an OpenAI-compatible API. Drop-in replacement for apps that support custom base URLs.

```bash
py -m flint serve --model llama3 --port 8000

# Available endpoints:
# GET  http://localhost:8000/v1/models
# POST http://localhost:8000/v1/chat/completions  (streaming + non-streaming)
```

### `flint bench` — Benchmark Models

Measures rough tokens/sec across multiple models.

```bash
py -m flint bench --models "llama3,qwen2.5:0.5b,phi3"
```

### `flint prompt` — Manage Prompt Templates

Save and reuse prompt templates stored in `~/.flint/prompts/`.

```bash
# Save a template to the registry
py -m flint prompt save my-template ./templates/review.txt

# Run a saved template
py -m flint prompt run my-template --model llama3 --var lang=Python
```

---

## Desktop App

A PySide6 GUI with chat history persistence, RAG toggle, file attachment, and multi-session sidebar.

```bash
# From the project root:
python run_desktop.py
```

Features:
- 🔍 **Model selector** — automatically detects all models across all running backends
- 🧠 **Codebase Memory toggle** — attach RAG context from your indexed vector store
- 📎 **File attach** — read any local file into the prompt context
- 🗂 **Chat History** — sessions persist in `~/.flint/chat_history.db` (SQLite)
- 🎨 **Dark ChatGPT-style UI** with markdown + code block rendering

---

## Configuration

Flint reads `~/.flint/config.toml` on startup. All values are optional.

```toml
[backends]
ollama_port   = 11434   # default
lmstudio_port = 1234    # default

[defaults]
model = "llama3"        # used by flint serve when no --model is given
```

---

## Development

```bash
git clone https://github.com/SmitBdangar/Flint.git
cd Flint

py -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS / Linux

py -m pip install -e ".[dev,desktop]"
```

**Run tests:**

```bash
py -m pytest tests/ -v
```

```
============================= test session starts =============================
collected 4 items

tests/test_core/test_basic.py::test_model_initialization PASSED          [ 25%]
tests/test_core/test_basic.py::test_prompt_formatting    PASSED          [ 50%]
tests/test_core/test_basic.py::test_chain_add            PASSED          [ 75%]
tests/test_core/test_prompt.py::test_prompt_missing_key  PASSED          [100%]

============================== 4 passed in 0.03s ==============================
```

---

## Architecture

```
Flint/
├── src/flint/
│   ├── backends/        # Ollama, LM Studio, llama.cpp HTTP clients
│   ├── core/            # Model, Prompt, Chain abstractions
│   ├── memory/          # ChromaDB vector store + tiktoken chunker
│   └── cli/             # Typer CLI commands
├── desktop/app/         # PySide6 GUI (main, ui_main, worker, history)
├── run_desktop.py       # Root-level launcher for the desktop app
└── pyproject.toml
```

All backends communicate over localhost HTTP — **no cloud calls, no telemetry, no API keys.**

---

## Contributing

1. Fork & clone the repo
2. Branch: `git checkout -b feat/your-feature`
3. Code + test: `py -m pytest`
4. Lint: `black . && isort .`
5. Open a PR

Bug reports and feature requests welcome. Open an issue first for large changes.

---

## License

MIT © Flint Community
