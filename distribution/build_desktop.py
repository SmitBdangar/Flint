import os
import sys
from pathlib import Path

def build_app():
    print("Building Flint Desktop App...")
    
    # Ensure pyinstaller is installed
    try:
        import PyInstaller.__main__
    except ImportError:
        print("PyInstaller is missing. Please install it using 'pip install pyinstaller'")
        sys.exit(1)

    root_dir = Path(__file__).resolve().parent.parent
    main_script = root_dir / "desktop" / "app" / "main.py"
    
    if not main_script.exists():
        print(f"Error: Could not find desktop app main script at {main_script}")
        sys.exit(1)
        
    print(f"Main script path: {main_script}")
    
    # Run PyInstaller
    PyInstaller.__main__.run([
        str(main_script),
        '--name=Flint Desktop',
        '--windowed', # Hide console window
        '--onedir',   # Create a directory containing the executable and dependencies
        '--noconfirm', # Overwrite output if it exists
        '--clean',     # Clean PyInstaller cache
        f'--distpath={root_dir / "dist"}',
        f'--workpath={root_dir / "build"}'
    ])
    
    print("\n✅ Build complete! You can find the executable in the 'dist' directory.")

if __name__ == "__main__":
    build_app()
