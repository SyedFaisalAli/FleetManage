#!/bin/bash
# Install the Network Diagnostics MCP Server in development mode

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install the package in development mode
echo "Installing package in development mode..."
pip install -e .

# Make the server script executable
chmod +x network_diagnostics_server/server.py

echo "Installation complete!"
echo "You can run the server with: network-diagnostics-mcp"
echo "Or directly with: python -m network_diagnostics_server.server"