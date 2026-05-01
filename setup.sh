#!/bin/bash

# SGP Project Setup Script for Mac/Linux

echo "===================================="
echo "SGP - Certificate System Setup"
echo "===================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo ""
echo "Step 1: Creating virtual environment..."
python3 -m venv venv

echo ""
echo "Step 2: Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Step 3: Upgrading pip..."
python -m pip install --upgrade pip

echo ""
echo "Step 4: Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Step 5: Creating directories..."
mkdir -p certificates
mkdir -p templates_upload

echo ""
echo "===================================="
echo "Setup Complete!"
echo "===================================="
echo ""
echo "To start the application:"
echo ""
echo "1. Activate virtual environment (if not already activated):"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the application:"
echo "   python backend/app.py"
echo ""
echo "The application will be available at http://localhost:5000"
echo ""
