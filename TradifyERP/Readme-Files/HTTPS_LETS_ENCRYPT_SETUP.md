# HTTPS Setup with Let's Encrypt for TradifyERP

## Overview
This guide shows how to set up HTTPS with Let's Encrypt SSL certificate for your TradifyERP application running on Windows at `www.tradifyglobal.com`.

## Prerequisites
- Domain: `www.tradifyglobal.com` (already pointing to your server IP: `192.168.2.55`)
- Windows Server with admin access
- Python/Django application running

## Option 1: Using IIS (Recommended for Windows)

### Step 1: Install IIS
```powershell
# Run as Administrator
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole -All
Enable-WindowsOptionalFeature -Online -FeatureName IIS-HostableWebCore
```

### Step 2: Install URL Rewrite and Application Request Routing (ARR)
1. Download from Microsoft:
   - URL Rewrite: https://www.iis.net/downloads/microsoft/url-rewrite
   - Application Request Routing: https://www.iis.net/downloads/microsoft/application-request-routing

2. Install both modules

### Step 3: Install Let's Encrypt Certificate (Using Certbot)

```powershell
# Install Certbot via Chocolatey
choco install certbot -y

# Or install manually from: https://github.com/certbot/certbot/releases

# Run Certbot with IIS plugin
certbot certonly --iis -d tradifyglobal.com -d www.tradifyglobal.com

# Note: On first run, you may need to use webroot plugin if IIS plugin fails:
certbot certonly --webroot -w C:\path\to\static\files -d tradifyglobal.com -d www.tradifyglobal.com
```

### Step 4: Configure IIS HTTPS Binding

1. Open IIS Manager
2. Select your website "TradifyERP"
3. In the right panel, click "Bindings"
4. Click "Add"
5. Select type: "https"
6. Port: 443
7. SSL certificate: Select the Let's Encrypt certificate
8. Click OK

### Step 5: Add HTTP to HTTPS Redirect Rule

1. In IIS Manager, select your website
2. Double-click "URL Rewrite"
3. Click "Add Rule" > "New Inbound Rule"
4. Rule name: "HTTPS Redirect"
5. Pattern: `.*`
6. Action: Redirect
7. Redirect URL: `https://{HTTP_HOST}{REQUEST_URI}`
8. Redirect type: Permanent (301)

## Option 2: Using Gunicorn + Nginx (Alternative)

### Step 1: Install Gunicorn
```powershell
pip install gunicorn
```

### Step 2: Install Nginx for Windows
Download from: http://nginx.org/en/download.html

### Step 3: Configure Gunicorn
Create `gunicorn.service.py`:
```powershell
# Run Gunicorn on port 8001
gunicorn --workers 4 --bind 127.0.0.1:8001 TradifyERP.wsgi:application
```

### Step 4: Configure Nginx
Edit nginx config file:
```nginx
server {
    listen 80;
    server_name www.tradifyglobal.com tradifyglobal.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name www.tradifyglobal.com tradifyglobal.com;

    ssl_certificate /etc/letsencrypt/live/tradifyglobal.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tradifyglobal.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias C:/TradifyERP/TradifyERP/static/;
    }

    location /media/ {
        alias C:/TradifyERP/TradifyERP/media/;
    }
}
```

## Step 5: Update Django Settings for Production

Edit `TradifyERP/settings.py`:

```python
# Production settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

## Step 6: Auto-Renew Let's Encrypt Certificate

### Using Windows Task Scheduler:

1. Create a renewal script `renew_cert.bat`:
```batch
@echo off
certbot renew --quiet
net stop IIS
net start IIS
```

2. Open Task Scheduler
3. Create Basic Task
4. Trigger: Daily at 3 AM
5. Action: Start program: `renew_cert.bat`

### Automatic Renewal (Certbot):
```powershell
# Test auto-renewal
certbot renew --dry-run

# Certbot usually auto-renews 30 days before expiration
```

## Step 7: Testing

```bash
# Test HTTPS
https://www.tradifyglobal.com

# Check SSL certificate
# Use online tool: https://www.ssllabs.com/ssltest/analyze.html?d=www.tradifyglobal.com

# Test Django is working
curl https://www.tradifyglobal.com/
```

## Troubleshooting

### Certificate Not Found
```powershell
# List certificates
certbot certificates

# Delete and re-create
certbot delete --cert-name tradifyglobal.com
certbot certonly --iis -d tradifyglobal.com -d www.tradifyglobal.com
```

### Port 443 Already in Use
```powershell
# Find what's using port 443
netstat -ano | findstr :443

# Kill the process
taskkill /PID <PID> /F
```

### DNS Issues
- Verify DNS points to correct IP in GoDaddy
- Wait 24-48 hours for DNS propagation
- Test DNS: `nslookup www.tradifyglobal.com`

## Security Checklist

- [ ] HTTPS enabled and redirecting HTTP to HTTPS
- [ ] SSL certificate valid and not expired
- [ ] HSTS header enabled
- [ ] Django DEBUG = False in production
- [ ] SECRET_KEY is strong and unique
- [ ] ALLOWED_HOSTS includes your domain
- [ ] Firewall rules configured
- [ ] Auto-renewal scheduled

## Next Steps

1. Choose deployment option (IIS or Nginx)
2. Install and configure Let's Encrypt
3. Update Django settings for production
4. Test HTTPS connection
5. Set up certificate auto-renewal
6. Monitor certificate expiration

## Resources

- Let's Encrypt: https://letsencrypt.org/
- Certbot Documentation: https://certbot.eff.org/docs/
- Django HTTPS: https://docs.djangoproject.com/en/5.2/topics/security/
- IIS URL Rewrite: https://docs.microsoft.com/en-us/iis/extensions/url-rewrite-module/using-the-url-rewrite-module
