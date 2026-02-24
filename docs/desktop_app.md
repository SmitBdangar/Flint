# Flint Desktop App

Flint includes a sleek, ChatGPT-style PySide6 desktop application for conversational AI with your local models, including file attachment support.

## Running the App
Since the desktop module is separated from the core CLI source, you must ensure the `desktop` module is in your Python path to launch it:

```bash
# On Windows PowerShell
$env:PYTHONPATH="$pwd\desktop"; python desktop/app/main.py

# On Linux/macOS
PYTHONPATH="./desktop" python desktop/app/main.py
```

## Features
- **Model Selection:** Automatically detects backends (Ollama, LM Studio) and populates the dropdown dynamically.
- **File Attachments:** Attach local files to provide direct context to the LLM.
- **Code Highlighting:** Chat history dynamically highlights code blocks.
- **Local Vectors:** (Coming to GUI soon) Leverage the `flint memory` databases visually.
