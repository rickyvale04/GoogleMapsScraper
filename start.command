#!/bin/bash

# Vai nella directory dello script
cd "$(dirname "$0")"

clear
echo "========================================="
echo "  🗺️  GOOGLE MAPS SCRAPER - SERVER"
echo "========================================="
echo ""
echo "📂 Working directory: $(pwd)"
echo ""

# Attiva virtual environment se esiste
if [ -d ".venv" ]; then
    echo "🐍 Activating virtual environment..."
    source .venv/bin/activate
fi

echo "🚀 Starting server..."
echo ""
echo "📱 Interface available at:"
echo "   http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================="
echo ""

# Avvia il server
python3 api_server.py

# Tieni aperto il Terminal
echo ""
echo "Server stopped. Press any key to close..."
read -n 1
