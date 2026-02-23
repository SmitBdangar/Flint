import sys
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
