#!/bin/bash

# Enable strict mode
set -euo pipefail

# Configuration
ENV_NAME="anki-cards-env"
ENV_PATH="./$ENV_NAME"

# Cleanup function
cleanup() {
    if [ -d "$ENV_PATH" ]; then
        echo "Removing incomplete environment '$ENV_NAME'..."
        rm -rf "$ENV_PATH"
    fi
}
trap cleanup ERR  # Trigger cleanup only if an error occurs

# Find the default Python 3 binary
PYTHON_BIN=$(which python3)

# Check if Python 3 is available
if [ -z "$PYTHON_BIN" ]; then
    echo "Error: Python 3 is not installed!"
    exit 1
fi

# Ensure the venv module is available
if ! $PYTHON_BIN -m ensurepip --version &>/dev/null; then
    echo "Python venv module is not available. Installing..."
    sudo apt install -y python3-venv
fi

# Create the virtual environment if it doesn't exist
if [ ! -d "$ENV_PATH" ]; then
    echo "Creating virtual environment '$ENV_NAME'..."
    $PYTHON_BIN -m venv "$ENV_PATH"
    echo "Virtual environment created."
fi

# Disable trap after successful creation
trap - ERR

# Activate the virtual environment
echo "Activating virtual environment '$ENV_NAME'..."
# shellcheck disable=SC1091
source $ENV_PATH/bin/activate

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "No requirements.txt found. Skipping dependency installation."
fi

echo "Environment setup complete."

