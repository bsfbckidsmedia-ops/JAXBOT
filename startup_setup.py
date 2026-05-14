#!/usr/bin/env python3
"""
Startup Setup for Dual-Mode VRChat Bot
Configures auto-launch and startup services.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def create_startup_script():
    """Create startup script for the bot."""
    script_content = f"""#!/bin/bash
# Dual-Mode VRChat Bot Startup Script
cd "{os.getcwd()}"
echo "Starting Dual-Mode VRChat Bot..."
python3 dual_mode_bot.py
"""
    
    script_path = os.path.join(os.getcwd(), "start_bot.sh")
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    os.chmod(script_path, 0o755)
    return script_path

def setup_windows_startup():
    """Setup auto-start on Windows."""
    try:
        import winreg
        
        # Get current directory
        bot_dir = os.getcwd()
        exe_path = sys.executable
        script_path = os.path.join(bot_dir, "dual_mode_bot.py")
        
        # Create startup entry
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(
            key,
            "DualModeVRChatBot",
            0,
            winreg.REG_SZ,
            f'"{exe_path}" "{script_path}"'
        )
        
        winreg.CloseKey(key)
        print("✅ Windows startup configured successfully")
        return True
        
    except ImportError:
        print("❌ winreg not available, manual setup required")
        return False
    except Exception as e:
        print(f"❌ Windows startup setup failed: {e}")
        return False

def setup_macos_startup():
    """Setup auto-start on macOS."""
    try:
        # Get current directory
        bot_dir = os.getcwd()
        script_path = os.path.join(bot_dir, "dual_mode_bot.py")
        
        # Create plist file
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dualmode.vrchatbot</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{script_path}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{bot_dir}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{bot_dir}/startup.log</string>
    <key>StandardErrorPath</key>
    <string>{bot_dir}/startup.error.log</string>
</dict>
</plist>
"""
        
        # Create LaunchAgents directory if it doesn't exist
        launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
        os.makedirs(launch_agents_dir, exist_ok=True)
        
        # Write plist file
        plist_path = os.path.join(launch_agents_dir, "com.dualmode.vrchatbot.plist")
        with open(plist_path, 'w') as f:
            f.write(plist_content)
        
        # Load the agent
        result = subprocess.run(['launchctl', 'load', plist_path], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ macOS startup configured successfully")
            return True
        else:
            print(f"❌ Failed to load launch agent: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ macOS startup setup failed: {e}")
        return False

def setup_linux_startup():
    """Setup auto-start on Linux."""
    try:
        # Get current directory
        bot_dir = os.getcwd()
        script_path = os.path.join(bot_dir, "dual_mode_bot.py")
        
        # Create systemd service
        service_content = f"""[Unit]
Description=Dual-Mode VRChat Bot
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'bot')}
WorkingDirectory={bot_dir}
ExecStart={sys.executable} {script_path}
Restart=always
RestartSec=10
Environment=PYTHONPATH={os.path.dirname(sys.executable)}

[Install]
WantedBy=multi-user.target
"""
        
        # Create service file
        service_path = "/etc/systemd/system/dualmode-vrchatbot.service"
        
        print(f"To setup Linux auto-start:")
        print(f"1. Create file: {service_path}")
        print("2. Copy the following content:")
        print("=" * 50)
        print(service_content)
        print("=" * 50)
        print("3. Run: sudo systemctl daemon-reload")
        print("4. Run: sudo systemctl enable dualmode-vrchatbot")
        print("5. Run: sudo systemctl start dualmode-vrchatbot")
        
        return True
        
    except Exception as e:
        print(f"❌ Linux startup setup failed: {e}")
        return False

def create_desktop_shortcut():
    """Create desktop shortcut for easy access."""
    system = platform.system().lower()
    
    if system == 'windows':
        # Create Windows shortcut
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "DualModeBot.lnk")
            target = sys.executable
            wDir = os.getcwd()
            icon = target
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.Arguments = f'"{os.path.join(wDir, "dual_mode_bot.py")}"'
            shortcut.WorkingDirectory = wDir
            shortcut.IconLocation = icon
            shortcut.save()
            
            print("✅ Desktop shortcut created")
            return True
            
        except ImportError:
            print("❌ Windows shortcut creation requires additional packages")
            return False
            
    elif system == 'linux':
        # Create Linux .desktop file
        desktop_dir = os.path.expanduser("~/.local/share/applications")
        os.makedirs(desktop_dir, exist_ok=True)
        
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Dual-Mode VRChat Bot
Comment=VRChat bot with system helper features
Exec={sys.executable} {os.path.join(os.getcwd(), "dual_mode_bot.py")}
Icon=applications-system
Terminal=true
Categories=System;Utility;
"""
        
        desktop_path = os.path.join(desktop_dir, "dualmode-vrchatbot.desktop")
        with open(desktop_path, 'w') as f:
            f.write(desktop_content)
        
        os.chmod(desktop_path, 0o755)
        print("✅ Desktop entry created")
        return True
        
    else:
        print(f"❌ Desktop shortcut not supported on {system}")
        return False

def check_startup_permissions():
    """Check if we have permissions for startup setup."""
    system = platform.system().lower()
    
    if system == 'linux':
        # Check if we can write to systemd directory
        return os.access('/etc/systemd/system/', os.W_OK)
    elif system == 'macos':
        # Check if we can write to LaunchAgents
        launch_agents = os.path.expanduser("~/Library/LaunchAgents")
        return os.access(launch_agents, os.W_OK)
    elif system == 'windows':
        # Check if we can write to registry
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_WRITE
            )
            winreg.CloseKey(key)
            return True
        except:
            return False
    
    return False

def main():
    """Main setup function."""
    print("Dual-Mode VRChat Bot - Startup Setup")
    print("=" * 40)
    
    system = platform.system()
    print(f"Detected system: {system}")
    
    # Check permissions
    if not check_startup_permissions():
        print("⚠️  Warning: Limited permissions for startup setup")
        print("Some features may require administrator privileges")
    
    # Create startup script
    print("\n1. Creating startup script...")
    script_path = create_startup_script()
    print(f"✅ Created: {script_path}")
    
    # Setup auto-start based on system
    print(f"\n2. Setting up auto-start for {system}...")
    
    success = False
    if system == 'Windows':
        success = setup_windows_startup()
    elif system == 'Darwin':  # macOS
        success = setup_macos_startup()
    elif system == 'Linux':
        success = setup_linux_startup()
    else:
        print(f"❌ Auto-start not supported on {system}")
    
    # Create desktop shortcut
    print("\n3. Creating desktop shortcut...")
    create_desktop_shortcut()
    
    # Create environment file if it doesn't exist
    env_file = os.path.join(os.getcwd(), '.env')
    if not os.path.exists(env_file):
        print("\n4. Creating .env file template...")
        env_content = """# Dual-Mode VRChat Bot Configuration
# Copy this file and fill in your credentials

# VRChat Account Credentials
VRCHAT_USERNAME=your_bot_username
VRCHAT_PASSWORD=your_bot_password
VRCHAT_2FA_CODE=your_2fa_code_if_enabled

# Bot Configuration
BOT_NAME=DualBot
BOT_PREFIX=!
DEFAULT_MODE=standby
AUTO_SWITCH_MODES=true
VRC_ACTIVE_HOURS=09:00-23:00

# System Helper Settings
ENABLE_DAILY_CLEANUP=true
ENABLE_WEEKLY_SCAN=true

# Resource Limits
MAX_MEMORY_MB=256
MAX_STORAGE_MB=100
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Created: {env_file}")
        print("⚠️  Please edit this file with your VRChat credentials")
    
    print("\n" + "=" * 40)
    print("Setup Summary:")
    print(f"✅ Startup script: {script_path}")
    print(f"{'✅' if success else '❌'} Auto-start: {'Configured' if success else 'Manual setup required'}")
    print("✅ Desktop shortcut: Available")
    print("✅ Environment file: Created")
    
    print("\nNext Steps:")
    print("1. Edit .env file with your VRChat credentials")
    print("2. Test the bot: python dual_mode_bot.py")
    print("3. If auto-start failed, follow the manual instructions above")
    
    if success:
        print("4. Reboot your system to test auto-start")
    
    print("\nBot will start in standby mode and automatically switch to VRChat mode during active hours.")

if __name__ == "__main__":
    main()
