#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Runner script for the web version of the label generator using Unix socket with Gunicorn.
This is the RECOMMENDED way for production deployment with reverse proxies like Nginx or Apache.
"""

import sys
import os
import argparse
import subprocess

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
        description='Run the Label Generator web application using Unix socket with Gunicorn',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default socket path
  python run_gunicorn_socket.py

  # Custom socket path
  python run_gunicorn_socket.py --socket /tmp/label-generator.sock

  # Production mode with 4 workers
  python run_gunicorn_socket.py --workers 4

  # Custom socket with specific permissions
  python run_gunicorn_socket.py --socket /var/run/label-gen.sock --mode 0o666

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
    parser.add_argument('--mode', type=str, default='0o666',
                        help='Socket file permissions in octal format (default: 0o666)')
    parser.add_argument('--workers', type=int, default=4,
                        help='Number of worker processes (default: 4)')
    parser.add_argument('--timeout', type=int, default=120,
                        help='Worker timeout in seconds (default: 120)')
    parser.add_argument('--reload', action='store_true',
                        help='Enable auto-reload on code changes (for development)')
    args = parser.parse_args()
    
    # Convert mode string to octal integer
    try:
        socket_mode = int(args.mode, 8) if isinstance(args.mode, str) else args.mode
    except ValueError:
        print(f"❌ Invalid mode format: {args.mode}")
        print("Use octal format like: 0o660, 0o666, 0o777")
        sys.exit(1)
    
    print("=" * 70)
    print("🚀 Starting Label Generator Web Application (Gunicorn + Unix Socket)...")
    print("=" * 70)
    print(f"\n📍 Socket Information:")
    print(f"   • Socket Path: {args.socket}")
    print(f"   • Permissions: {oct(socket_mode)}")
    print(f"\n⚙️  Server Configuration:")
    print(f"   • Workers: {args.workers}")
    print(f"   • Timeout: {args.timeout}s")
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
    
    # Check if gunicorn is installed
    try:
        import gunicorn
        print("✓ Gunicorn found")
    except ImportError:
        print("❌ Gunicorn not installed!")
        print("Install it with: pip install gunicorn")
        sys.exit(1)
    
    # Verify the app can be imported
    try:
        sys.path.insert(0, src_dir)
        from web_app import app
        print("✓ Application loaded successfully")
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    print(f"✓ Starting Gunicorn on Unix socket: {args.socket}")
    print()
    
    # Set PYTHONPATH so gunicorn workers can find our modules
    env = os.environ.copy()
    env['PYTHONPATH'] = src_dir
    
    # Build gunicorn command
    gunicorn_cmd = [
        'gunicorn',
        'src.web_app:app',
        '--bind', f'unix:{args.socket}',
        '--workers', str(args.workers),
        '--worker-class', 'uvicorn.workers.UvicornWorker',
        '--timeout', str(args.timeout),
        '--access-logfile', '-',
        '--error-logfile', '-',
        '--log-level', 'info',
    ]
    
    if args.reload:
        gunicorn_cmd.append('--reload')
    
    # Set umask to allow socket permission control
    old_umask = os.umask(0o000)
    
    try:
        # Run gunicorn
        process = subprocess.Popen(gunicorn_cmd, env=env)
        
        # Wait a moment for socket to be created
        import time
        time.sleep(2)
        
        # Set socket permissions if it exists
        if os.path.exists(args.socket):
            os.chmod(args.socket, socket_mode)
            print(f"✓ Set socket permissions to {oct(socket_mode)}")
        else:
            print(f"⚠️  Socket file not yet visible (this is normal, Gunicorn may still be starting)")
        
        # Wait for the process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Received shutdown signal...")
        process.terminate()
        process.wait()
    except Exception as e:
        print(f"❌ Error running server: {e}")
        sys.exit(1)
    finally:
        # Restore original umask
        os.umask(old_umask)
        
        # Cleanup socket file on exit
        if os.path.exists(args.socket):
            try:
                os.remove(args.socket)
                print(f"\n✓ Cleaned up socket file: {args.socket}")
            except Exception as e:
                print(f"\n⚠️  Could not remove socket file: {e}")
