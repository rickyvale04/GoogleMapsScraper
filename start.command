#!/bin/bash

# Vai nella directory dello script
cd "$(dirname "$0")"

clear
echo "========================================="
echo "  GOOGLE MAPS SCRAPER - SERVER"
echo "========================================="
echo ""
echo "Working directory: $(pwd)"
echo ""

# ---- Controllo Python ----
echo "Checking prerequisites..."
echo ""

if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "[ERROR] Python not found!"
    echo "Please install Python 3.8+ from https://www.python.org/downloads/"
    echo ""
    echo "  macOS:   brew install python3"
    echo "  Ubuntu:  sudo apt install python3 python3-pip python3-venv"
    echo ""
    read -p "Press Enter to close..." -n 1
    exit 1
fi

PY_VERSION=$($PYTHON --version 2>&1)
echo "[OK] $PY_VERSION"

# ---- Controllo pip ----
if ! $PYTHON -m pip --version &>/dev/null; then
    echo "[ERROR] pip not found!"
    echo "Installing pip..."
    $PYTHON -m ensurepip --upgrade 2>/dev/null || {
        echo "Failed to install pip automatically."
        echo "Please install pip manually: https://pip.pypa.io/en/stable/installation/"
        read -p "Press Enter to close..." -n 1
        exit 1
    }
fi
echo "[OK] pip available"

# ---- Virtual environment ----
if [ ! -d ".venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    $PYTHON -m venv .venv || {
        echo "[WARNING] Could not create venv, continuing without it..."
    }
fi

if [ -d ".venv" ]; then
    echo "[OK] Activating virtual environment..."
    source .venv/bin/activate
fi

# ---- Controllo dipendenze Python ----
MISSING=0
for pkg in flask playwright pandas openpyxl numpy; do
    if ! $PYTHON -c "import $pkg" &>/dev/null; then
        MISSING=1
        break
    fi
done

if [ $MISSING -eq 1 ]; then
    echo ""
    echo "Installing Python dependencies..."
    $PYTHON -m pip install -r requirements.txt || {
        echo "[ERROR] Failed to install dependencies!"
        read -p "Press Enter to close..." -n 1
        exit 1
    }
    echo "[OK] Dependencies installed"
else
    echo "[OK] All Python dependencies installed"
fi

# ---- Controllo Playwright Chromium ----
if ! $PYTHON -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(headless=True); b.close(); p.stop()" &>/dev/null 2>&1; then
    echo ""
    echo "Installing Playwright Chromium browser..."
    $PYTHON -m playwright install chromium || {
        echo "[ERROR] Failed to install Chromium!"
        read -p "Press Enter to close..." -n 1
        exit 1
    }
    echo "[OK] Chromium installed"
else
    echo "[OK] Playwright Chromium ready"
fi

# ---- Controllo porta ----
if command -v lsof &>/dev/null; then
    if lsof -i :5001 &>/dev/null; then
        echo ""
        echo "[WARNING] Port 5001 is already in use!"
        echo "Please close the other server or change the port."
        read -p "Press Enter to close..." -n 1
        exit 1
    fi
fi

# ---- Avvio server ----
echo ""
echo "========================================="
echo "  All checks passed!"
echo "========================================="
echo ""
echo "Starting server..."
echo ""
echo "Interface available at:"
echo "   http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================="
echo ""

$PYTHON api_server.py

# Tieni aperto il Terminal
echo ""
echo "Server stopped. Press any key to close..."
read -n 1
