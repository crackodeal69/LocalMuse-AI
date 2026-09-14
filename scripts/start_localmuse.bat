@echo off
setlocal

cd /d "%~dp0.."
set "PROJECT_ROOT=%CD%"

echo Starting LocalMuse in the system tray...
start "LocalMuse Tray" powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PROJECT_ROOT%\scripts\LocalMuseTray.ps1"

echo.
echo LocalMuse UI will be available at:
echo http://127.0.0.1:7861
echo.
echo Forge API: http://127.0.0.1:7860
echo Forge and LocalMuse UI are running in the system tray.
timeout /t 5 /nobreak >nul
