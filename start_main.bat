@echo off
cd /d %~dp0
if not exist "dist\main.exe" (
    echo Error: dist\main.exe not found.
    echo Build may have failed or the executable is missing.
    pause
    exit /b 1
)
echo Starting VRChat main bot...
"dist\main.exe"
pause
