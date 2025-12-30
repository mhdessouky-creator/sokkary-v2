#!/bin/bash

# setup_ai_agent.sh - Setup script for Termux Multi-Agent AI

echo "Starting setup for Termux Multi-Agent AI..."

# Update packages
echo "Updating package lists..."
pkg update -y && pkg upgrade -y

# Install Python and basic dependencies
echo "Installing Python and dependencies..."
pkg install python git clang build-essential libffi libxml2 libxslt -y

# Upgrade pip
python -m pip install --upgrade pip

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing requirements from requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Installing manually..."
    pip install python-dotenv g4f google-generativeai requests
fi

# Create directories if they don't exist
mkdir -p ai_agent/logs ai_agent/exports ai_agent/sandbox

echo "Setup complete! Don't forget to configure ai_agent/.env"
echo "To start the agent: python ai_agent/main.py"
