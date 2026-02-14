@echo off
setlocal enabledelayedexpansion
color 0A
title Google Maps Scraper - Server

cls
echo ==========================================
echo   GOOGLE MAPS SCRAPER v1.0
echo ==========================================
echo.

:: Change to script directory
cd /d "%~dp0"
echo Working directory: %CD%
echo.

:: ---- Check Python ----
echo [1/6] Checking Python...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        color 0C
        echo [ERROR] Python not found!
        echo Please install Python 3.8+ from https://www.python.org/downloads/
        echo.
        echo Make sure to check "Add Python to PATH" during installation.
        echo.
        pause
        exit /b 1
    )
    set PYTHON=python3
) else (
    set PYTHON=python
)

for /f "tokens=*" %%i in ('%PYTHON% --version 2^>^&1') do set PY_VERSION=%%i
echo [OK] %PY_VERSION%

:: ---- Check pip ----
echo [2/6] Checking pip...
%PYTHON% -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip not found! Installing pip...
    %PYTHON% -m ensurepip --upgrade >nul 2>&1
    if errorlevel 1 (
        echo Failed to install pip automatically.
        echo Please reinstall Python with pip enabled.
        pause
        exit /b 1
    )
)
echo [OK] pip available

:: ---- Virtual environment ----
echo [3/6] Setting up virtual environment...
if not exist ".venv" (
    echo.
    echo Creating virtual environment...
    %PYTHON% -m venv .venv
    if errorlevel 1 (
        echo [WARNING] Could not create venv, continuing without it...
    )
)

if exist ".venv\Scripts\activate.bat" (
    echo [OK] Activating virtual environment...
    call .venv\Scripts\activate.bat
)

:: ---- Check Python dependencies ----
echo [4/6] Checking Python dependencies...
set MISSING=0
for %%p in (flask playwright pandas openpyxl numpy) do (
    %PYTHON% -c "import %%p" >nul 2>&1
    if errorlevel 1 set MISSING=1
)

if !MISSING! equ 1 (
    echo.
    echo Installing Python dependencies...
    %PYTHON% -m pip install -r requirements.txt
    if errorlevel 1 (
        color 0C
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] All Python dependencies installed
)

:: ---- Check Playwright Chromium ----
echo [5/6] Checking Chromium browser...
:: Check if any Chromium binary exists in Playwright cache
set CHROMIUM_FOUND=0
for /d %%d in ("%LOCALAPPDATA%\ms-playwright\chromium-*") do (
    if exist "%%d\chrome-win\chrome.exe" (
        set CHROMIUM_FOUND=1
        echo [OK] Playwright Chromium ready ^(%%d^)
    )
)

if !CHROMIUM_FOUND! equ 0 (
    echo.
    echo Installing Playwright Chromium browser...
    %PYTHON% -m playwright install chromium
    if errorlevel 1 (
        color 0C
        echo [ERROR] Failed to install Chromium!
        pause
        exit /b 1
    )
    echo [OK] Chromium installed
)

:: ---- Check port ----
echo [6/6] Checking port 5001...
netstat -ano | findstr :5001 >nul
if not errorlevel 1 (
    color 0E
    echo.
    echo [WARNING] Port 5001 is already in use!
    echo Please close the other server or change the port.
    echo.
    pause
    exit /b 1
)

:: ---- Start server ----
echo.
echo ==========================================
echo   All checks passed!
echo ==========================================
echo.

if not exist ".gms_initialized" (
    echo.
    echo ========================================
    echo   FIRST RUN - WELCOME!
    echo.
    echo   Your browser will open automatically.
    echo   1. Enter what you want to search for
    echo   2. Enter the cities to search in
    echo   3. Click "Start Search"
    echo   4. Wait for results, then download CSV
    echo.
    echo   Tip: Click "How It Works" in the web
    echo   interface for a full guide.
    echo ========================================
    echo.
    echo. > .gms_initialized
)

echo Starting server...
echo.
echo Interface available at:
echo   http://localhost:5001
echo.
echo Press Ctrl+C to stop the server
echo ==========================================
echo.

:: Open browser after 3 seconds
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5001"

:: Start the server
%PYTHON% api_server.py

:: If server stops
echo.
if errorlevel 1 (
    color 0C
    echo [ERROR] Server crashed!
) else (
    color 0A
    echo Server stopped successfully.
)
echo.
pause
