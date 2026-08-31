@echo off
setlocal

set VENV_DIR=%~dp0.venv
set PYTHON=%VENV_DIR%\Scripts\python.exe

if not exist "%PYTHON%" (
    echo [!] Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)

"%PYTHON%" "%~dp0server.py" %*
