#!/bin/bash

# Change to the repository root (where this script lives)
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

# macOS: remove Gatekeeper quarantine if present
if [ "$(uname)" = "Darwin" ]; then
    xattr -d com.apple.quarantine "$0" 2>/dev/null
fi

clear
echo "========================================="
echo "  GOOGLE MAPS SCRAPER v2.0"
echo "========================================="
echo ""
echo "Working directory: $REPO_DIR"
echo ""

# ---- Check Python ----
echo "[1/6] Checking Python..."
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

# ---- Check pip ----
echo "[2/6] Checking pip..."
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
echo "[3/6] Setting up virtual environment..."
if [ ! -d "$REPO_DIR/.venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    $PYTHON -m venv "$REPO_DIR/.venv" || {
        echo "[WARNING] Could not create venv, continuing without it..."
    }
fi

if [ -f "$REPO_DIR/.venv/bin/activate" ]; then
    echo "[OK] Activating virtual environment..."
    source "$REPO_DIR/.venv/bin/activate"
fi

# ---- Check Python dependencies ----
echo "[4/6] Checking Python dependencies..."
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
    $PYTHON -m pip install -r "$REPO_DIR/requirements.txt" \
    || $PYTHON -m pip install --user -r "$REPO_DIR/requirements.txt" \
    || {
        echo "[ERROR] Failed to install dependencies!"
        read -p "Press Enter to close..." -n 1
        exit 1
    }
    echo "[OK] Dependencies installed"
else
    echo "[OK] All Python dependencies installed"
fi

# ---- Check Playwright Chromium ----
echo "[5/6] Checking Chromium browser..."
CHROMIUM_FOUND=0

if [ "$(uname)" = "Darwin" ]; then
    for dir in "$HOME/Library/Caches/ms-playwright"/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium \
               "$HOME/Library/Caches/ms-playwright"/chromium-*/chrome-mac-*/Chromium.app/Contents/MacOS/Chromium; do
        if [ -x "$dir" ] 2>/dev/null; then
            CHROMIUM_FOUND=1
            echo "[OK] Playwright Chromium ready"
            break
        fi
    done
else
    for dir in "$HOME/.cache/ms-playwright"/chromium-*/chrome-linux/chrome; do
        if [ -x "$dir" ] 2>/dev/null; then
            CHROMIUM_FOUND=1
            echo "[OK] Playwright Chromium ready"
            break
        fi
    done
fi

if [ $CHROMIUM_FOUND -eq 0 ]; then
    echo ""
    echo "Installing Playwright Chromium browser (one-time, ~200 MB)..."
    $PYTHON -m playwright install chromium || {
        echo "[ERROR] Failed to install Chromium!"
        read -p "Press Enter to close..." -n 1
        exit 1
    }
    echo "[OK] Chromium installed"
fi

# ---- Check port ----
echo "[6/6] Checking port 5001..."
if command -v lsof &>/dev/null; then
    if lsof -i :5001 &>/dev/null; then
        echo ""
        echo "[WARNING] Port 5001 is already in use!"
        echo "The server may already be running. Open: http://localhost:5001"
        read -p "Press Enter to close..." -n 1
        exit 1
    fi
fi

# ---- Start server ----
echo ""
echo "========================================="
echo "  All checks passed!"
echo "========================================="
echo ""

if [ ! -f "$REPO_DIR/.gms_initialized" ]; then
    echo ""
    echo "╔══════════════════════════════════════════╗"
    echo "║  FIRST RUN - WELCOME!                   ║"
    echo "║                                          ║"
    echo "║  Your browser will open automatically.   ║"
    echo "║  1. Enter what you want to search for    ║"
    echo "║  2. Enter the cities to search in        ║"
    echo "║  3. Click \"Start Search\"                 ║"
    echo "║  4. Wait for results, then download CSV  ║"
    echo "║                                          ║"
    echo "║  Tip: After this, use GoogleMapsScraper  ║"
    echo "║  .app to launch without opening Terminal ║"
    echo "╚══════════════════════════════════════════╝"
    echo ""
    touch "$REPO_DIR/.gms_initialized"
fi

echo "Starting server..."
echo ""
echo "Interface available at:"
echo "   http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================="
echo ""

(sleep 3 && open "http://localhost:5001") &
cd "$REPO_DIR"
$PYTHON api_server.py

# Keep terminal open
echo ""
echo "Server stopped. Press any key to close..."
read -n 1
