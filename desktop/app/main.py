import sys
import os
from pathlib import Path

# FIX: Ensure both `src/` (for flint.*) and `desktop/` (for app.*) are on sys.path
# so the app can be run from any working directory (including the project root).
_HERE = Path(__file__).resolve().parent          # desktop/app/
_DESKTOP_DIR = _HERE.parent                      # desktop/
_SRC_DIR = _DESKTOP_DIR.parent / "src"           # src/

for _p in [str(_SRC_DIR), str(_DESKTOP_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from PySide6.QtWidgets import QApplication
from app.ui_main import MainWindow

def run():
    app = QApplication(sys.argv)
    
    # Ensure Windows displays icon correctly by setting App ID 
    try:
        from ctypes import windll  # type: ignore
        windll.shell32.SetCurrentProcessExplicitAppUserModelID("flint.desktop.app")
    except ImportError:
        pass

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()
