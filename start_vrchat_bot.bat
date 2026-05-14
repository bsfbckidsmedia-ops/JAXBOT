@echo off
cd /d %~dp0
echo VRChat Bot Startup
echo.






























:endgoto end"dist\minimal_main.exe"echo Running minimal bot...)    goto end    pause    echo Error: dist\minimal_main.exe not found.if not exist "dist\minimal_main.exe" (:minimalgoto end"dist\main.exe"echo Running main bot...)    goto end    pause    echo Error: dist\main.exe not found.if not exist "dist\main.exe" (:maingoto endpauseecho Invalid choice.if "%choice%"=="3" goto endif "%choice%"=="2" goto minimalif "%choice%"=="1" goto mainset /p choice=Enter choice: echo.echo 3) Exitecho 2) Run minimal bot (minimal_main.exe)echo 1) Run main bot (main.exe)