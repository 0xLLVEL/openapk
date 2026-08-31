@echo off
setlocal

set VENV_DIR=%~dp0.venv
set PYTHON=%VENV_DIR%\Scripts\python.exe
set PIP=%VENV_DIR%\Scripts\pip.exe

echo ========================================
echo  Mobile Pentest MCP - Setup
echo ========================================
echo.

if not exist "%VENV_DIR%" (
    echo [*] Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [!] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [+] Virtual environment created
) else (
    echo [+] Virtual environment already exists
)

echo.
echo [*] Installing requirements...
"%PIP%" install -r "%~dp0requirements.txt" --quiet
if errorlevel 1 (
    echo [!] Failed to install requirements
    pause
    exit /b 1
)
echo [+] Requirements installed

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo To use: Run start.bat
echo.
pause
