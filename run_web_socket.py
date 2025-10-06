#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Runner script for the web version of the label generator using Unix socket.
This is useful for deployment with reverse proxies like Nginx or Apache.
"""

import sys
import os
import argparse
import uvicorn

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def ensure_socket_dir(socket_path):
    """Ensure the directory for the socket file exists."""
    socket_dir = os.path.dirname(socket_path)
    if socket_dir and not os.path.exists(socket_dir):
        os.makedirs(socket_dir, mode=0o755)
        print(f"✓ Created socket directory: {socket_dir}")
    
    # Remove existing socket file if it exists
    if os.path.exists(socket_path):
        os.remove(socket_path)
        print(f"✓ Removed existing socket file: {socket_path}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Run the Label Generator web application using Unix socket',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default socket path
  python run_web_socket.py

  # Custom socket path
  python run_web_socket.py --socket /tmp/label-generator.sock

  # With auto-reload for development
  python run_web_socket.py --reload

  # Custom socket with specific permissions
  python run_web_socket.py --socket /var/run/label-gen.sock --mode 0o666

Nginx configuration example:
  upstream label_generator {
      server unix:/tmp/label-generator.sock;
  }

  server {
      listen 80;
      server_name example.com;

      location / {
          proxy_pass http://label_generator;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      }

      location /static {
          alias /path/to/excel-label-generate/static;
      }
  }
        """
    )
    parser.add_argument('--socket', type=str, default='/tmp/label-generator.sock',
                        help='Path to Unix socket file (default: /tmp/label-generator.sock)')
    parser.add_argument('--mode', type=str, default='0o660',
                        help='Socket file permissions in octal format (default: 0o660)')
    parser.add_argument('--reload', action='store_true',
                        help='Enable auto-reload on code changes (for development)')
    parser.add_argument('--workers', type=int, default=1,
                        help='Number of worker processes (default: 1)')
    args = parser.parse_args()
    
    # Convert mode string to octal integer
    try:
        socket_mode = int(args.mode, 8) if isinstance(args.mode, str) else args.mode
    except ValueError:
        print(f"❌ Invalid mode format: {args.mode}")
        print("Use octal format like: 0o660, 0o666, 0o777")
        sys.exit(1)
    
    print("=" * 70)
    print("🚀 Starting Label Generator Web Application (Unix Socket Mode)...")
    print("=" * 70)
    print(f"\n📍 Socket Information:")
    print(f"   • Socket Path: {args.socket}")
    print(f"   • Permissions: {oct(socket_mode)}")
    print(f"\n⚙️  Server Configuration:")
    print(f"   • Workers: {args.workers}")
    print(f"   • Auto-reload: {'Enabled' if args.reload else 'Disabled'}")
    print(f"\n💡 Usage with Nginx:")
    print(f"   upstream label_generator {{")
    print(f"       server unix:{args.socket};")
    print(f"   }}")
    print(f"\n💡 Testing the socket:")
    print(f"   curl --unix-socket {args.socket} http://localhost/")
    print(f"\n🛑 Press Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    # Ensure socket directory exists and clean up old socket
    ensure_socket_dir(args.socket)
    
    try:
        # Import the app to verify it works
        from web_app import app
        print("✓ Application loaded successfully")
        print(f"✓ Starting server on Unix socket: {args.socket}")
        print()
        
        # Run uvicorn with Unix socket
        uvicorn.run(
            app,
            uds=args.socket,  # Unix Domain Socket
            reload=args.reload,
            workers=args.workers if not args.reload else 1,  # reload mode doesn't support workers
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except PermissionError as e:
        print(f"❌ Permission error: {e}")
        print(f"Make sure you have write access to: {os.path.dirname(args.socket)}")
        print(f"You may need to run with sudo or choose a different socket path")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
    finally:
        # Cleanup socket file on exit
        if os.path.exists(args.socket):
            try:
                os.remove(args.socket)
                print(f"\n✓ Cleaned up socket file: {args.socket}")
            except Exception as e:
                print(f"\n⚠️  Could not remove socket file: {e}")
