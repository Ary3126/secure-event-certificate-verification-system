@echo off
REM SGP Project Setup Script for Windows

echo ====================================
echo SGP - Certificate System Setup
echo ====================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org
    pause
    exit /b 1
)

echo.
echo Step 1: Creating virtual environment...
python -m venv venv

echo.
echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 3: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 4: Installing dependencies...
pip install -r requirements.txt

echo.
echo Step 5: Creating directories...
if not exist certificates mkdir certificates
if not exist templates_upload mkdir templates_upload

echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo To start the application:
echo.
echo 1. Activate virtual environment (if not already activated):
echo    venv\Scripts\activate.bat
echo.
echo 2. Run the application:
echo    python backend/app.py
echo.
echo The application will be available at http://localhost:5000
echo.
pause
