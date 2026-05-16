#!/bin/bash

# Define venv directory
VENV_DIR="venv"

# 1. Create/Verify venv
if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/python3" ] || [ ! -f "$VENV_DIR/bin/pip" ]; then
    echo "⚙️ Creating/Repairing virtual environment..."
    rm -rf "$VENV_DIR"
    
    # Try standard venv creation
    python3 -m venv "$VENV_DIR" 2>/dev/null
    
    # If pip is missing (common on some Debian/Ubuntu systems without python3-venv fully installed)
    if [ ! -f "$VENV_DIR/bin/pip" ]; then
        echo "⚠️ standard venv creation failed to include pip. Attempting manual pip installation..."
        python3 -m venv --without-pip "$VENV_DIR"
        curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        ./"$VENV_DIR"/bin/python3 get-pip.py
        rm get-pip.py
    fi
    
    if [ ! -f "$VENV_DIR/bin/pip" ]; then
        echo "❌ Error: Failed to create virtual environment with pip."
        exit 1
    fi
fi

# 2. Install/Update requirements
echo "📦 Installing dependencies..."
./"$VENV_DIR"/bin/pip install --upgrade pip -q
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
echo "🚀 Starting TravelMate AI Assistant (GUI)..."
./"$VENV_DIR"/bin/python3 main.py
