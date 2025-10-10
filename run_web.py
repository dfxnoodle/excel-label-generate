#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Runner script for the web version of the label generator.
"""

import sys
import os
import socket
import argparse
import uvicorn

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def get_local_ip():
    """Get the local IP address of the machine."""
    try:
        # Create a socket to get the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the Label Generator web application')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 8000)),
                        help='Port to run the server on (default: 8000 or PORT env var)')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='Host to bind to (default: 0.0.0.0 for network access)')
    parser.add_argument('--reload', action='store_true',
                        help='Enable auto-reload on code changes (for development)')
    args = parser.parse_args()
    
    local_ip = get_local_ip()
    
    print("=" * 70)
    print("🚀 Starting Label Generator Web Application...")
    print("=" * 70)
    print("\n📍 Access the application at:")
    print(f"   • Local:   http://localhost:{args.port}")
    print(f"   • Network: http://{local_ip}:{args.port}")
    print("\n💡 To access from other devices on your network:")
    print(f"   Use: http://{local_ip}:{args.port}")
    print(f"\n⚙️  Server Configuration:")
    print(f"   • Host: {args.host}")
    print(f"   • Port: {args.port}")
    print(f"   • Auto-reload: {'Enabled' if args.reload else 'Disabled'}")
    print(f"\n⚠️  Make sure your firewall allows connections on port {args.port}")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("\n💡 Usage examples:")
    print(f"   python run_web.py --port 5000")
    print(f"   python run_web.py --port 3000 --reload")
    print(f"   PORT=9000 python run_web.py")
    print("=" * 70)
    print()
    
    try:
        # When using reload, we need to pass the app as an import string
        if args.reload:
            # Pass as import string for reload to work properly
            uvicorn.run(
                "web_app:app",
                host=args.host,
                port=args.port,
                reload=True
            )
        else:
            # Import and pass the app object directly when not reloading
            from web_app import app
            print("✓ Application loaded successfully")
            uvicorn.run(
                app,
                host=args.host,
                port=args.port,
                reload=False
            )
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
