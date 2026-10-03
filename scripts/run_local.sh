#!/usr/bin/env bash
set -e

echo "=================================================="
echo " Starting 'What do I tap?' Helper Locally"
echo "=================================================="

# check for python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python 3 is required."
    exit 1
fi

# create venv on first run
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment (.venv)..."
    python3 -m venv .venv
fi

echo "🔄 Activating virtual environment..."
source .venv/bin/activate

echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🎨 Ensuring demo assets are present..."
python generate_demo_assets.py

echo "🚀 Starting Gradio application..."
python app.py
