# TradifyERP Manual Deployment Guide
# Two-Server Setup: App (192.168.20.10) + Database (192.168.20.11)
# December 13, 2025

## Overview

```
┌──────────────────────────────────┐
│   App Server 192.168.20.10        │
│   - Django + Gunicorn + Nginx    │
│   - User: zubair                 │
│   - Root Password: erp           │
└──────────┬───────────────────────┘
           │ PostgreSQL Connection
           │
┌──────────▼───────────────────────┐
│   DB Server 192.168.20.11         │
│   - PostgreSQL 16                │
│   - User: zubair                 │
│   - Root Password: sql           │
└──────────────────────────────────┘
```

## Phase 1: Database Server Setup (192.168.20.11)

### Step 1.1: Connect to Database Server

```bash
ssh zubair@192.168.20.11
# Password: sql
```

### Step 1.2: Install PostgreSQL

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install PostgreSQL 16
sudo apt-get install -y postgresql postgresql-contrib postgresql-16
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Step 1.3: Create Database and User

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Inside PostgreSQL:
CREATE DATABASE tradify ENCODING 'UTF8';
CREATE USER zubair WITH PASSWORD 'zubair@0862';
ALTER USER zubair CREATEDB;
ALTER USER zubair SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE tradify TO zubair;

# Verify
\l
\du
\q
```

### Step 1.4: Configure for Remote Access

```bash
# Find PostgreSQL version
psql --version

# Edit postgresql.conf (replace 16 with your version)
sudo nano /etc/postgresql/16/main/postgresql.conf

# Find and change this line:
# listen_addresses = 'localhost'
# To:
listen_addresses = '*'

# Save and exit (Ctrl+X, Y, Enter)

# Edit pg_hba.conf
sudo nano /etc/postgresql/16/main/pg_hba.conf

# Add at the end:
host    tradify    zubair    192.168.20.10/32    md5
host    all        all       192.168.2.0/24     md5

# Save and exit

# Restart PostgreSQL
sudo systemctl restart postgresql
sudo systemctl status postgresql
```

### Step 1.5: Verify Database Setup

```bash
# Test local connection
psql -U zubair -d tradify -c "SELECT version();"
```

**✓ Database Server Setup Complete**

---

## Phase 2: Application Server Setup (192.168.20.10)

### Step 2.1: Connect to Application Server

```bash
ssh zubair@192.168.20.10
# Password: erp
```

### Step 2.2: Install System Dependencies

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.12 and dependencies
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev
sudo apt-get install -y python3-pip git curl wget
sudo apt-get install -y build-essential libpq-dev postgresql-client
sudo apt-get install -y nginx
```

### Step 2.3: Create Application Directory

```bash
# Create and prepare directory
sudo mkdir -p /var/www/tradifyerp
sudo chown -R zubair:zubair /var/www/tradifyerp
cd /var/www/tradifyerp

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate
```

### Step 2.4: Install Python Packages

```bash
# Activate virtual environment (if not already active)
source /var/www/tradifyerp/venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install gunicorn==23.0.0
pip install psycopg2-binary
pip install django==5.2.9
pip install djangorestframework
pip install django-cors-headers
pip install python-decouple
pip install pillow
```

### Step 2.5: Copy Application Code

On your local machine:
```bash
# Copy TradifyERP directory to server
scp -r f:\ERP-Production\Zubair-ERP-Project\TradifyERP\* zubair@192.168.20.10:/var/www/tradifyerp/
```

Or on the server:
```bash
# If you have git access
cd /var/www/tradifyerp
git clone <your-repo> .
```

### Step 2.6: Configure Django Settings

```bash
# Copy production settings
cp /path/to/settings_production.py /var/www/tradifyerp/TradifyERP/settings.py

# Or manually update TradifyERP/settings.py with:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tradify',
        'USER': 'zubair',
        'PASSWORD': 'zubair@0862',
        'HOST': '192.168.20.11',
        'PORT': '5432',
    }
}

ALLOWED_HOSTS = ['192.168.20.10', 'tradifyglobal.com', 'www.tradifyglobal.com']
DEBUG = False
```

### Step 2.7: Run Migrations

```bash
cd /var/www/tradifyerp
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser (optional, can do later)
# python manage.py createsuperuser
```

### Step 2.8: Collect Static Files

```bash
source /var/www/tradifyerp/venv/bin/activate
cd /var/www/tradifyerp

# Collect static files
python manage.py collectstatic --noinput
```

### Step 2.9: Configure Gunicorn

Create `/var/www/tradifyerp/gunicorn_config.py`:

```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
```

### Step 2.10: Create Gunicorn Systemd Service

```bash
sudo nano /etc/systemd/system/gunicorn_tradifyerp.service
```

Add:
```ini
[Unit]
Description=Gunicorn service for TradifyERP
After=network.target

[Service]
User=zubair
Group=www-data
WorkingDirectory=/var/www/tradifyerp
Environment="PATH=/var/www/tradifyerp/venv/bin"
ExecStart=/var/www/tradifyerp/venv/bin/gunicorn -c gunicorn_config.py TradifyERP.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn_tradifyerp
```

### Step 2.11: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/tradifyerp
```

Add the configuration from `nginx_tradifyglobal_prod.conf`

Enable and test:
```bash
sudo ln -sf /etc/nginx/sites-available/tradifyerp /etc/nginx/sites-enabled/tradifyerp
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx
```

### Step 2.12: Create Log Directories

```bash
sudo mkdir -p /var/log/tradifyerp
sudo chown -R zubair:www-data /var/log/tradifyerp
sudo chmod 755 /var/log/tradifyerp
```

**✓ Application Server Setup Complete**

---

## Phase 3: Start Services and Test

### Step 3.1: Start Gunicorn

```bash
sudo systemctl start gunicorn_tradifyerp
sudo systemctl status gunicorn_tradifyerp
```

### Step 3.2: Start Nginx

```bash
sudo systemctl start nginx
sudo systemctl status nginx
```

### Step 3.3: Test Connection from App to Database

```bash
source /var/www/tradifyerp/venv/bin/activate
python3 -c "
import psycopg2
conn = psycopg2.connect(
    host='192.168.20.11',
    database='tradify',
    user='zubair',
    password='zubair@0862'
)
print('✓ Database connection successful!')
conn.close()
"
```

### Step 3.4: Test Django Application

```bash
curl http://localhost/
# or
curl http://192.168.20.10/
```

Visit: `http://192.168.20.10/` in your browser

**✓ Services running and tested**

---

## Phase 4: Import Production Data

### Step 4.1: Copy Data File to Server

```bash
# From local machine
scp f:\ERP-Production\Zubair-ERP-Project\TradifyERP\prod_data_complete_backup.json \
    zubair@192.168.20.10:/var/www/tradifyerp/
```

### Step 4.2: Load Data into Database

```bash
cd /var/www/tradifyerp
source venv/bin/activate

# Load the fixture
python manage.py loaddata prod_data_complete_backup.json
```

**✓ Production data imported**

---

## Phase 5: Verification

### Verify Dashboard
- Visit: `http://192.168.20.10/accounting/dashboard/`
- Check for Minia theme with light green colors
- Verify Tradify logo is displayed

### Verify Modules
- Accounting: `http://192.168.20.10/accounting/`
- Sales: `http://192.168.20.10/sales/`
- CRM: `http://192.168.20.10/crm/`
- HR: `http://192.168.20.10/hr/`
- Inventory: `http://192.168.20.10/inventory/`

### Check Database
```bash
psql -h 192.168.20.11 -U zubair -d tradify -c "SELECT COUNT(*) FROM accounting_account;"
```

---

## Phase 6: Final Configuration

### Enable SSL/HTTPS (Optional but Recommended)

1. Get SSL certificate (Let's Encrypt):
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot certonly --nginx -d tradifyglobal.com -d www.tradifyglobal.com
```

2. Update nginx configuration with SSL

3. Update Django settings:
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Set Up Backups

```bash
# Database backup script
sudo nano /usr/local/bin/backup_tradify_db.sh

# Content:
#!/bin/bash
BACKUP_DIR="/backups/tradify"
mkdir -p $BACKUP_DIR
pg_dump -h 192.168.20.11 -U zubair tradify | gzip > $BACKUP_DIR/tradify_$(date +%Y%m%d_%H%M%S).sql.gz

# Make executable
sudo chmod +x /usr/local/bin/backup_tradify_db.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup_tradify_db.sh
```

---

## Troubleshooting

### Database Connection Issues
```bash
# Test from app server
psql -h 192.168.20.11 -U zubair -d tradify

# Check PostgreSQL is listening
ssh zubair@192.168.20.11 "sudo netstat -tlnp | grep 5432"

# Check firewall rules
ssh zubair@192.168.20.11 "sudo ufw status"
```

### Gunicorn Issues
```bash
# Check status
sudo systemctl status gunicorn_tradifyerp

# View logs
sudo journalctl -u gunicorn_tradifyerp -f

# Restart
sudo systemctl restart gunicorn_tradifyerp
```

### Nginx Issues
```bash
# Check config
sudo nginx -t

# View error log
sudo tail -f /var/log/nginx/tradifyerp_error.log

# Restart
sudo systemctl restart nginx
```

---

## Rollback Plan

If issues occur:

1. Stop services:
```bash
sudo systemctl stop gunicorn_tradifyerp nginx
```

2. Restore from backup or previous snapshot

3. Contact support or re-run setup

---

**Setup Complete!** Your TradifyERP is now running on the new servers with PostgreSQL database on a separate server.
