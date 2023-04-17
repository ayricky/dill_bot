#!/bin/bash

set -e

# Create a virtual environment
python3.11 -m venv .venv

# Activate the virtual environment and upgrade pip
source .venv/bin/activate
pip install --upgrade pip

# Install Poetry
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
pip install poetry

# Install dependencies using Poetry
poetry install

# Check if ~/secret/dill_do_bot.env exists and copy to .env
if [ -f ~/secret/dill_do_bot.env ]; then
    cp ~/secret/dill_do_bot.env .env
fi