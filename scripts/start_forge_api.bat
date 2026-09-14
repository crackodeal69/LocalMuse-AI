@echo off
setlocal

if not defined LOCALMUSE_FORGE_ROOT set "LOCALMUSE_FORGE_ROOT=E:\ai_work\webui"
if exist "%LOCALMUSE_FORGE_ROOT%\..\environment.bat" call "%LOCALMUSE_FORGE_ROOT%\..\environment.bat"
cd /d "%LOCALMUSE_FORGE_ROOT%"
set COMMANDLINE_ARGS=--api --nowebui
call webui.bat
