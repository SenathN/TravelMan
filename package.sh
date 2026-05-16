#!/bin/bash

# package.sh — TravelMate Packaging Script
# This script triggers the build process to generate a standalone Windows executable.

echo "🚀 Starting TravelMate Packaging Process..."

# Ensure python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed."
    exit 1
fi

# Install requirements if not already present
echo "📦 Ensuring dependencies are installed..."
pip install -r requirements.txt pyinstaller &> /dev/null

# Run the build script
echo "🛠️  Running build.py..."
python3 build.py "$@"

if [ $? -eq 0 ]; then
    echo "✅ Packaging complete! Check the 'dist' folder for the executable."
else
    echo "❌ Packaging failed. Check 'build.log' for details."
    exit 1
fi
