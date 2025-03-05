#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
else
    echo "uv is already installed"
fi

# Navigate to the backend directory
cd backend

# Create a local virtual environment using Python 3.12
uv venv --python 3.13

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies from pyproject.toml
uv sync

# Web assets setup
cd ..
# Define colors
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Setting up web assets..."
echo 
echo -e "${YELLOW}Do you want to download pre-built html/javascript files for the user interface, or install the tooling to modify and build these files?${NC}"
echo -e "${YELLOW}1) Download pre-built files (faster, recommended for most users)${NC}"
echo -e "${YELLOW}2) Install tooling to modify and build web assets (for development)${NC}"

read -p "Enter your choice (1 or 2): " web_choice

# Create the target directory if it doesn't exist
mkdir -p ./backend/backend/switch_web

if [ "$web_choice" = "1" ]; then
    echo "Downloading pre-built web assets..."
    curl -L https://github.com/sansseriff/switch_control/releases/download/0.0.1/switch_web.zip -o switch_web.zip
    unzip -o switch_web.zip -d ./backend/backend/
    rm switch_web.zip
    echo "Web assets downloaded successfully"
elif [ "$web_choice" = "2" ]; then
    echo "Installing Bun for web development..."
    curl -fsSL https://bun.sh/install | bash
    export PATH="$HOME/.bun/bin:$PATH"  # Add Bun to PATH for this script
    
    echo "Installing and building web assets..."
    cd switch_control
    bun install
    bun run buildall
    cd ..
    echo "Web assets built successfully"
else
    echo "Invalid choice. Exiting..."
    exit 1
fi

# Print colored instructions
GREEN='\033[0;32m'
NC='\033[0m' # No Color
echo -e "${GREEN}Setup complete! Do 'cd switch_control' and the either: ${NC}"
echo -e "${GREEN}1. Run the script with: sh run.sh${NC}"
echo -e "${GREEN}2. Run directly with uv: cd ./backend/backend && uv run main.py${NC}"