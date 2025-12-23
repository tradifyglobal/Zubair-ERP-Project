# Backup App Server Setup Guide

**Date**: December 23, 2025  
**Target Server**: 192.168.20.20 (Backup App Server)  
**Configuration**: Standby/Replica of 192.168.20.10 (Primary App Server)  
**OS**: Ubuntu 22.04 LTS

---

## 📋 Prerequisites

- Secondary VM/physical server provisioned
- IP: 192.168.20.20 assigned
- SSH access configured
- Network connectivity to all servers
- Same Linux distribution as primary (Ubuntu 22.04)

---

## 🚀 Phase 1: Initial Server Setup

### Connect to Backup App Server

```bash
ssh zubair@192.168.20.20
```

### Update System

```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

### Install Required Packages

```bash
# Python and development tools
sudo apt install -y python3.12 python3.12-venv python3.12-dev
sudo apt install -y build-essential libpq-dev

# Web server
sudo apt install -y nginx

# Process manager
sudo apt install -y supervisor

# Monitoring and utilities
sudo apt install -y htop net-tools git curl wget

# SSL/TLS
sudo apt install -y certbot python3-certbot-nginx

# Backup tools
sudo apt install -y rsync openssh-client
```

### Create Application User

```bash
sudo useradd -m -s /bin/bash tradifyapp
sudo usermod -aG www-data tradifyapp
```

---

## 🔧 Phase 2: Clone Application Code

### Create Application Directory

```bash
sudo mkdir -p /var/www/tradifyerp
sudo chown tradifyapp:www-data /var/www/tradifyerp
sudo chmod 750 /var/www/tradifyerp

cd /var/www/tradifyerp
```

### Clone from GitHub (Assuming Public Repo)

```bash
sudo -u tradifyapp git clone https://github.com/tradifyglobal/Zubair-ERP-Project.git /var/www/tradifyerp

# Or copy from primary server
sudo rsync -avz --delete zubair@192.168.20.10:/var/www/tradifyerp/ /var/www/tradifyerp/

# Fix ownership
sudo chown -R tradifyapp:www-data /var/www/tradifyerp
```

### Create Python Virtual Environment

```bash
cd /var/www/tradifyerp/TradifyERP

sudo -u tradifyapp python3.12 -m venv /var/www/tradifyerp/venv

# Activate and upgrade pip
sudo -u tradifyapp /var/www/tradifyerp/venv/bin/pip install --upgrade pip setuptools wheel
```

### Install Python Dependencies

```bash
# Install requirements
sudo -u tradifyapp /var/www/tradifyerp/venv/bin/pip install -r /var/www/tradifyerp/requirements.txt

# Typical dependencies
# django
# psycopg2-binary (PostgreSQL driver)
# gunicorn
# djangorestframework
# etc.
```

---

## ⚙️ Phase 3: Configure Django Settings

### Copy Production Settings

```bash
sudo -u tradifyapp cp /var/www/tradifyerp/TradifyERP/settings_production.py \
                        /var/www/tradifyerp/TradifyERP/settings_production.py.backup
```

### Edit Production Settings

```bash
sudo nano /var/www/tradifyerp/TradifyERP/settings_production.py
```

**Required changes:**

```python
# Database Configuration (point to PRIMARY database)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tradifyerp_db',
        'USER': 'tradifyerp_user',
        'PASSWORD': 'Tradify@PostgreSQL2024',
        'HOST': '192.168.20.11',  # Primary database server
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
    }
}

# Allow this server
ALLOWED_HOSTS = [
    '192.168.20.20',
    'localhost',
    '127.0.0.1',
    '192.168.20.50',  # Virtual IP
    'backup-app.yourdomain.com',
]

# CSRF Settings
CSRF_TRUSTED_ORIGINS = [
    'http://192.168.20.20',
    'http://192.168.20.50',
    'https://192.168.20.50',
]

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/tradifyerp/static/'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/tradifyerp/media/'

# Debug (should be False in production)
DEBUG = False

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/tradifyerp/django.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### Collect Static Files

```bash
cd /var/www/tradifyerp/TradifyERP

sudo -u tradifyapp /var/www/tradifyerp/venv/bin/python manage.py collectstatic --noinput --settings=TradifyERP.settings_production
```

---

## 🚀 Phase 4: Setup Gunicorn

### Create Gunicorn Systemd Service

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

**Configuration:**

```ini
[Unit]
Description=Gunicorn daemon for TradifyERP (Backup)
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
User=tradifyapp
Group=www-data
WorkingDirectory=/var/www/tradifyerp
Environment="PATH=/var/www/tradifyerp/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=TradifyERP.settings_production"
ExecStart=/var/www/tradifyerp/venv/bin/gunicorn \
          --workers 2 \
          --worker-class sync \
          --bind 127.0.0.1:8000 \
          --timeout 300 \
          --access-logfile /var/log/tradifyerp/gunicorn_access.log \
          --error-logfile /var/log/tradifyerp/gunicorn_error.log \
          TradifyERP.wsgi:application

Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Create Logging Directory

```bash
sudo mkdir -p /var/log/tradifyerp
sudo chown tradifyapp:www-data /var/log/tradifyerp
sudo chmod 750 /var/log/tradifyerp
```

### Enable and Start Gunicorn

```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn

# Check status
sudo systemctl status gunicorn
```

---

## 🌐 Phase 5: Configure Nginx

### Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/tradifyerp
```

**Configuration:**

```nginx
upstream gunicorn {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name 192.168.20.20 backup-app backup-app.yourdomain.com;

    client_max_body_size 100M;
    proxy_read_timeout 600s;
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;

    location / {
        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        proxy_http_version 1.1;
    }

    location /static/ {
        alias /var/www/tradifyerp/static/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/tradifyerp/media/;
        expires 7d;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/tradifyerp_access.log;
    error_log /var/log/nginx/tradifyerp_error.log;
}

# Redirect HTTP to HTTPS (if SSL configured)
# This is optional - configure after initial testing
```

### Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/tradifyerp /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
sudo systemctl enable nginx
```

---

## 🔄 Phase 6: Setup Code Synchronization

### Method 1: Git Pull (Recommended)

**Setup periodic git pull from GitHub:**

```bash
sudo nano /etc/cron.d/tradifyerp-sync
```

Add:
```bash
# Sync TradifyERP code every 15 minutes
*/15 * * * * tradifyapp cd /var/www/tradifyerp && /var/www/tradifyerp/venv/bin/git pull origin changes >> /var/log/tradifyerp/git-sync.log 2>&1
```

### Method 2: Rsync from Primary (Alternative)

```bash
# Create sync script
sudo nano /usr/local/bin/sync-tradifyerp.sh
```

Add:
```bash
#!/bin/bash
rsync -avz --delete zubair@192.168.20.10:/var/www/tradifyerp/ /var/www/tradifyerp/
```

Make executable:
```bash
sudo chmod +x /usr/local/bin/sync-tradifyerp.sh

# Add to crontab
sudo nano /etc/cron.d/tradifyerp-rsync
```

Add:
```bash
*/15 * * * * root /usr/local/bin/sync-tradifyerp.sh >> /var/log/tradifyerp/rsync.log 2>&1
```

---

## ✅ Phase 7: Verification

### Check Gunicorn Status

```bash
sudo systemctl status gunicorn
ps aux | grep gunicorn
curl -s http://127.0.0.1:8000/ -w "\nHTTP: %{http_code}\n"
```

Expected: HTTP 302 (redirect to login)

### Check Nginx Status

```bash
sudo systemctl status nginx
curl -s http://192.168.20.20/ -w "\nHTTP: %{http_code}\n"
```

Expected: HTTP 302

### Check Database Connection

```bash
sudo -u tradifyapp /var/www/tradifyerp/venv/bin/python3 << 'EOF'
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT 1')
    print("✓ Database connection successful")
    print(f"  Server: 192.168.20.11")
    print(f"  Database: tradifyerp_db")
EOF
```

### Check Log Files

```bash
# Gunicorn logs
sudo tail -20 /var/log/tradifyerp/gunicorn_error.log
sudo tail -20 /var/log/tradifyerp/gunicorn_access.log

# Nginx logs
sudo tail -20 /var/log/nginx/tradifyerp_error.log
sudo tail -20 /var/log/nginx/tradifyerp_access.log
```

---

## 🔐 Phase 8: Security Hardening

### SSH Hardening

```bash
# Disable password auth (use keys only)
sudo nano /etc/ssh/sshd_config
```

Set:
```
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin no
```

Restart:
```bash
sudo systemctl restart sshd
```

### Firewall Configuration

```bash
# Install UFW (Uncomplicated Firewall)
sudo apt install -y ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check rules
sudo ufw status numbered
```

### File Permissions

```bash
# Secure application directory
sudo chmod -R 750 /var/www/tradifyerp
sudo chmod -R o-rwx /var/www/tradifyerp/TradifyERP

# Secure logs
sudo chmod 750 /var/log/tradifyerp
sudo chmod 640 /var/log/tradifyerp/*.log
```

---

## 📊 Phase 9: Monitoring & Health Checks

### Create Health Check Script

```bash
sudo nano /usr/local/bin/app-health-check.sh
```

Add:
```bash
#!/bin/bash

echo "=== APP SERVER HEALTH CHECK ==="
echo ""

echo "1. Gunicorn Status:"
systemctl is-active gunicorn || echo "FAILED"

echo "2. Nginx Status:"
systemctl is-active nginx || echo "FAILED"

echo "3. Port 8000 Listening:"
ss -tlnp | grep :8000 || echo "NOT FOUND"

echo "4. HTTP Response:"
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8000/

echo "5. Database Connection:"
/var/www/tradifyerp/venv/bin/python3 << 'PYEOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        print("✓ Connected")
except Exception as e:
    print(f"✗ Failed: {e}")
PYEOF

echo ""
echo "=== END HEALTH CHECK ==="
```

Make executable:
```bash
sudo chmod +x /usr/local/bin/app-health-check.sh

# Run manually
sudo /usr/local/bin/app-health-check.sh
```

### Auto-Start Health Check Service

```bash
sudo nano /etc/systemd/system/app-health-check.service
```

Add:
```ini
[Unit]
Description=App Server Health Check
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/app-health-check.sh
StandardOutput=journal

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable app-health-check.service
```

---

## 🎯 Backup Server is Ready!

Your backup app server is now:
- ✓ Running Nginx and Gunicorn
- ✓ Connected to primary database
- ✓ Syncing code from primary/GitHub
- ✓ Ready for failover
- ✓ Monitored and health checked

**Next Steps:**
1. Set up HAProxy load balancer (192.168.20.30)
2. Configure virtual IP (192.168.20.50)
3. Test failover scenarios
4. Monitor replication and app health

---

*Backup App Server Setup Guide*  
*For: Zubair ERP System*  
*Date: December 23, 2025*
