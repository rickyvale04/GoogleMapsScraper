@echo off
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

:: Attiva virtual environment se esiste
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

echo Starting server...
echo.
echo Interface available at:
echo   http://localhost:5001
echo.
echo Press Ctrl+C to stop the server
echo ==========================================
echo.

:: Avvia il server
python api_server.py

:: Se il server si ferma, tieni aperta la finestra
echo.
echo Server stopped.
pause
