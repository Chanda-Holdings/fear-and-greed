#!/bin/bash
# Setup script for the fear-and-greed project

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Set up pre-commit hooks
pre-commit install
