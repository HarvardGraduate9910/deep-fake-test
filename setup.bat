@echo off
REM Deep Fake Detector - Setup Script for Windows

setlocal enabledelayedexpansion

echo 🎭 Deep Fake Detector - Setup Script
echo ======================================
echo.

REM Check Python installation
echo 📌 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH.
    echo    Please install Python 3.8+ from https://python.org
    echo    Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found
echo.

REM Create virtual environment
echo 📌 Creating virtual environment...
if exist venv (
    echo ⚠️  Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    echo ✅ Virtual environment created
)
echo.

REM Activate virtual environment
echo 📌 Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated
echo.

REM Upgrade pip
echo 📌 Upgrading pip...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
echo ✅ pip upgraded
echo.

REM Install requirements
echo 📌 Installing dependencies...
echo    This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed
echo.

REM Create necessary directories
echo 📌 Creating necessary directories...
if not exist "backend\models" mkdir backend\models
if not exist "backend\utils" mkdir backend\utils
if not exist "logs" mkdir logs
if not exist "storage" mkdir storage
echo ✅ Directories created
echo.

REM Create .env file if it doesn't exist
echo 📌 Setting up environment variables...
if not exist ".env" (
    copy .env.example .env
    echo ✅ .env file created (customize as needed)
) else (
    echo ⚠️  .env file already exists
)
echo.

REM Test Flask import
echo 📌 Testing backend dependencies...
python -c "import flask; import cv2; import numpy; print('✅ All dependencies imported successfully')" 2>nul || (
    echo ⚠️  Some dependencies may not be fully installed
)
echo.

echo ======================================
echo ✅ Setup Complete!
echo.
echo 🚀 Next steps:
echo    1. If not already active: venv\Scripts\activate.bat
echo    2. Start backend: python backend\app.py
echo    3. Load extension in Chrome (chrome://extensions/)
echo    4. Start a video call and test
echo.
echo 📖 For more info, see README.md
echo.
pause
