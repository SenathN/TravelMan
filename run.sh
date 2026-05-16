#!/bin/bash

# 1. Setup/Initialize venv
source ./setup_venv.sh

# 2. Check for tkinter
$VENV_PYTHON -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ WARNING: 'tkinter' (GUI library) is not found."
    echo "   To use the GUI, install it on your system:"
    echo "   - Linux (Ubuntu/Debian): sudo apt-get install python3-tk"
    echo "   - macOS: brew install python-tk"
    echo "   - Windows: Re-install Python and check 'tcl/tk and IDLE'"
    echo ""
    echo "🔄 Switching to CLI mode as a fallback..."
    echo ""
    $VENV_PYTHON cli.py
    exit 0
fi

# 3. Start the application
echo "🚀 Starting TravelMate AI Assistant (GUI)..."
$VENV_PYTHON main.py
