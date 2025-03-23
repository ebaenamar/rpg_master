#!/bin/bash

# Activate the virtual environment
source rpg_venv/bin/activate

# Install Jupyter if not already installed
pip install jupyter

# Launch Jupyter Notebook
jupyter notebook
