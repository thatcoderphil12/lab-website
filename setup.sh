#!/bin/bash

# Exit immediately if a command fails
set -e

APP_DIR=~/lab-website/app
VENV_DIR="$APP_DIR/venv"

# Navigate to the app directory
cd "$APP_DIR" || { echo "Directory $APP_DIR not found."; exit 1; }

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "requirements.txt not found in $APP_DIR"
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Setup complete! Virtual environment is located at $VENV_DIR"
echo "To activate it in the future, run: source $VENV_DIR/bin/activate"
