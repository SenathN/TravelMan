#!/bin/bash

# Define venv directory
VENV_DIR="venv"

# 1. Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "⚙️ Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# 2. Install/Update requirements
echo "� Installing dependencies..."
./"$VENV_DIR"/bin/pip install -q -r requirements.txt

# 3. Check for tkinter
./"$VENV_DIR"/bin/python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ WARNING: 'tkinter' (GUI library) is not found."
    echo "   To use the GUI, install it on your system:"
    echo "   - Linux (Ubuntu/Debian): sudo apt-get install python3-tk"
    echo "   - macOS: brew install python-tk"
    echo "   - Windows: Re-install Python and check 'tcl/tk and IDLE'"
    echo ""
    echo "🔄 Switching to CLI mode as a fallback..."
    echo ""
    ./"$VENV_DIR"/bin/python3 cli.py
    exit 0
fi

# 4. Start the application
echo "� Starting TravelMate AI Assistant (GUI)..."
./"$VENV_DIR"/bin/python3 main.py
