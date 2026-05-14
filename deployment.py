#!/usr/bin/env python3
"""
VRChat Bot Deployment Script
Handles deployment and service setup for autonomous operation.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def create_systemd_service():
    """Create a systemd service file for Linux deployment."""
    service_content = """[Unit]
Description=VRChat Bot Service
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={working_dir}
ExecStart={exec_start}
Restart=always
RestartSec=10
Environment=PYTHONPATH={python_path}

[Install]
WantedBy=multi-user.target
""".format(
        user=os.getenv('USER', 'vrchatbot'),
        working_dir=os.getcwd(),
        exec_start=f"{sys.executable} {os.path.join(os.getcwd(), 'main.py')}",
        python_path=os.path.dirname(sys.executable)
    )
    
    service_path = "/etc/systemd/system/vrchat-bot.service"
    
    print(f"To install as systemd service:")
    print(f"1. Copy the following to {service_path}:")
    print("=" * 50)
    print(service_content)
    print("=" * 50)
    print(f"2. Run: sudo systemctl daemon-reload")
    print(f"3. Run: sudo systemctl enable vrchat-bot")
    print(f"4. Run: sudo systemctl start vrchat-bot")
    print(f"5. Check status: sudo systemctl status vrchat-bot")

def create_launchd_plist():
    """Create a launchd plist file for macOS deployment."""
    plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.vrchat.bot</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{working_dir}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{working_dir}/bot.log</string>
    <key>StandardErrorPath</key>
    <string>{working_dir}/bot.error.log</string>
</dict>
</plist>
""".format(
        python_path=sys.executable,
        script_path=os.path.join(os.getcwd(), 'main.py'),
        working_dir=os.getcwd()
    )
    
    plist_path = os.path.expanduser("~/Library/LaunchAgents/com.vrchat.bot.plist")
    
    print(f"To install as launchd service on macOS:")
    print(f"1. Create file: {plist_path}")
    print("=" * 50)
    print(plist_content)
    print("=" * 50)
    print(f"2. Run: launchctl load {plist_path}")
    print(f"3. Check status: launchctl list | grep com.vrchat.bot")
    print(f"4. To stop: launchctl unload {plist_path}")

def create_windows_service():
    """Create instructions for Windows service deployment."""
    print(f"To install as Windows service:")
    print(f"1. Install NSSM (Non-Sucking Service Manager)")
    print(f"2. Run: nssm install VRChatBot \"{sys.executable}\" \"{os.path.join(os.getcwd(), 'main.py')}\"")
    print(f"3. Set working directory in NSSM to: {os.getcwd()}")
    print(f"4. Start service: net start VRChatBot")
    print(f"5. Stop service: net stop VRChatBot")

def create_docker_deployment():
    """Create Docker deployment files."""
    dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 botuser
USER botuser

# Expose port (if needed for web interface)
EXPOSE 8080

# Command to run the bot
CMD ["python", "main.py"]
"""

    docker_compose_content = """version: '3.8'

services:
  vrchat-bot:
    build: .
    restart: unless-stopped
    environment:
      - VRCHAT_USERNAME=${VRCHAT_USERNAME}
      - VRCHAT_PASSWORD=${VRCHAT_PASSWORD}
      - VRCHAT_2FA_CODE=${VRCHAT_2FA_CODE}
      - BOT_NAME=${BOT_NAME:-VRChatBot}
      - BOT_PREFIX=${BOT_PREFIX:-!}
      - BOT_STATUS=${BOT_STATUS:-Hello! I'm a VRChat assistant bot.}
      - MAX_REQUESTS_PER_MINUTE=${MAX_REQUESTS_PER_MINUTE:-1}
      - AUTO_RECONNECT=${AUTO_RECONNECT:-true}
      - RESPONSE_DELAY=${RESPONSE_DELAY:-2.0}
    volumes:
      - ./bot.log:/app/bot.log
      - ./config.yaml:/app/config.yaml
"""

    # Write Docker files
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
        
    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose_content)
        
    print("Created Docker deployment files:")
    print("- Dockerfile")
    print("- docker-compose.yml")
    print("\nTo deploy with Docker:")
    print("1. Ensure .env file is configured")
    print("2. Run: docker-compose up -d")
    print("3. Check logs: docker-compose logs -f")

def setup_monitoring():
    """Setup monitoring and health checks."""
    health_check_script = """#!/bin/bash
# Health check script for VRChat bot

BOT_PID=$(pgrep -f "python.*main.py")
if [ -z "$BOT_PID" ]; then
    echo "Bot is not running"
    exit 1
fi

# Check if bot is responsive (would need to implement health check endpoint)
echo "Bot is running with PID: $BOT_PID"
exit 0
"""

    with open('health_check.sh', 'w') as f:
        f.write(health_check_script)
        
    os.chmod('health_check.sh', 0o755)
    
    print("Created health_check.sh for monitoring")

def main():
    """Main deployment setup."""
    print("VRChat Bot Deployment Setup")
    print("=" * 40)
    
    # Create deployment directory
    deploy_dir = Path("deployment")
    deploy_dir.mkdir(exist_ok=True)
    os.chdir(deploy_dir)
    
    system = platform.system().lower()
    
    print(f"\nDetected system: {system}")
    print("\nChoose deployment method:")
    print("1. System service (Linux/macOS/Windows)")
    print("2. Docker container")
    print("3. Manual setup")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        if system == "linux":
            create_systemd_service()
        elif system == "darwin":
            create_launchd_plist()
        elif system == "windows":
            create_windows_service()
        else:
            print(f"Unsupported system for service deployment: {system}")
            
    elif choice == "2":
        create_docker_deployment()
        
    elif choice == "3":
        print("\nManual setup instructions:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Configure .env file with your credentials")
        print("3. Run: python main.py")
        print("4. For background execution, use: nohup python main.py > bot.log 2>&1 &")
        
    else:
        print("Invalid choice")
        return
        
    # Setup monitoring
    setup_monitoring()
    
    print("\nDeployment setup complete!")
    print("Remember to:")
    print("- Configure your .env file with VRChat credentials")
    print("- Test the bot manually before deploying as service")
    print("- Monitor logs for any issues")

if __name__ == "__main__":
    main()
