@echo off
setlocal

set "PROJECT_ROOT=%~dp0.."
set "KOHYA_ROOT=E:\ai_work\kohya_ss\sd-scripts"
set "PYTHON=E:\ai_work\kohya_ss\.venv\Scripts\python.exe"
set "CONFIG=%PROJECT_ROOT%\configs\lora_baseline_dataset_v01.toml"

if not exist "%PYTHON%" (
    echo ERROR: kohya Python was not found: %PYTHON%
    exit /b 1
)
if not exist "%CONFIG%" (
    echo ERROR: training config was not found: %CONFIG%
    exit /b 1
)

pushd "%KOHYA_ROOT%"
call "%~dp0..\scripts\_run_sdxl_training.bat"
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%