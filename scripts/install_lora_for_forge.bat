@echo off
setlocal

set "PROJECT_ROOT=%~dp0.."
set "SOURCE_DIR=%PROJECT_ROOT%\models\lora"
if not defined LOCALMUSE_FORGE_LORA_DIR set "LOCALMUSE_FORGE_LORA_DIR=E:\ai_work\webui\models\Lora"
set "FORGE_DIR=%LOCALMUSE_FORGE_LORA_DIR%"
set "SOURCE=%~1"

if "%SOURCE%"=="" set "SOURCE=nag_person_dataset_v01-000005.safetensors"
if not exist "%SOURCE_DIR%\%SOURCE%" (
    echo ERROR: LoRA checkpoint was not found: %SOURCE_DIR%\%SOURCE%
    echo Available checkpoints:
    dir /b "%SOURCE_DIR%\*.safetensors"
    exit /b 1
)

if not exist "%FORGE_DIR%" mkdir "%FORGE_DIR%"
copy /Y "%SOURCE_DIR%\%SOURCE%" "%FORGE_DIR%\%SOURCE%" >nul
echo Installed %SOURCE% into %FORGE_DIR%
echo Select it in Forge under the LoRA browser.
