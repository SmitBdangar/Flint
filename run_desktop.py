#!/usr/bin/env python
"""
Root-level launcher for the Flint Desktop GUI.

Run from the project root with:
    python run_desktop.py

This avoids needing to `cd desktop/` first.
"""
import sys
import os
from pathlib import Path

# Ensure the correct directories are on sys.path before importing anything.
_ROOT = Path(__file__).resolve().parent        # project root
_SRC_DIR = _ROOT / "src"                       # src/  -> flint.*
_DESKTOP_DIR = _ROOT / "desktop"               # desktop/ -> app.*

for _p in [str(_SRC_DIR), str(_DESKTOP_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Now the imports in desktop/app/main.py will resolve correctly.
from app.main import run  # noqa: E402

if __name__ == "__main__":
    run()
