# Unix Socket Issue - Root Cause and Solution

## Problem Summary

The socket file `/tmp/label-generator.sock` was disappearing immediately after creation when using the `run_web_socket.py` script with uvicorn.

## Root Cause

**Uvicorn has a known issue/limitation with Unix sockets when using multiple workers.**

When uvicorn creates a Unix socket with workers > 1:
1. The socket is registered in the kernel (visible with `lsof` and `ss`)
2. But the socket file is NOT properly created in the filesystem
3. This makes it inaccessible to Nginx or other reverse proxies

Evidence:
```bash
# Socket visible in kernel
$ ss -xl | grep label
u_str LISTEN 0 2048 /tmp/label-generator.sock 2407874 * 0

# But not in filesystem
$ ls -la /tmp/label-generator.sock
ls: cannot access '/tmp/label-generator.sock': No such file or directory

# Cannot connect
$ curl --unix-socket /tmp/label-generator.sock http://localhost/
curl: (7) Failed to connect to localhost port 80: Could not connect to server
```

## Solution: Use Gunicorn Instead

**Gunicorn is the recommended production server for FastAPI/ASGI applications with Unix sockets.**

### New Script: `run_gunicorn_socket.py`

This script properly creates and manages Unix sockets using Gunicorn with uvicorn workers.

#### Usage:

```bash
# Default settings (4 workers)
python run_gunicorn_socket.py

# Custom workers
python run_gunicorn_socket.py --workers 2

# Custom socket path
python run_gunicorn_socket.py --socket /var/run/label-gen.sock

# Custom permissions (for Nginx compatibility)
python run_gunicorn_socket.py --mode 0o666

# Development mode with auto-reload
python run_gunicorn_socket.py --reload
```

### Verification:

```bash
# Start the server
python run_gunicorn_socket.py --workers 2

# Check socket exists (in another terminal)
ls -la /tmp/label-generator.sock
# Output: srw-rw-rw- 1 dinochlai dinochlai 0 Oct 6 11:03 /tmp/label-generator.sock

# Test connection
curl --unix-socket /tmp/label-generator.sock http://localhost/
# Output: HTML content from the application
```

## Comparison

### uvicorn (run_web_socket.py)
❌ Socket not accessible in filesystem with workers > 1
✅ Works with single worker only
❌ Not recommended for production with Unix sockets

### Gunicorn (run_gunicorn_socket.py)
✅ Socket properly created in filesystem
✅ Works with multiple workers
✅ Recommended for production
✅ Better process management
✅ Proper socket permission control

## Installation

Add to `requirements.txt`:
```
gunicorn>=23.0.0
```

Install:
```bash
pip install gunicorn
```

## Updated Systemd Service

Update `label-generator.service` to use Gunicorn:

```ini
[Service]
Type=simple
User=dinochlai
Group=dinochlai
WorkingDirectory=/home/dinochlai/excel-label-generate
Environment="PATH=/home/dinochlai/excel-label-generate/.venv/bin"
ExecStart=/home/dinochlai/excel-label-generate/.venv/bin/python /home/dinochlai/excel-label-generate/run_gunicorn_socket.py --socket /tmp/label-generator.sock --workers 4 --mode 0o666
```

## Testing Checklist

- [x] Socket file exists in filesystem: `ls -la /tmp/label-generator.sock`
- [x] Socket has correct permissions: `0o666` or `srw-rw-rw-`
- [x] Can connect via curl: `curl --unix-socket /tmp/label-generator.sock http://localhost/`
- [x] Works with multiple workers
- [x] Nginx can connect to the socket

## Nginx Configuration

No changes needed - same configuration works:

```nginx
upstream label_generator {
    server unix:/tmp/label-generator.sock fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://label_generator;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /home/dinochlai/excel-label-generate/static;
    }
}
```

## Recommendation

**Use `run_gunicorn_socket.py` for all production deployments with Unix sockets.**

Keep `run_web_socket.py` only for:
- Single worker scenarios
- Development/testing
- When you specifically need pure uvicorn features
