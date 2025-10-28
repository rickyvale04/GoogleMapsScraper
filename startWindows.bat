@echo off
setlocal enabledelayedexpansion
color 0A
title Google Maps Scraper - Server

cls
echo ==========================================
echo   GOOGLE MAPS SCRAPER - SERVER
echo ==========================================
echo.

:: Vai nella directory dello script
cd /d "%~dp0"
echo Working directory: %CD%
echo.

:: Controlla se Python e' installato
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from python.org
    echo.
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

:: Controlla se requirements e' installato
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Flask not found. Installing dependencies...
    python -m pip install -r requirements.txt
    python -m playwright install chromium
    echo.
)

:: Attiva virtual environment se esiste
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
    echo.
)

:: Controlla se la porta 5001 e' gia' in uso
netstat -ano | findstr :5001 >nul
if not errorlevel 1 (
    color 0E
    echo WARNING: Port 5001 is already in use!
    echo Please close the other server or change the port.
    echo.
    pause
    exit /b 1
)

echo Starting server...
echo.
echo Interface available at:
echo   http://localhost:5001
echo.
echo Press Ctrl+C to stop the server
echo ==========================================
echo.

:: Apri il browser dopo 3 secondi
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5001"

:: Avvia il server
python api_server.py

:: Se il server si ferma
echo.
if errorlevel 1 (
    color 0C
    echo ERROR: Server crashed!
) else (
    color 0A
    echo Server stopped successfully.
)
echo.
pause
