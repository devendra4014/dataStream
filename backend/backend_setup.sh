#!/usr/bin/env bash

set -e

echo "======================================"
echo "Setting up Python backend"
echo "======================================"

# Initialize project if needed
if [ ! -f "pyproject.toml" ]; then
    echo "Initializing uv project..."
    uv init
fi

# Create virtual environment if needed
if [ ! -d ".venv" ]; then
    uv venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    uv add -r requirements.txt
else
    echo "requirements.txt not found. Skipping dependency installation."
fi

echo ""
echo "======================================"
echo "Backend setup completed"
echo "======================================"
echo ""
echo "Activate environment with:"
echo "source .venv/bin/activate"