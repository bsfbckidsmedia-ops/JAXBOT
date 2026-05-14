@echo off
cd /d %~dp0
if not exist "dist\JaxBot.exe" (
    echo Error: dist\JaxBot.exe not found.
    echo Run "python build_exe.py" or "python build_jaxbot.py" first.
    pause
    exit /b 1
)
echo Starting JaxBot Console...
"dist\JaxBot.exe"
pause
