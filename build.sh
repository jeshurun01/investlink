#!/usr/bin/env bash
# Build script for Render

set -o errexit

# Install uv if not present
pip install uv

# Install dependencies with uv (much faster than pip)
uv pip install -r requirements.txt --system

# Collect static files
uv run manage.py collectstatic --no-input

# Run migrations
uv run manage.py migrate
