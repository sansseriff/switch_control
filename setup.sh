#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define colors
PURPLE='\033[0;35m'  # Changed from YELLOW to PURPLE with purple color code
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${PURPLE}This setup uses the UV python package manager to build a local portable python installation. Press 1 to continue with UV, or 2 to setup your python environment manually${NC}"
read -p "Enter your choice (1 or 2): " py_choice

if [ "$py_choice" = "1" ]; then
    # Check if uv is installed
    if ! command -v uv &> /dev/null; then
        echo "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
    else
        echo "uv is already installed"
    fi

    # Navigate to the backend directory
    cd backend

    # Create a local virtual environment using Python 3.13
    uv venv --python 3.13

    # Activate the virtual environment
    source .venv/bin/activate

    # Install dependencies from pyproject.toml
    uv sync
    
    # Return to the main directory
    cd ..
elif [ "$py_choice" = "2" ]; then
    echo "Please ensure you have Python 3.13+ installed and set up with the required packages."
    echo "You'll need to manually install dependencies listed in backend/pyproject.toml"
    read -p "Press Enter to continue with the rest of the setup..."
else
    echo "Invalid choice. Exiting..."
    exit 1
fi

echo "Setting up web assets..."
if ! command -v bun &> /dev/null; then
    echo "Installing Bun..."
    curl -fsSL https://bun.sh/install | bash
    export PATH="$HOME/.bun/bin:$PATH"
else
    echo "Bun is already installed"
fi

echo "Installing and building web assets..."
cd switch_control
bun install
bun run buildall
cd ..
echo "Web assets built successfully"

# Print colored instructions
GREEN='\033[0;32m'
NC='\033[0m' # No Color
echo -e "${GREEN}Setup complete! Do 'cd switch_control' and then either: ${NC}"
echo -e "${GREEN}1. Run the script with: sh run.sh${NC}"
echo -e "${GREEN}2. Run directly with uv: cd ./backend/backend && uv run main.py${NC}"
