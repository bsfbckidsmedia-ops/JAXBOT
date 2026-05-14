@echo off
cd /d %~dp0
echo JaxBot - VRChat ChatBox and TTS Standby Bot
echo.

if not exist "dist\JaxBot.exe" (
    echo dist\JaxBot.exe not found.
    echo.
    echo Build it first:
    echo   python build_exe.py
    echo   python build_jaxbot.py
    echo.
    pause
    exit /b 1
)

echo Starting JaxBot Console...
"dist\JaxBot.exe"
pause
