# FLINT

## DESCRIPTION
**Flint** is a local-first, terminal-native AI development toolkit. It provides seamless abstractions over local inference engines (Ollama, LM Studio) and equips engineers with autonomous inline coding capabilities, semantic repository memory (RAG), and a rapid prototyping Desktop GUI.

All computations are local. No telemetry. No paywalls. No cloud dependencies.

## COMMANDS

**flint list**
    List all LLM models currently downloaded to the local machine via registered backend providers (e.g., Ollama).

**flint pull** *MODEL_NAME*
    Pull a remote model to local storage via the backend provider.

**flint code** *FILE* *INSTRUCTION* [**-m** *MODEL*] [**-b** *BACKEND*]
    Invoke autonomous repository modifications. Flint interprets the given *INSTRUCTION*, evaluates the target *FILE*, and generates a `difflib` AST unified diff. Prompts for [Y/n] verification before writing directly to disk.

**flint bench** *PROMPT* [**--iterations** *N*]
    Conduct automated generative latency benchmarking to assess tokens/sec inference speeds across available local hardware.

**flint memory index** *DIR*
    Recursively walk *DIR*, ignoring pathspec rules (e.g. `.gitignore`, `node_modules`), and encode repository text using `tiktoken` into a local `ChromaDB` vector graph (`~/.flint/vector_db`).

**flint memory search** *QUERY*
    Query the internal vector graph to retrieve the most semantically relevant AST blocks.

## CONFIGURATION
Flint reads global configurations from `~/.flint/config.toml`. 

Example configuration:
```toml
[backends]
ollama_port = 11434
lmstudio_port = 1234
```

## ENVIRONMENT
Requires Python 3.9+ for CLI operations.
Standalone Desktop Application relies on Qt6 bindings (`PySide6`).
