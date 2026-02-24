# Flint System Architecture

This document provides a high-level overview of the Flint toolkit's architectural patterns, data flow mechanisms, and backend integration design.

## 1. Core Principles
- **Local-First Executions:** Network requests strictly target `localhost`. External internet calls are reserved purely for upstream package managers or base model pulls initiated by the end-user.
- **Backend Agnosticism:** Operations are decoupled from the underlying LLM inference router via abstract base classes (ABC).
- **Graceful Degradation:** Core CLI capabilities do not rely on UI libraries (`PySide6`), vector databases (`chromadb`), or tokenizer dependencies unless explicitly invoked.

## 2. Component Diagram

```text
+----------------------+        +-------------------------+
|      USER SPACE      |        |     ~/.flint/ STATE     |
|                      |        |                         |
|  [CLI Entrypoint]    |<------>| config.toml             |
|  [Desktop App GUI]   |<------>| chat_history.db (SQLite)|
|                      |        | vector_db/ (ChromaDB)   |
+----------+-----------+        +-------------------------+
           |
           v
+----------------------+        +-------------------------+
|   CORE ABSTRACTIONS  |        |      RAG / MEMORY       |
|                      |        |                         |
| flint.core.model     | <----> | flint.memory.vector_... |
| flint.core.config    |        | (AST Chunking, HNSW)    |
+----------+-----------+        +-------------------------+
           |
           v
+---------------------------------------------------------+
|                    BACKEND DRIVERS                      |
|                                                         |
|  [OllamaBackend]    [LMStudioBackend]   [BaseBackend]   |
+----------+--------------------+-------------------------+
           |                    |
           v                    v
    http://localhost:11434   http://localhost:1234/v1
```

## 3. The Backend Interface (`BaseBackend`)
The core routing entity in Flint is `src/flint/backends/base.py`. Any new AI engine must implement this `ABC`:

```python
class BaseBackend(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    async def list_models(self) -> List[Model]: ...

    @abstractmethod
    async def generate_stream(self, prompt, model_name, **kwargs) -> AsyncGenerator[str, None]: ...
```

By relying strictly on async streams (`httpx`), the Desktop UI and CLI avoid main-thread blocking, rendering 60FPS UI loops even during heavy sequential token decodes.

## 4. RAG Implementation (Vector Memory)
Flint leverages `ChromaDB` configured for local `PersistentClient` storage. 

### Ingestion Flow (`flint memory index`)
1. **Directory Walk:** Driven by `os.walk` but filtered heavily via `pathspec` representing `.gitignore` standard evaluation matrices.
2. **Lexical Chunking:** Managed by OpenAI's `tiktoken` (`cl100k_base` BPE tokenizer) to enforce a hard sub-500 token limit per embedded dimension, minimizing context window overflow.
3. **Database Upsert:** Bulk HTTP inserts via ChromaDB API.

### Retrieval Flow (`Desktop App` / UI)
- Triggers a concurrent blocking wait (`k=4`) query to `vector_db`.
- Astutely merges retrieved semantic `metadatas` (relative pathlines) into the zero-shot prompt header before bridging the payload to the Backend Driver.

## 5. UI Event Loop (PySide6)
The Desktop UI separates the Chromium/WebEngine render loop from the AI polling loop using `QThread` and custom PyQt `Signal` classes in `worker.py`. This ensures typing interrupts and chat scrolling are native speed regardless of GPU lockup on the backend.
