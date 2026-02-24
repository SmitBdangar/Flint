# Security & Privacy Policy

As an enterprise-grade AI developer toolkit, **Flint** enforces strict data governance natively through its architecture. This document outlines the security postures adopted by the framework.

## 1. Zero-Telemetry Guarantee
Flint does not phone home. There are no tracking pixels, analytics suites, or crash-reporting servers bundled within the CLI or the Desktop Application binaries.

- All database generations (`~/.flint/vector_db`, `~/.flint/chat_history.db`) remain strictly on the host operating system disk context.
- Backends (e.g. Ollama, LM Studio) are routed strictly to `127.0.0.1` or OS-defined `localhost` subnets. 

## 2. Codebase Memory (RAG) Sandboxing
When invoking `flint memory index`, Flint strictly evaluates path security. 

- **Symlink traversal:** Evaluated safely but strongly discouraged.
- **Ignored paths:** Hardcoded drops exist for known high-risk storage targets such as `.git`, `.env`, and secret directories, regardless of user-provided `.gitignore` files.
- **Embeddings:** Vector embedding mathematical conversions happen completely offline; your proprietary source code is never transmitted to OpenAI or third-party proprietary API endpoints for ingestion.

## 3. Autonomous Coder Restrictions
The `flint code` utility evaluates LLM responses and performs an in-place Unified Diff algorithm to propose modifications to the AST.

To ensure developers maintain governance over their repository states:
- **No Execute Flag:** `flint code` cannot trigger bash, powershell, or command line executables on its own.
- **Diff Prompts:** `flint code` will halt standard standard out (`stdout`) and require explicit user input `Confirm.ask("[Y/n]")` before the python IO layer initiates an `open(file, "w")`.

## 4. Supply Chain and Packaging
- Distribution binaries (`dist/Flint Desktop.exe`) are generated entirely locally via `PyInstaller`.
- Dependencies are pinned to minor versions in `pyproject.toml` to prevent immediate zero-day upstream payload injections from automatically bleeding into deployment environments.

If you identify a security vulnerability in Flint, please document the attack surface and open an Issue on the official repository.
