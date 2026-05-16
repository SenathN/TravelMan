#!/bin/bash

# setup_venv.sh - Shared virtual environment initialization for TravelMate

VENV_DIR="venv"

# Create/Verify venv
VENV_PYTHON="./$VENV_DIR/bin/python3"

# Check if venv is healthy
RECREATE_VENV=false
if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_PYTHON" ]; then
    RECREATE_VENV=true
else
    # Check if the python executable actually works (handles bad shebangs/paths)
    if ! "$VENV_PYTHON" -c "import sys; print(sys.prefix)" >/dev/null 2>&1; then
        RECREATE_VENV=true
    fi
fi

if [ "$RECREATE_VENV" = true ]; then
    echo "⚙️  Initializing/Repairing virtual environment..."
    rm -rf "$VENV_DIR"
    python3 -m venv "$VENV_DIR"
    
    # If pip is missing (common on some Debian/Ubuntu systems)
    if ! "$VENV_PYTHON" -m pip --version >/dev/null 2>&1; then
        echo "⚠️  Standard venv creation failed to include pip. Attempting manual pip installation..."
        python3 -m venv --without-pip "$VENV_DIR"
        curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        "$VENV_PYTHON" get-pip.py
        rm get-pip.py
    fi
    
    if ! "$VENV_PYTHON" -m pip --version >/dev/null 2>&1; then
        echo "❌ Error: Failed to create virtual environment with pip. Please install 'python3-venv' on your host system."
        exit 1
    fi
fi

# Install/Update requirements
echo "📦 Updating dependencies in venv..."
"$VENV_PYTHON" -m pip install --upgrade pip -q
"$VENV_PYTHON" -m pip install -q -r requirements.txt

# Export the python path to be used by other scripts
export VENV_PYTHON
export VENV_PIP="$VENV_PYTHON -m pip"
