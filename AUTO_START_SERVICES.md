# TradifyERP Auto-Start Services Configuration

## Overview
Your Ubuntu production server is configured to automatically start all ERP-related services when the system reboots. This ensures zero-downtime recovery after unexpected shutdowns.

## Auto-Starting Services

### 1. **Gunicorn (Django Application Server)**
- **Service Name**: `gunicorn_tradifyerp`
- **Status**: ✓ Enabled for auto-start
- **Configuration File**: `/etc/systemd/system/gunicorn_tradifyerp.service`
- **Worker Processes**: 8
- **Socket**: `/var/www/tradifyerp/gunicorn.sock`
- **Auto-Restart**: Yes (with 10-second delay if it crashes)
- **Startup Order**: Starts after network is ready
- **Log Files**:
  - Access: `/var/log/tradifyerp/gunicorn_access.log`
  - Error: `/var/log/tradifyerp/gunicorn_error.log`

### 2. **Nginx (Web Server & Reverse Proxy)**
- **Service Name**: `nginx`
- **Status**: ✓ Enabled for auto-start
- **Configuration**: `/etc/nginx/sites-enabled/tradifyerp`
- **Purpose**: Serves static files, proxies requests to Gunicorn
- **SSL**: HTTPS enabled (Let's Encrypt certificate)
- **Auto-Restart**: Yes (systemd manages restart)

### 3. **SSH (Remote Access)**
- **Service Name**: `ssh`
- **Status**: ✓ Enabled for auto-start
- **Port**: 22 (default)
- **Purpose**: Secure remote shell access
- **Connection User**: `zubair`

### 4. **UFW (Uncomplicated Firewall)**
- **Service Name**: `ufw`
- **Status**: ✓ Configured but currently inactive
- **Purpose**: Port and network traffic management
- **Note**: Currently inactive. Enable with: `sudo ufw enable`

## Service Management Commands

### Check Service Status
```bash
# Check individual service
systemctl status gunicorn_tradifyerp
systemctl status nginx
systemctl status ssh

# Check all at once (on production server)
/home/zubair/check_services.sh
```

### Manual Service Control
```bash
# Start service
sudo systemctl start gunicorn_tradifyerp

# Stop service
sudo systemctl stop gunicorn_tradifyerp

# Restart service
sudo systemctl restart gunicorn_tradifyerp

# Enable auto-start
sudo systemctl enable gunicorn_tradifyerp

# Disable auto-start
sudo systemctl disable gunicorn_tradifyerp

# View service logs
sudo journalctl -u gunicorn_tradifyerp -f
```

## Automatic Startup Sequence on System Reboot

When your Ubuntu server restarts, systemd automatically performs these steps:

1. **System Boot** (kernel starts)
2. **Network Initialization** (network.target is reached)
3. **SSH Service Starts** (port 22 opens)
4. **Gunicorn Starts** (listens on `/var/www/tradifyerp/gunicorn.sock`)
5. **Nginx Starts** (listens on ports 80/443, proxies to Gunicorn)
6. **UFW Loads** (firewall rules, currently inactive)

**Total Startup Time**: Approximately 1-2 minutes

## Current Auto-Start Status

| Service | Enabled | Active | Auto-Restart |
|---------|---------|--------|--------------|
| gunicorn_tradifyerp | ✓ Yes | ✓ Yes | ✓ Yes (10s) |
| nginx | ✓ Yes | ✓ Yes | ✓ Yes |
| ssh | ✓ Yes | ✓ Yes | ✓ Yes |
| ufw | ✓ Yes | ✗ No | N/A |

## Testing Auto-Start (Optional)

To verify services start automatically after reboot:

```bash
# 1. SSH into the server
ssh zubair@192.168.2.185

# 2. Check all services are running
systemctl status gunicorn_tradifyerp nginx ssh

# 3. Verify the application is responding
curl -L http://localhost:80

# 4. Check via domain (if DNS is working)
curl -I https://tradifyglobal.com
```

## Monitoring & Alerts

### View Recent Service Logs
```bash
# Last 50 lines of gunicorn logs
sudo journalctl -u gunicorn_tradifyerp -n 50

# Real-time logs (Ctrl+C to exit)
sudo journalctl -u gunicorn_tradifyerp -f

# View nginx error logs
sudo tail -f /var/log/nginx/error.log

# View nginx access logs
sudo tail -f /var/log/nginx/access.log
```

### Check System Uptime
```bash
uptime
# Shows: system uptime and load average
```

### Verify Application Health
```bash
# Check if Gunicorn socket exists
ls -la /var/www/tradifyerp/gunicorn.sock

# Check listening ports
sudo netstat -tuln | grep LISTEN

# Check Nginx status
sudo nginx -t
```

## Troubleshooting Auto-Start Issues

### If Gunicorn doesn't start:
```bash
# Check logs
sudo journalctl -u gunicorn_tradifyerp -n 100

# Verify working directory exists
ls -la /var/www/tradifyerp/TradifyERP

# Check Python virtual environment
/var/www/tradifyerp/venv/bin/python --version

# Try manual start
sudo systemctl start gunicorn_tradifyerp
sudo systemctl status gunicorn_tradifyerp
```

### If Nginx doesn't start:
```bash
# Test configuration
sudo nginx -t

# Check logs
sudo journalctl -u nginx

# View error log
sudo tail -f /var/log/nginx/error.log
```

### If SSH doesn't respond:
```bash
# Check SSH service
sudo systemctl status ssh

# Restart SSH
sudo systemctl restart ssh

# Check SSH port
sudo netstat -tuln | grep :22
```

## Quick Reference

| Task | Command |
|------|---------|
| Check all services | `/home/zubair/check_services.sh` |
| View gunicorn status | `systemctl status gunicorn_tradifyerp` |
| Restart gunicorn | `sudo systemctl restart gunicorn_tradifyerp` |
| View gunicorn logs | `sudo journalctl -u gunicorn_tradifyerp -f` |
| Restart all services | `sudo systemctl restart nginx gunicorn_tradifyerp` |
| Check app at domain | `curl -I https://tradifyglobal.com` |
| SSH to server | `ssh zubair@192.168.2.185` |

## Key Files & Locations

| Component | Location |
|-----------|----------|
| Django App | `/var/www/tradifyerp/TradifyERP/` |
| Gunicorn Config | `/etc/systemd/system/gunicorn_tradifyerp.service` |
| Nginx Config | `/etc/nginx/sites-enabled/tradifyerp` |
| Gunicorn Logs | `/var/log/tradifyerp/gunicorn_*.log` |
| Nginx Logs | `/var/log/nginx/` |
| Virtual Environment | `/var/www/tradifyerp/venv/` |
| Gunicorn Socket | `/var/www/tradifyerp/gunicorn.sock` |

## Summary

✓ **All services are configured for automatic startup**

Your TradifyERP application will automatically start on system reboot without manual intervention. The gunicorn application server has auto-restart enabled, so if it crashes, it will automatically restart after 10 seconds.

For production monitoring, consider setting up:
- System monitoring tools (e.g., `htop`, `monitoring` dashboards)
- Log aggregation (e.g., centralized log server)
- Health check endpoints (e.g., ping/healthcheck API)
- Alerting system for critical service failures

---
**Last Updated**: December 6, 2025
**Server**: Ubuntu 24.04 LTS
**Python**: 3.12.3
