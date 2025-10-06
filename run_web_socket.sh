#!/bin/bash
# Shell script to run the web application using Unix socket

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# Default socket path
SOCKET_PATH="${SOCKET_PATH:-/tmp/label-generator.sock}"

# Run the application
python run_web_socket.py --socket "$SOCKET_PATH" "$@"
