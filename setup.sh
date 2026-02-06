#!/bin/bash

echo "🦙 llamabench - Installation Script"
echo "===================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"

# Check Docker
if command -v docker &> /dev/null; then
    echo "✓ Docker is installed"
else
    echo "⚠️  Docker not found - engine auto-setup will not work"
    echo "   Install Docker from: https://docs.docker.com/get-docker/"
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Make executable
chmod +x llamabench.py

echo ""
echo "✅ Installation complete!"
echo ""
echo "Try it out:"
echo "  python llamabench.py list-models"
echo "  python llamabench.py run --model llama-3.1-8b --engines llama.cpp,ollama"
echo ""
