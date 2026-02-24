# Installation

Flint is a local-first AI developer toolkit designed to run seamlessly with local LLM providers like Ollama, LM Studio, and Llama.cpp.

## Prerequisites
1. Python 3.9+
2. A local LLM backend running on your machine:
   - [Ollama](https://ollama.com/) (default port 11434)
   - [LM Studio](https://lmstudio.ai/) (default port 1234)

## Quick Start
Clone the repository and install it in editable mode:
```bash
git clone https://github.com/SmitBdangar/Flint.git
cd Flint
pip install -e .
```

Verify the installation by listing available models:
```bash
flint list
```
