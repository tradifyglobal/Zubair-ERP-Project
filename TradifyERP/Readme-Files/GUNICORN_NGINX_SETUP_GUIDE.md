# Gunicorn + Nginx + Let's Encrypt Setup for TradifyERP

## Overview
This guide sets up TradifyERP with:
- **Gunicorn**: WSGI application server
- **Nginx**: Reverse proxy and web server
- **Let's Encrypt**: Free SSL/TLS certificates

## Prerequisites
- Windows Server or workstation
- Administrator access
- Python 3.8+ with pip
- Domain: `www.tradifyglobal.com` (already pointing to your server)
- Ports 80 and 443 must be open

## Step 1: Install Gunicorn

```powershell
# Already installed via pip
# Verify installation
gunicorn --version
```

## Step 2: Download and Install Nginx for Windows

### Option A: Using pre-built binary (Recommended)
1. Download from: http://nginx.org/en/download.html
2. Download the latest stable version (e.g., nginx/Windows-1.25.x)
3. Extract to `C:\nginx`
4. Create logs directory:
```powershell
mkdir C:\nginx\logs
mkdir C:\nginx\html
```

### Option B: Build from source
```powershell
# Not recommended on Windows - use pre-built binary instead
```

### Verify Nginx Installation
```powershell
cd C:\nginx
.\nginx.exe -v
```

## Step 3: Install Let's Encrypt with Certbot

### Install Certbot
```powershell
# Using Chocolatey (recommended)
choco install certbot -y

# Or download manually from:
# https://github.com/certbot/certbot/releases

# Verify installation
certbot --version
```

### Get SSL Certificate
```powershell
# Stop Nginx if running
C:\nginx\nginx.exe -s stop

# Get certificate (will prompt for email, agree to ToS)
certbot certonly --standalone -d tradifyglobal.com -d www.tradifyglobal.com

# Certificate will be saved to:
# C:\ProgramData\certbot\live\tradifyglobal.com\

# If you want to use a different path
certbot certonly --standalone -d tradifyglobal.com -d www.tradifyglobal.com --config-dir C:\letsencrypt --work-dir C:\letsencrypt\work --logs-dir C:\letsencrypt\logs
```

### Certificate Location
Certificates are typically stored in:
- Windows: `C:\ProgramData\certbot\live\tradifyglobal.com\`
  - `fullchain.pem` - Full certificate chain
  - `privkey.pem` - Private key
  - `cert.pem` - Certificate only
  - `chain.pem` - Intermediate certificates

## Step 4: Configure Nginx

1. Copy the provided `nginx_tradifyglobal.conf` file
2. Place it in `C:\nginx\conf\` directory
3. Update the nginx main config at `C:\nginx\conf\nginx.conf`:

```nginx
# Add this to the http block in nginx.conf
include C:/TradifyERP/TradifyERP/nginx_tradifyglobal.conf;
```

Or edit `C:\nginx\conf\nginx.conf` and replace the server block with the config from `nginx_tradifyglobal.conf`.

### Update certificate paths in nginx_tradifyglobal.conf
Find and update these lines with your certificate path:
```nginx
ssl_certificate "C:\letsencrypt\live\tradifyglobal.com\fullchain.pem";
ssl_certificate_key "C:\letsencrypt\live\tradifyglobal.com\privkey.pem";
ssl_trusted_certificate "C:\letsencrypt\live\tradifyglobal.com\chain.pem";
```

### Verify Nginx Configuration
```powershell
C:\nginx\nginx.exe -t
# Output should say: successful
```

## Step 5: Update Django Settings for Production

Edit `TradifyERP/settings.py`:

```python
# SECURITY SETTINGS FOR PRODUCTION
import os

# Check if running in production
if os.environ.get('DJANGO_ENV') == 'production':
    DEBUG = False
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'SAMEORIGIN'
else:
    # Development settings
    DEBUG = True
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
```

## Step 6: Create Logs Directory

```powershell
# Create logs directory for Gunicorn
mkdir G:\TradifyERP\TradifyERP\logs

# Create logs directory for Nginx
mkdir C:\nginx\logs
```

## Step 7: Start Services

### Method 1: Manual Startup (Testing)

**Terminal 1 - Start Gunicorn:**
```powershell
cd G:\TradifyERP\TradifyERP
python -m gunicorn --config gunicorn_config.py TradifyERP.wsgi:application
```

Or use the batch file:
```powershell
cd G:\TradifyERP\TradifyERP
.\run_gunicorn.bat
```

**Terminal 2 - Start Nginx:**
```powershell
cd C:\nginx
.\nginx.exe
```

Or use the batch file:
```powershell
.\run_nginx.bat
```

### Method 2: Automated Startup with Task Scheduler

#### Create Gunicorn Task
1. Open Task Scheduler
2. Create Basic Task: "Start Gunicorn TradifyERP"
3. Trigger: "At startup"
4. Action: Start a program
   - Program: `C:\Python311\python.exe` (your Python path)
   - Arguments: `-m gunicorn --config gunicorn_config.py TradifyERP.wsgi:application`
   - Start in: `G:\TradifyERP\TradifyERP`
   - Check: "Run whether user is logged in or not"
5. Finish

#### Create Nginx Task
1. Create Basic Task: "Start Nginx"
2. Trigger: "At startup"
3. Action: Start a program
   - Program: `C:\nginx\nginx.exe`
   - Start in: `C:\nginx`
   - Check: "Run whether user is logged in or not"
4. Finish

### Method 3: Windows Services (Advanced)

**For Gunicorn:**
```powershell
# Install NSSM (Non-Sucking Service Manager)
choco install nssm -y

# Create service
nssm install TradifyERP-Gunicorn C:\Python311\python.exe "-m gunicorn --config gunicorn_config.py TradifyERP.wsgi:application"
nssm set TradifyERP-Gunicorn AppDirectory "G:\TradifyERP\TradifyERP"
nssm set TradifyERP-Gunicorn AppEnvironmentExtra DJANGO_ENV=production

# Start service
nssm start TradifyERP-Gunicorn
```

**For Nginx:**
```powershell
# Install NSSM if not already installed
choco install nssm -y

# Create service
nssm install TradifyERP-Nginx C:\nginx\nginx.exe
nssm set TradifyERP-Nginx AppDirectory "C:\nginx"

# Start service
nssm start TradifyERP-Nginx
```

## Step 8: Test HTTPS Connection

```powershell
# Test HTTP (should redirect to HTTPS)
curl -v http://www.tradifyglobal.com/

# Test HTTPS
curl -v https://www.tradifyglobal.com/

# Or open in browser
# https://www.tradifyglobal.com
```

## Step 9: Renew Let's Encrypt Certificate

### Manual Renewal
```powershell
# Renew all certificates (runs 30 days before expiration)
certbot renew

# Reload Nginx after renewal
C:\nginx\nginx.exe -s reload
```

### Automatic Renewal with Task Scheduler

1. Open Task Scheduler
2. Create Basic Task: "Renew Let's Encrypt Certificates"
3. Trigger: Daily at 3:00 AM
4. Action: Start a program
   - Program: `certbot`
   - Arguments: `renew --quiet`
5. Add another action:
   - Program: `C:\nginx\nginx.exe`
   - Arguments: `-s reload`
6. Finish

### Check Certificate Expiration
```powershell
# Check all certificates
certbot certificates

# Check specific certificate
certbot certificates -d tradifyglobal.com
```

## Step 10: Monitor Services

```powershell
# Check if Gunicorn is running
netstat -ano | findstr 8001

# Check if Nginx is running
netstat -ano | findstr :80
netstat -ano | findstr :443

# View Nginx logs
Get-Content C:\nginx\logs\error.log -Tail 50

# View Gunicorn logs
Get-Content G:\TradifyERP\TradifyERP\logs\error.log -Tail 50
```

## Common Commands

### Nginx Control
```powershell
# Start Nginx
C:\nginx\nginx.exe

# Stop Nginx
C:\nginx\nginx.exe -s stop

# Reload configuration (graceful restart)
C:\nginx\nginx.exe -s reload

# Reload configuration and restart
C:\nginx\nginx.exe -s reopen

# Test configuration
C:\nginx\nginx.exe -t
```

### Gunicorn Control
```powershell
# Start with config file
gunicorn --config gunicorn_config.py TradifyERP.wsgi:application

# Start with specific workers
gunicorn --workers 4 --bind 127.0.0.1:8001 TradifyERP.wsgi:application

# Kill Gunicorn process
taskkill /F /IM python.exe  # Be careful with this!

# Or find PID first
netstat -ano | findstr 8001
taskkill /PID <PID> /F
```

### Certbot Control
```powershell
# Renew certificates
certbot renew

# List certificates
certbot certificates

# Delete certificate
certbot delete --cert-name tradifyglobal.com

# Show help
certbot --help
```

## Troubleshooting

### Port 80 or 443 Already in Use
```powershell
# Find what's using the port
netstat -ano | findstr :80
netstat -ano | findstr :443

# Kill the process
taskkill /PID <PID> /F
```

### Nginx Won't Start
```powershell
# Test configuration
C:\nginx\nginx.exe -t

# View error log
Get-Content C:\nginx\logs\error.log

# Check if port is in use
netstat -ano | findstr :80
netstat -ano | findstr :443
```

### Certificate Issues
```powershell
# Verify certificate
certbot certificates

# Dry run renewal
certbot renew --dry-run

# Force renewal
certbot renew --force-renewal

# Update contact email
certbot update_account --email newemail@example.com
```

### Django Static Files Not Loading
```powershell
# Collect static files
python manage.py collectstatic --noinput

# Check file permissions
Get-Acl G:\TradifyERP\TradifyERP\static
```

### Gunicorn Not Connecting
```powershell
# Check if Gunicorn is running
netstat -ano | findstr 8001

# Check logs
Get-Content G:\TradifyERP\TradifyERP\logs\error.log

# Restart Gunicorn
taskkill /F /PID <PID>
python -m gunicorn --config gunicorn_config.py TradifyERP.wsgi:application
```

## Performance Tuning

### Nginx Settings
```nginx
# In nginx.conf, optimize worker processes
worker_processes auto;  # Auto-detect CPU cores
worker_connections 1024;  # Connections per worker

# Connection buffering
client_body_buffer_size 128k;
client_max_body_size 100M;
```

### Gunicorn Settings
```python
# In gunicorn_config.py
workers = multiprocessing.cpu_count() * 2 + 1  # Workers
worker_connections = 1000  # Connections per worker
max_requests = 1000  # Requests before restart
```

## Security Checklist

- [ ] HTTPS enabled and redirecting HTTP
- [ ] SSL certificate valid (check expiration)
- [ ] Certificate auto-renewal scheduled
- [ ] Django DEBUG = False in production
- [ ] SECRET_KEY is strong and unique
- [ ] ALLOWED_HOSTS configured correctly
- [ ] Security headers in place (HSTS, CSP, etc.)
- [ ] Firewall rules configured
- [ ] Static and media files served correctly
- [ ] Logs being written and monitored
- [ ] Regular backups scheduled

## Accessing Your Application

- **HTTPS (Secure)**: https://www.tradifyglobal.com
- **HTTP (Auto-redirects)**: http://www.tradifyglobal.com → https://www.tradifyglobal.com

## Support & Resources

- Nginx Documentation: http://nginx.org/en/docs/
- Gunicorn Documentation: https://docs.gunicorn.org/
- Let's Encrypt: https://letsencrypt.org/
- Certbot: https://certbot.eff.org/
- Django Production: https://docs.djangoproject.com/en/5.2/howto/deployment/

---
**Last Updated:** December 1, 2025
**For:** TradifyERP Application
**Domain:** www.tradifyglobal.com
