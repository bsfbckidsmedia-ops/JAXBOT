#!/usr/bin/env python3
"""
Build Script for JaxBot Console Executable
Creates a standalone .exe file using PyInstaller.

Usage:
    python build_exe.py          # builds dist/JaxBot.exe
    python build_exe.py --pack   # builds + creates portable zip
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")

    required_packages = ['pyinstaller']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"  {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"  {package} - MISSING")

    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install'] + missing_packages
            )
            print("All dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            return False

    return True


def build_executable():
    """Build the executable using PyInstaller and the existing spec file."""
    print("\nBuilding executable...")

    spec_file = Path('jaxbot_console.spec')
    if not spec_file.exists():
        print(f"ERROR: {spec_file} not found")
        return False

    # Clean previous build artifacts
    for d in ('build', 'dist'):
        p = Path(d)
        if p.exists():
            shutil.rmtree(p)
            print(f"  Cleaned {d}/")

    cmd = ['pyinstaller', '--clean', str(spec_file)]
    print(f"  Running: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, check=True)
        print("Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False


def create_portable_package():
    """Create a portable package with the executable and config files."""
    print("\nCreating portable package...")

    dist_dir = Path('dist')
    package_dir = Path('JaxBot_Portable')

    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)

    # Locate the built executable
    exe_name = 'JaxBot.exe' if os.name == 'nt' else 'JaxBot'
    exe_file = dist_dir / exe_name
    if not exe_file.exists():
        print(f"ERROR: Executable not found: {exe_file}")
        return False

    shutil.copy2(exe_file, package_dir / exe_name)
    print(f"  Copied {exe_name}")

    # Copy config files that should ship alongside the exe
    config_files = [
        'nano.env',
        'config.yaml',
        'low_resource_config.yaml',
    ]

    for fname in config_files:
        src = Path(fname)
        if src.exists():
            shutil.copy2(src, package_dir / fname)
            print(f"  Copied {fname}")
        else:
            print(f"  Skipped {fname} (not found)")

    # Create a startup batch file (Windows)
    bat = package_dir / 'START.bat'
    bat.write_text(
        '@echo off\r\n'
        'echo Starting JaxBot Console...\r\n'
        'echo.\r\n'
        'JaxBot.exe\r\n'
        'pause\r\n'
    )
    print("  Created START.bat")

    # Create a quick README
    readme = package_dir / 'README.txt'
    readme.write_text(
        'JaxBot - VRChat ChatBox & TTS Standby Bot\n'
        '==========================================\n\n'
        'Quick Start:\n'
        '  1. Edit nano.env with your VRChat credentials\n'
        '  2. Double-click START.bat (or run JaxBot.exe)\n'
        '  3. Type "start" in the console to launch the bot\n'
        '  4. Type "help" for a list of all commands\n\n'
        'Requirements:\n'
        '  - VRChat with OSC enabled (Settings > OSC > Enable)\n'
        '  - Windows 7 or higher\n'
        '  - espeak-ng (for TTS on non-Windows systems)\n'
    )
    print("  Created README.txt")

    total_size = sum(f.stat().st_size for f in package_dir.rglob('*') if f.is_file())
    print(f"\nPortable package: {package_dir.absolute()}")
    print(f"  Size: {total_size / (1024*1024):.1f} MB")
    print(f"  Files: {len(list(package_dir.rglob('*')))}")

    return True


def main():
    """Main build process."""
    print("=== JaxBot Executable Builder ===\n")

    if not check_dependencies():
        print("Cannot proceed without required dependencies")
        return False

    if not build_executable():
        print("Build failed")
        return False

    # Create portable package if --pack flag is passed
    if '--pack' in sys.argv:
        if not create_portable_package():
            print("Package creation failed")
            return False

    exe_name = 'JaxBot.exe' if os.name == 'nt' else 'JaxBot'
    print(f"\nDone! Run: dist/{exe_name}")
    if '--pack' not in sys.argv:
        print("Tip: run with --pack to create a portable zip package")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nBuild cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
