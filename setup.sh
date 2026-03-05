#!/bin/bash

# Deep Fake Detector - Setup Script for macOS/Linux

set -e

echo "🎭 Deep Fake Detector - Setup Script"
echo "======================================"
echo ""

# Check Python installation
echo "📌 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "📌 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "📌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "📌 Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null
echo "✅ pip upgraded"
echo ""

# Install requirements
echo "📌 Installing dependencies..."
echo "   This may take a few minutes..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create necessary directories
echo "📌 Creating necessary directories..."
mkdir -p backend/models
mkdir -p backend/utils
mkdir -p logs
mkdir -p storage
echo "✅ Directories created"
echo ""

# Create .env file if it doesn't exist
echo "📌 Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env file created (customize as needed)"
else
    echo "⚠️  .env file already exists"
fi
echo ""

# Test Flask import
echo "📌 Testing backend dependencies..."
python -c "import flask; import cv2; import numpy; print('✅ All dependencies imported successfully')" 2>/dev/null || {
    echo "⚠️  Some dependencies may not be fully installed"
}
echo ""

echo "======================================"
echo "✅ Setup Complete!"
echo ""
echo "🚀 Next steps:"
echo "   1. Activate environment: source venv/bin/activate"
echo "   2. Start backend: python backend/app.py"
echo "   3. Load extension in Chrome (chrome://extensions/)"
echo "   4. Start a video call and test"
echo ""
echo "📖 For more info, see README.md"
echo ""
