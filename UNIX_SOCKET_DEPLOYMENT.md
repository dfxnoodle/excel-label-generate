# Unix Socket Deployment Guide

This guide explains how to deploy the Label Generator web application using Unix sockets with Nginx as a reverse proxy.

## Overview

Using Unix sockets instead of TCP ports provides:
- Better performance for local communication
- Improved security (no network exposure)
- Simpler configuration with reverse proxies
- No port conflicts

## Quick Start

### 1. Run with Default Settings

```bash
# Using Python script directly
source .venv/bin/activate
python run_web_socket.py

# Or using the shell script
./run_web_socket.sh
```

This will create a socket at `/tmp/label-generator.sock`

### 2. Run with Custom Socket Path

```bash
python run_web_socket.py --socket /var/run/label-generator.sock
```

### 3. Run with Multiple Workers (Production)

```bash
python run_web_socket.py --workers 4
```

## Command Line Options

```
--socket PATH       Path to Unix socket file (default: /tmp/label-generator.sock)
--mode MODE         Socket file permissions in octal (default: 0o660)
--reload            Enable auto-reload for development
--workers N         Number of worker processes (default: 1)
```

### Examples

```bash
# Development mode with auto-reload
python run_web_socket.py --reload

# Production mode with 4 workers
python run_web_socket.py --workers 4 --socket /var/run/label-gen.sock

# Custom permissions (accessible by all users)
python run_web_socket.py --mode 0o666
```

## Nginx Configuration

### 1. Install Nginx

```bash
sudo apt update
sudo apt install nginx
```

### 2. Configure Nginx

Create a new site configuration:

```bash
sudo nano /etc/nginx/sites-available/label-generator
```

Use the provided `nginx.conf.example` as a template, or copy this minimal configuration:

```nginx
upstream label_generator {
    server unix:/tmp/label-generator.sock fail_timeout=0;
}

server {
    listen 80;
    server_name label-generator.yourdomain.com;
    
    client_max_body_size 50M;
    
    location /static {
        alias /path/to/excel-label-generate/static;
    }
    
    location / {
        proxy_pass http://label_generator;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Important**: Replace `/path/to/excel-label-generate` with your actual installation path!

### 3. Enable the Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/label-generator /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## Systemd Service (Running as a Service)

### 1. Configure the Service File

Edit `label-generator.service` and update these paths:
- `WorkingDirectory=/path/to/excel-label-generate`
- `Environment="PATH=/path/to/excel-label-generate/.venv/bin"`
- `ExecStart=/path/to/excel-label-generate/.venv/bin/python ...`

Also set the appropriate user/group (e.g., `www-data` or your username).

### 2. Install and Enable the Service

```bash
# Copy service file
sudo cp label-generator.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable label-generator

# Start the service
sudo systemctl start label-generator

# Check status
sudo systemctl status label-generator
```

### 3. Service Management Commands

```bash
# Start service
sudo systemctl start label-generator

# Stop service
sudo systemctl stop label-generator

# Restart service
sudo systemctl restart label-generator

# View logs
sudo journalctl -u label-generator -f

# View recent logs
sudo journalctl -u label-generator -n 100
```

## Testing the Setup

### 1. Test the Socket Directly

```bash
# Using curl with Unix socket
curl --unix-socket /tmp/label-generator.sock http://localhost/

# Should return HTML from the application
```

### 2. Test Through Nginx

```bash
# Test locally
curl http://localhost/

# Test from another machine (replace with your server IP)
curl http://192.168.1.100/
```

### 3. Access in Browser

Open your browser and navigate to:
- Local: `http://localhost/`
- Domain: `http://label-generator.yourdomain.com/`

## Security Considerations

### 1. Socket Permissions

Default permissions (0o660) allow only the owner and group to access the socket.

```bash
# More restrictive (owner only)
python run_web_socket.py --mode 0o600

# More permissive (all users can access)
python run_web_socket.py --mode 0o666
```

### 2. User and Group

Make sure the Nginx user can access the socket:

```bash
# Check Nginx user
ps aux | grep nginx

# Common users: www-data (Debian/Ubuntu), nginx (CentOS/RHEL)
```

Set the service to run as the same user or add Nginx user to the app's group.

### 3. Firewall

If using a firewall, allow HTTP/HTTPS:

```bash
# UFW (Ubuntu)
sudo ufw allow 'Nginx Full'

# Firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## SSL/HTTPS Setup (Recommended for Production)

### Using Let's Encrypt (Free SSL)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate (interactive)
sudo certbot --nginx -d label-generator.yourdomain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

Certbot will automatically modify your Nginx configuration to use HTTPS.

## Troubleshooting

### Socket Permission Denied

```bash
# Check socket permissions
ls -la /tmp/label-generator.sock

# Fix permissions
chmod 660 /tmp/label-generator.sock

# Or run with more open permissions
python run_web_socket.py --mode 0o666
```

### Socket Already in Use

```bash
# Remove old socket file
rm /tmp/label-generator.sock

# Or the script will auto-remove it on start
```

### Nginx Cannot Connect

```bash
# Check if app is running
ps aux | grep "run_web_socket"

# Check socket exists
ls -la /tmp/label-generator.sock

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check Nginx user can access socket directory
sudo -u www-data ls -la /tmp/label-generator.sock
```

### Service Won't Start

```bash
# Check service status
sudo systemctl status label-generator

# View detailed logs
sudo journalctl -u label-generator -n 50

# Check if virtual environment exists
ls -la /path/to/excel-label-generate/.venv/

# Check if dependencies are installed
source .venv/bin/activate
pip list
```

## Performance Tuning

### Worker Processes

Adjust based on CPU cores:

```bash
# Check CPU cores
nproc

# Use 2x CPU cores for CPU-bound tasks
python run_web_socket.py --workers 8
```

### Nginx Worker Connections

Edit `/etc/nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}
```

## Monitoring

### Application Logs

```bash
# Follow systemd logs
sudo journalctl -u label-generator -f

# Filter by date
sudo journalctl -u label-generator --since "1 hour ago"
```

### Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/label-generator-access.log

# Error logs
sudo tail -f /var/log/nginx/label-generator-error.log
```

## Comparison: TCP Port vs Unix Socket

### Run with TCP Port (like before)
```bash
python run_web.py --port 8002
```
- Accessible over network
- Can specify any port
- Uses TCP/IP stack

### Run with Unix Socket
```bash
python run_web_socket.py --socket /tmp/label-generator.sock
```
- Local communication only
- Better performance
- More secure
- Requires reverse proxy for HTTP access

## Additional Resources

- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Systemd Service Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Let's Encrypt](https://letsencrypt.org/)

## Support

For issues or questions, check the main README.md or open an issue on the project repository.
