#!/bin/bash

# Default port
PORT=${PORT:-8000}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --reload)
            RELOAD_FLAG="--reload"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--port PORT] [--reload]"
            exit 1
            ;;
    esac
done

# Get local IP address
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "======================================================================"
echo "🚀 Starting Label Generator Web Application..."
echo "======================================================================"
echo ""
echo "📍 Access the application at:"
echo "   • Local:   http://localhost:${PORT}"
echo "   • Network: http://${LOCAL_IP}:${PORT}"
echo ""
echo "💡 To access from other devices on your network:"
echo "   Use: http://${LOCAL_IP}:${PORT}"
echo ""
echo "⚠️  Make sure your firewall allows connections on port ${PORT}"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""
echo "💡 Usage examples:"
echo "   ./run_web.sh --port 5000"
echo "   PORT=3000 ./run_web.sh"
echo "   ./run_web.sh --port 9000 --reload"
echo "======================================================================"
echo ""

python3 run_web.py --port ${PORT} ${RELOAD_FLAG}