#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to the backend directory
cd backend

# Create a local virtual environment using Python 3.12
uv venv --python 3.13

# Activate the virtual environment
source .venv/bin/activate


# Install dependencies from pyproject.toml
uv sync

# Print colored instructions
GREEN='\033[0;32m'
NC='\033[0m' # No Color
echo -e "${GREEN}Setup complete! Do 'cd switch_control' and the either: ${NC}"
echo -e "${GREEN}1. Run the script with: sh run.sh${NC}"
echo -e "${GREEN}2. Run directly with uv: cd ./backend/backend && uv run main.py${NC}"


