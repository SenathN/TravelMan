#!/bin/bash

# ==============================================================================
# TravelMate Windows Executable Build Script
# Target: Windows 10/11
# Environment: Fedora / Linux (with PyInstaller)
# ==============================================================================

# Exit on any error (Requirement 5)
set -e

# Configuration
APP_NAME="TravelMate"
ENTRY_POINT="main.py"
DIST_DIR="dist"
BUILD_DIR="build"
RESOURCES=("intents.json" "packages.json" "nltk_data")

# ANSI Color Codes
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting comprehensive build process for $APP_NAME.exe...${NC}"

# 1. Dependency Handling (Requirement 3)
echo -e "${BLUE}📦 Step 1: Handling dependencies...${NC}"
if ! command -v pyinstaller &> /dev/null; then
    echo -e "${RED}❌ Error: PyInstaller is not installed.${NC}"
    echo "   Please run: pip install pyinstaller"
    exit 1
fi

# Ensure requirements are met
echo "   Installing project requirements..."
pip install -r requirements.txt || { echo -e "${RED}❌ Failed to install requirements${NC}"; exit 1; }

# Pre-download NLTK data for bundling (Requirement 3)
echo "   Pre-downloading NLTK data for embedding..."
python3 -c "import nltk; import os; path=os.path.abspath('nltk_data'); os.makedirs(path, exist_ok=True); nltk.download('punkt', download_dir=path, quiet=True); nltk.download('wordnet', download_dir=path, quiet=True); nltk.download('omw-1.4', download_dir=path, quiet=True); nltk.download('stopwords', download_dir=path, quiet=True)" || { echo -e "${RED}❌ Failed to download NLTK data${NC}"; exit 1; }

# 2. Validation of Seeding Process (Requirement 4)
echo -e "${BLUE}✅ Step 2: Validating database seeding logic...${NC}"
python3 validate_db.py || { echo -e "${RED}❌ Database validation failed! Build aborted.${NC}"; exit 1; }

# 3. Build Configuration (Requirement 1 & 5)
echo -e "${BLUE}🏗️ Step 3: Compiling executable...${NC}"

# Clean previous builds
rm -rf "$DIST_DIR" "$BUILD_DIR"

# Check if we are running under Wine or if we should attempt a Linux build
# Note: PyInstaller does NOT cross-compile natively.
if command -v wine &> /dev/null; then
    echo -e "${BLUE}🍷 Wine detected! Checking for Windows Python inside Wine...${NC}"
    
    # Try to find python in wine
    if wine python --version &> /dev/null; then
        echo -e "${GREEN}✅ Windows Python found in Wine!${NC}"
        WINE_PYTHON="wine python"
        $WINE_PYTHON -m pip install pyinstaller -r requirements.txt
        PYINSTALLER_CMD="wine pyinstaller --noconfirm --onefile --windowed --name '$APP_NAME'"
    else
        echo -e "${RED}❌ Windows Python not found inside Wine prefix.${NC}"
        echo -e "${BLUE}💡 To install Python in Wine, run these commands:${NC}"
        echo "   1. wget https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe"
        echo "   2. wine python-3.12.3-amd64.exe /quiet PrependPath=1"
        echo "   3. wine python -m pip install --upgrade pip"
        echo "   Then run this script again."
        exit 1
    fi
else
    echo -e "${RED}⚠️ Wine not found. Building a Linux executable instead.${NC}"
    echo -e "${BLUE}💡 To generate a true Windows .exe on Fedora, please install Wine:${NC}"
    echo "   sudo dnf install wine"
    echo "   Then install Windows Python inside Wine and run this script again."
    PYINSTALLER_CMD="pyinstaller --noconfirm --onefile --windowed --name '$APP_NAME'"
fi

for res in "${RESOURCES[@]}"; do
    if [ -d "$res" ]; then
        # For directories, format is src:dest
        PYINSTALLER_CMD="$PYINSTALLER_CMD --add-data '$res:$res'"
    elif [ -f "$res" ]; then
        # For files, format is src:.
        PYINSTALLER_CMD="$PYINSTALLER_CMD --add-data '$res:.'"
    fi
done

PYINSTALLER_CMD="$PYINSTALLER_CMD '$ENTRY_POINT'"

echo "   Executing build command..."
eval $PYINSTALLER_CMD || { echo -e "${RED}❌ PyInstaller compilation failed!${NC}"; exit 1; }

# 4. Final Verification (Requirement 6)
echo -e "${BLUE}🏁 Step 4: Finalizing build...${NC}"
if [ -f "$DIST_DIR/$APP_NAME" ] || [ -f "$DIST_DIR/$APP_NAME.exe" ]; then
    echo -e "${GREEN}------------------------------------------------------------${NC}"
    echo -e "${GREEN}🎉 SUCCESS: $APP_NAME executable generated successfully!${NC}"
    echo -e "📂 Location: $(pwd)/$DIST_DIR/"
    echo -e "${GREEN}------------------------------------------------------------${NC}"
    echo -e "${BLUE}Note for Fedora Users:${NC}"
    echo "The generated file in '$DIST_DIR/' is a standalone executable."
    echo "To produce a native Windows .exe from Fedora, you should run this"
    echo "script using Wine: 'wine pyinstaller ...' or run it on a Windows host."
    echo "The code has been optimized to use private AppData folders on Windows."
else
    echo -e "${RED}❌ Error: Build completed but executable was not found.${NC}"
    exit 1
fi
