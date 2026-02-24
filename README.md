```
███████╗██╗     ██╗███╗   ██╗████████╗
██╔════╝██║     ██║████╗  ██║╚══██╔══╝
█████╗  ██║     ██║██╔██╗ ██║   ██║   
██╔══╝  ██║     ██║██║╚██╗██║   ██║   
██║     ███████╗██║██║ ╚████║   ██║   
╚═╝     ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝  v0.1.0
```

**Zero-telemetry. Fully local. AI-powered development — on your machine, under your control.**

```bash
$ flint --version
flint 0.1.0 — local-first AI dev toolkit (python 3.12, linux/amd64)
backend: ollama @ localhost:11434
memory:  chromadb (indexed: 1,842 chunks)
```

## Requirements

```
Python     >= 3.10
Ollama     >= 0.1.x   OR   LM Studio >= 0.2.x   (at least one required)
ChromaDB   >= 0.4.x   (auto-installed)
PySide6    >= 6.6.x   (for desktop app only)
```

## Install

**From PyPI**

```bash
pip install flint
```

**From source**

```bash
git clone https://github.com/SmitBdangar/Flint.git
cd Flint
pip install -e .
```

## Quick Start

```bash
# 1. Make sure Ollama is running
ollama pull codellama

# 2. Index your codebase
cd /your/project
flint memory index

# 3. Ask Flint to make a code change
flint code "add input validation to the register() function in auth.py"

# 4. Review the diff and approve
# [Y/n]?
```

## Commands

### `flint code` — Autonomous Coding

Flint reads your codebase, understands the context via RAG, and streams AI-generated edits as a **git-style unified diff**. Nothing is written to disk until you approve.

```bash
$ flint code "refactor the database connection to use a context manager"

[✓] reading codebase context...
[✓] querying memory (top 8 chunks)...
[~] streaming edits from codellama:13b...

--- a/src/db/connection.py
+++ b/src/db/connection.py
@@ -12,9 +12,12 @@
-def get_connection():
-    conn = sqlite3.connect(DB_PATH)
-    return conn
+from contextlib import contextmanager
+
+@contextmanager
+def get_connection():
+    conn = sqlite3.connect(DB_PATH)
+    try:
+        yield conn
+    finally:
+        conn.close()

Apply these changes? [Y/n]: y
[✓] db/connection.py updated.
```

**Options:**

```
flint code [OPTIONS] PROMPT

Options:
  --file PATH      Target a specific file (skips RAG lookup)
  --model TEXT     Override model for this run
  --dry-run        Show diff but never prompt to apply
  --no-memory      Disable RAG context for this run
  -h, --help       Show this message and exit.
```

### `flint memory` — Codebase RAG

Flint uses **ChromaDB** to vectorize your entire repository into a local, offline vector store. It respects your `.gitignore`, chunks files intelligently, and gives the AI deep structural understanding of your project.

```bash
# Index the current directory
$ flint memory index

[✓] scanning project...
[✓] .gitignore rules applied (skipped 214 files)
[~] chunking 87 source files...
[✓] vectorized 1,842 chunks → .flint/memory/chromadb
    done in 4.2s

# Query the index directly
$ flint memory query "how is authentication handled?"

[1] src/auth/jwt.py         score: 0.94
[2] src/auth/middleware.py  score: 0.91
[3] src/users/models.py     score: 0.87

# Check index status
$ flint memory status

  index     : .flint/memory/chromadb
  files     : 87
  chunks    : 1,842
  last run  : 2026-02-24 11:03:41
  model     : nomic-embed-text (local)
```

**Options:**

```
flint memory [COMMAND]

Commands:
  index   Build or rebuild the vector index.
  query   Search the index with a natural language query.
  status  Show index stats.
  clear   Delete the local vector store.

flint memory index [OPTIONS]
  --path PATH      Root directory to index  [default: cwd]
  --chunk-size N   Token chunk size  [default: 512]
  --force          Re-index even if up to date
```

### `flint chat` — Terminal Chat

Prefer staying in the terminal? `flint chat` opens a rich interactive REPL with the same memory and model options as the GUI.

```bash
$ flint chat --memory

  flint chat  |  model: codellama:13b  |  memory: ON
  type /help for commands, /exit to quit
  ─────────────────────────────────────────────────

  you › how does the job queue work in this project?

  flint › Based on your codebase, the job queue is implemented
          in src/workers/queue.py using Redis as the broker.
          Tasks are registered with the @job decorator and
          dispatched via JobQueue.push(). Workers are started
          with `python -m workers.runner`...

  you › /exit
```

## Configuration

Flint stores config at `~/.config/flint/config.toml` (global) or `.flint/config.toml` (per-project).

```toml
[flint]
backend = "ollama"           # ollama | lmstudio
model   = "codellama:13b"
host    = "http://localhost:11434"

[flint.memory]
enabled    = true
chunk_size = 512
embed_model = "nomic-embed-text"
db_path    = ".flint/memory/chromadb"

[flint.history]
db_path  = ".flint/history.db"
max_msgs = 1000

[flint.app]
theme = "dark"               # dark | light
```

**Initialize config for a project:**

```bash
$ flint config init

[✓] created .flint/config.toml
[✓] added .flint/ to .gitignore
```

## Development

```bash
git clone https://github.com/SmitBdangar/Flint.git
cd Flint

python -m venv .venv
source .venv/bin/activate       # windows: .venv\Scripts\activate

pip install -e ".[dev,desktop]"
```

**Run tests**

```bash
pytest

pytest --cov=flint --cov-report=term-missing tests/
```

```
========================= test session starts ==========================
platform linux -- Python 3.12.2, pytest-8.1.0
collected 38 items

tests/test_core/test_agent.py  ..............    [ 36%]
tests/test_core/test_memory.py ............      [ 68%]
tests/test_core/test_diff.py   ............      [100%]

----------- coverage: platform linux, python 3.12.2 -----------
Name                        Stmts   Miss  Cover
-----------------------------------------------
src/flint/core/agent.py        58      0   100%
src/flint/core/diff.py         34      0   100%
src/flint/memory/indexer.py    47      2    96%
src/flint/memory/store.py      29      0   100%
-----------------------------------------------
TOTAL                         168      2    98%

========================= 38 passed in 1.04s ==========================
```

## Contributing

```bash
# 1. fork & clone
git clone https://github.com/YOUR_USERNAME/Flint.git

# 2. branch
git checkout -b feat/your-feature

# 3. code + test
pytest

# 4. lint
ruff check .

# 5. PR
git push origin feat/your-feature
```

Open an issue first for large changes. Bug reports and feature requests welcome.

---

## License

```
MIT License — Copyright (c) 2026 Smit Dangar
Your code stays on your machine. Always.
```
