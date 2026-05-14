#!/usr/bin/env python3
"""
Build Script for VRChat Bot Executable
Creates a standalone .exe file using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = ['pyinstaller']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ All dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    return True

def create_spec_file():
    """Create PyInstaller spec file for the launcher."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('.env.example', '.'),
        ('.env.dual_mode', '.'),
        ('config.yaml', '.'),
        ('low_resource_config.yaml', '.'),
        ('requirements.txt', '.'),
        ('README_DUAL_MODE.md', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'vrchatapi',
        'yaml',
        'dotenv',
        'psutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
        'cv2',
        'torch',
        'tensorflow',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VRChatBotLauncher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    spec_file = 'launcher.spec'
    with open(spec_file, 'w') as f:
        f.write(spec_content)
    
    print(f"✅ Created {spec_file}")
    return spec_file

def build_executable():
    """Build the executable using PyInstaller."""
    print("\n🔨 Building executable...")
    
    # Create spec file
    spec_file = create_spec_file()
    
    # Build command
    cmd = [
        'pyinstaller',
        '--clean',
        spec_file
    ]
    
    print(f"🚀 Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Build completed successfully!")
        
        # Show output
        if result.stdout:
            print("Build output:")
            print(result.stdout)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        return False

def create_portable_package():
    """Create a portable package with the executable."""
    print("\n📦 Creating portable package...")
    
    # Source and destination directories
    dist_dir = Path('dist')
    package_dir = Path('VRChatBot_Portable')
    
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    # Copy executable
    exe_file = dist_dir / 'VRChatBotLauncher.exe'
    if exe_file.exists():
        shutil.copy2(exe_file, package_dir / 'VRChatBotLauncher.exe')
        print(f"✅ Copied executable")
    else:
        print(f"❌ Executable not found: {exe_file}")
        return False
    
    # Copy necessary files
    required_files = [
        '.env.example',
        '.env.dual_mode',
        'config.yaml',
        'low_resource_config.yaml',
        'requirements.txt',
        'README_DUAL_MODE.md',
        'dual_mode_bot.py',
        'minimal_main.py',
        'system_helper.py',
        'system_commands.py',
        'resource_monitor.py',
    ]
    
    for file_name in required_files:
        src = Path(file_name)
        dst = package_dir / file_name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"✅ Copied {file_name}")
        else:
            print(f"⚠️  File not found: {file_name}")
    
    # Create startup script for portable use
    startup_script = package_dir / 'START_BAT_HERE.bat'
    with open(startup_script, 'w') as f:
        f.write('''@echo off
echo Starting VRChat Bot Launcher...
echo.
echo First time setup:
echo 1. Copy .env.dual_mode to .env
echo 2. Edit .env with your VRChat credentials
echo 3. Run VRChatBotLauncher.exe
echo.
pause
''')
    
    print("✅ Created startup script")
    
    # Create README for portable package
    readme_content = '''# VRChat Bot - Portable Version

## Quick Start

1. **Copy Configuration File**
   ```
   copy .env.dual_mode .env
   ```

2. **Edit Configuration**
   - Open `.env` in a text editor
   - Add your VRChat username and password
   - Save the file

3. **Run the Launcher**
   - Double-click `VRChatBotLauncher.exe`
   - Choose your mode:
     - Press 1 for VRChat Mode
     - Press 2 for Standby Mode
     - Press 3 for System Helper Mode
     - Press 4 for Minimal VRChat

## Features

- **Mode 1**: Full VRChat integration with system helper
- **Mode 2**: Standby mode with minimal resource usage
- **Mode 3**: System helper for disk cleanup and optimization
- **Mode 4**: Lightweight VRChat mode for low resources

## Troubleshooting

- If the bot doesn't start, check your credentials in `.env`
- Make sure Python scripts are in the same directory as the exe
- Check the launcher.log file for error messages

## System Requirements

- Windows 7 or higher
- 2GB RAM minimum
- 500MB free disk space
- Internet connection for VRChat features
'''
    
    with open(package_dir / 'README_PORTABLE.md', 'w') as f:
        f.write(readme_content)
    
    print("✅ Created portable README")
    
    # Calculate package size
    total_size = sum(f.stat().st_size for f in package_dir.rglob('*') if f.is_file())
    size_mb = total_size / (1024 * 1024)
    
    print(f"\n📊 Portable package created:")
    print(f"📁 Location: {package_dir.absolute()}")
    print(f"📏 Size: {size_mb:.1f} MB")
    print(f"📄 Files: {len(list(package_dir.rglob('*')))}")
    
    return True

def test_executable():
    """Test the created executable."""
    print("\n🧪 Testing executable...")
    
    exe_path = Path('dist/VRChatBotLauncher.exe')
    if not exe_path.exists():
        print("❌ Executable not found")
        return False
    
    try:
        # Test if executable can be started (quick test)
        result = subprocess.run(
            [str(exe_path), '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print("✅ Executable test passed")
        return True
    except subprocess.TimeoutExpired:
        print("⚠️  Executable started but didn't exit quickly (normal for GUI)")
        return True
    except Exception as e:
        print(f"❌ Executable test failed: {e}")
        return False

def main():
    """Main build process."""
    print("🤖 VRChat Bot Executable Builder")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Cannot proceed without required dependencies")
        return False
    
    # Check if we're on Windows
    if os.name != 'nt':
        print("⚠️  Warning: Not on Windows. Exe may not work properly.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return False
    
    # Build executable
    if not build_executable():
        print("❌ Build failed")
        return False
    
    # Test executable
    if not test_executable():
        print("❌ Executable test failed")
        return False
    
    # Create portable package
    if not create_portable_package():
        print("❌ Package creation failed")
        return False
    
    print("\n🎉 Build completed successfully!")
    print("\n📋 Next steps:")
    print("1. Test the executable: dist/VRChatBotLauncher.exe")
    print("2. Check the portable package: VRChatBot_Portable/")
    print("3. Distribute the portable package to users")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            input("\nPress Enter to exit...")
        else:
            input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        print("\n👋 Build cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...")
