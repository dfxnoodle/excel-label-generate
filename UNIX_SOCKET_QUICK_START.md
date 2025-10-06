# Unix Socket Deployment - Quick Reference

## What Was Created

This update adds Unix socket support for production deployment of the Label Generator web application.

## New Files

1. **`run_web_socket.py`** - Main Python script to run the app with Unix socket
   - Supports custom socket paths
   - Configurable permissions
   - Multiple worker processes
   - Auto-reload for development

2. **`run_web_socket.sh`** - Shell wrapper script
   - Auto-activates virtual environment
   - Simple execution

3. **`nginx.conf.example`** - Nginx reverse proxy configuration
   - HTTP and HTTPS examples
   - Static file serving
   - WebSocket support
   - Security headers

4. **`label-generator.service`** - Systemd service file
   - Run as background service
   - Auto-start on boot
   - Auto-restart on failure
   - Logging configuration

5. **`UNIX_SOCKET_DEPLOYMENT.md`** - Complete deployment guide
   - Installation instructions
   - Configuration examples
   - Troubleshooting tips
   - Security best practices

## Quick Start Examples

### Development (with auto-reload)
```bash
python run_web_socket.py --reload
```

### Production (4 workers)
```bash
python run_web_socket.py --workers 4
```

### Custom Socket Path
```bash
python run_web_socket.py --socket /var/run/label-gen.sock
```

### As Systemd Service
```bash
sudo systemctl start label-generator
sudo systemctl enable label-generator  # Start on boot
```

## When to Use Each Method

### Use `run_web.py` (TCP Port) when:
- Development and testing
- Quick demos
- Need direct network access
- Running locally without reverse proxy

### Use `run_web_socket.py` (Unix Socket) when:
- Production deployment
- Using Nginx/Apache reverse proxy
- Need better performance
- Enhanced security required
- Running as a system service

## Benefits of Unix Socket Deployment

✅ **Better Performance** - Local IPC faster than TCP/IP stack
✅ **Enhanced Security** - No network exposure, file-based permissions
✅ **No Port Conflicts** - Uses file paths instead of ports
✅ **Production Ready** - Works with Nginx, systemd, monitoring tools
✅ **Easy Scaling** - Multiple workers, load balancing support

## Next Steps

1. **Test locally first:**
   ```bash
   python run_web_socket.py
   curl --unix-socket /tmp/label-generator.sock http://localhost/
   ```

2. **Set up Nginx** (see nginx.conf.example)

3. **Configure systemd service** (see label-generator.service)

4. **Add SSL/HTTPS** (use Let's Encrypt/Certbot)

5. **Monitor and optimize** (check logs, adjust workers)

## Documentation References

- **Full Guide**: [UNIX_SOCKET_DEPLOYMENT.md](UNIX_SOCKET_DEPLOYMENT.md)
- **Web App Guide**: [WEB_README.md](WEB_README.md)
- **Main README**: [README.md](README.md)

## Support

For questions or issues:
1. Check UNIX_SOCKET_DEPLOYMENT.md troubleshooting section
2. Review Nginx error logs: `sudo tail -f /var/log/nginx/error.log`
3. Check service logs: `sudo journalctl -u label-generator -f`
