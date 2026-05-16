#!/bin/bash

# run_tests.sh — Test runner for TravelMate

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}✈️  TravelMate Test Runner${NC}"
echo -e "============================================================"

# Check if venv exists
if [ -d "venv" ]; then
    PYTHON_BIN="venv/bin/python"
else
    PYTHON_BIN="python3"
fi

# 1. Run the Full Integration Test Suite
echo -e "\n${BLUE}${BOLD}Step 1: Running Integration Scenarios (full_test.py)${NC}"
$PYTHON_BIN full_test.py

# 2. Run all unit tests in the tests/ directory
# This uses Python's built-in unittest discovery to find and execute 
# all files matching 'test_*.py' inside the 'tests/' folder.
# These tests cover lower-level logic, database persistence, and security robustness.
echo -e "\n${BLUE}${BOLD}Step 2: Running Unit Tests (unittest discover)${NC}"
$PYTHON_BIN -m unittest discover -s tests -p "test_*.py"

echo -e "\n${BOLD}============================================================${NC}"
echo -e "${GREEN}${BOLD}Tests Completed!${NC}"
