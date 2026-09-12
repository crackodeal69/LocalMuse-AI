@echo off
setlocal

cd /d "%~dp0.."
set "PROJECT_ROOT=%CD%"

echo Starting Forge API...
start "LocalMuse - Forge API" cmd /k call "%PROJECT_ROOT%\scripts\start_forge_api.bat"

echo Starting LocalMuse UI...
start "LocalMuse - UI" cmd /k call "%PROJECT_ROOT%\scripts\start_localmuse_ui.bat"

echo.
echo LocalMuse UI will be available at:
echo http://127.0.0.1:7861
echo.
echo Keep both windows open while using LocalMuse.
pause