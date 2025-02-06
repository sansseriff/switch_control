#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to the backend directory
cd backend

# Create a local virtual environment using Python 3.12
uv venv --python 3.12

# Activate the virtual environment
source .venv/bin/activate


# Install dependencies from pyproject.toml
uv pip sync
