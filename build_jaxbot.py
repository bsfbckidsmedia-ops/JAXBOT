#!/usr/bin/env python3
"""
Build script for JaxBot Console executable.
Creates a single-file .exe using PyInstaller.

Usage:
    python build_jaxbot.py
"""

import subprocess
import sys
import shutil
from pathlib import Path


def main():
    print("=== Building JaxBot Console ===\n")

    # Ensure PyInstaller is available
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyinstaller"]
        )

    # Clean previous build artifacts
    for d in ("build", "dist"):
        p = Path(d)
        if p.exists():
            shutil.rmtree(p)
            print(f"Cleaned {d}/")

    # Run PyInstaller
    cmd = ["pyinstaller", "--clean", "jaxbot_console.spec"]
    print(f"Running: {' '.join(cmd)}\n")

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("\nBuild FAILED.")
        sys.exit(1)

    exe_path = Path("dist") / "JaxBot"
    # On Windows the extension is .exe
    exe_win = Path("dist") / "JaxBot.exe"

    if exe_win.exists():
        print(f"\nBuild SUCCESS: {exe_win}")
        print(f"Size: {exe_win.stat().st_size / (1024*1024):.1f} MB")
    elif exe_path.exists():
        print(f"\nBuild SUCCESS: {exe_path}")
        print(f"Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
    else:
        print("\nBuild completed but executable not found in dist/")
        sys.exit(1)

    print("\nTo run: ./dist/JaxBot  (or dist\\JaxBot.exe on Windows)")


if __name__ == "__main__":
    main()
