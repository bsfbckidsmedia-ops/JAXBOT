@echo off
cd /d %~dp0
if not exist "dist\minimal_main.exe" (
    echo Error: dist\minimal_main.exe not found.
    echo Build may have failed or the executable is missing.
    pause
    exit /b 1
)
echo Starting VRChat minimal bot...
"dist\minimal_main.exe"
pause
