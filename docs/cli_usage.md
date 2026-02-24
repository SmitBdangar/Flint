# CLI Usage

The `flint` CLI offers a suite of tools for leveraging your local AI models.

## Core Commands

### `flint list`
Lists all available models across detected local backends.

### `flint pull <model>`
Pulls a new model (currently supports Ollama).

### `flint bench`
Runs a basic benchmark to test the speed and capability of a local model.

### `flint code <file> <prompt>`
Autonomous file modification. Flint will read the file, send it to the LLM with your prompt, extract the modified code, and rewrite the file *in-place*. 
```bash
flint code src/main.py "Refactor this file to use async IO"
```

### `flint memory index <dir>`
Indexes a local directory into ChromaDB so the AI can perform semantic search across your codebase.

### `flint memory search <query>`
Queries the local vector database for matching codebase snippets.
```bash
flint memory search "database connection"
```
