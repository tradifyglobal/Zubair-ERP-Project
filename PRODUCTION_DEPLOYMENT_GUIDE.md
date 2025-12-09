# Production Deployment Guide - Secondary Server

This guide allows you to deploy the complete TradifyERP application to a secondary server as a backup using the `production-backup` branch.

## Prerequisites

- Ubuntu 24.04 LTS server
- SSH access with root privileges
- Domain name (or use IP address)
- PostgreSQL 16+ installed
- Python 3.12+
- Nginx installed

## Quick Start Deployment

### 1. Clone Repository on Secondary Server

```bash
cd /var/www
git clone -b production-backup https://github.com/tradifyglobal/Zubair-ERP-Project.git tradifyerp
cd tradifyerp
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r TradifyERP/requirements.txt
```

### 3. Configure PostgreSQL Database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE tradifyerp_db;
CREATE USER tradifyerp_user WITH PASSWORD 'your_secure_password';
ALTER ROLE tradifyerp_user SET client_encoding TO 'utf8';
ALTER ROLE tradifyerp_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE tradifyerp_user SET default_transaction_deferrable TO on;
ALTER ROLE tradifyerp_user SET default_transaction_level TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE tradifyerp_db TO tradifyerp_user;
\q
```

### 4. Configure Django Settings

Edit `TradifyERP/TradifyERP/settings.py`:

```python
ALLOWED_HOSTS = [
    'your.domain.com',
    'www.your.domain.com',
    'your.server.ip',
    'localhost',
    '127.0.0.1',
]

CSRF_TRUSTED_ORIGINS = [
    'https://your.domain.com',
    'https://www.your.domain.com',
    'https://your.server.ip',
    'http://your.server.ip',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tradifyerp_db',
        'USER': 'tradifyerp_user',
        'PASSWORD': 'your_secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
    }
}
```

### 5. Run Django Migrations

```bash
cd /var/www/tradifyerp/TradifyERP
export PYTHONPATH=/var/www/tradifyerp/TradifyERP
/var/www/tradifyerp/venv/bin/python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
/var/www/tradifyerp/venv/bin/python manage.py createsuperuser
```

### 7. Collect Static Files

```bash
/var/www/tradifyerp/venv/bin/python manage.py collectstatic --noinput
```

### 8. Configure Gunicorn

Create `/etc/systemd/system/gunicorn-tradifyerp.service`:

```ini
[Unit]
Description=Gunicorn Application Server for TradifyERP
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/tradifyerp/TradifyERP
Environment="PATH=/var/www/tradifyerp/venv/bin"
Environment="PYTHONPATH=/var/www/tradifyerp/TradifyERP"
ExecStart=/var/www/tradifyerp/venv/bin/gunicorn \
    --workers 8 \
    --bind unix:/var/www/tradifyerp/gunicorn.sock \
    --worker-class sync \
    TradifyERP.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start Gunicorn:

```bash
sudo systemctl enable gunicorn-tradifyerp
sudo systemctl start gunicorn-tradifyerp
```

### 9. Configure Nginx

Create `/etc/nginx/sites-available/tradifyerp`:

```nginx
upstream gunicorn_app {
    server unix:/var/www/tradifyerp/gunicorn.sock fail_timeout=0;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name your.domain.com www.your.domain.com;
    client_max_body_size 100M;

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name your.domain.com www.your.domain.com;
    client_max_body_size 100M;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your.domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your.domain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location /static/ {
        alias /var/www/tradifyerp/TradifyERP/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/tradifyerp/TradifyERP/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://gunicorn_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

# Fallback for localhost/IP access
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    location / {
        proxy_pass http://gunicorn_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable Nginx site:

```bash
sudo ln -s /etc/nginx/sites-available/tradifyerp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 10. Configure SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your.domain.com -d www.your.domain.com
```

## Database Restore (If Importing Existing Data)

If you have a database backup from the primary server:

```bash
# From primary server
pg_dump -U tradifyerp_user -h localhost tradifyerp_db > backup.sql

# Transfer to secondary server
scp backup.sql user@secondary-server:/tmp/

# On secondary server
psql -U tradifyerp_user -d tradifyerp_db < /tmp/backup.sql
```

## Verification

### Check Gunicorn Status

```bash
sudo systemctl status gunicorn-tradifyerp
ps aux | grep gunicorn
```

### Test Django Application

```bash
curl -I https://your.domain.com/
curl -I https://your.domain.com/accounts/login/
curl -I https://your.domain.com/admin/
```

### Check Logs

```bash
sudo journalctl -u gunicorn-tradifyerp -f
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## Important Configuration Files

The `production-backup` branch includes:

- ✅ `TradifyERP/TradifyERP/settings.py` - PostgreSQL configured + CSRF settings
- ✅ `TradifyERP/TradifyERP/wsgi.py` - WSGI application with correct path
- ✅ `TradifyERP/requirements.txt` - All Python dependencies
- ✅ `TradifyERP/manage.py` - Django management script
- ✅ All Django apps and migrations
- ✅ HR module with payroll recursion fix
- ✅ Expense tracking system
- ✅ Admin interface with permissions

## Troubleshooting

### Port Already in Use
```bash
sudo lsof -i :80
sudo lsof -i :443
```

### CSRF Token Errors
Ensure `CSRF_TRUSTED_ORIGINS` and `ALLOWED_HOSTS` are correctly configured for your domain.

### Database Connection Issues
```bash
psql -U tradifyerp_user -h localhost -d tradifyerp_db
```

### Gunicorn Not Starting
```bash
PYTHONPATH=/var/www/tradifyerp/TradifyERP /var/www/tradifyerp/venv/bin/python -m gunicorn --check-config TradifyERP.wsgi:application
```

## Backup Strategy

For regular backups on secondary server:

```bash
# Daily PostgreSQL backup
0 2 * * * pg_dump -U tradifyerp_user -h localhost tradifyerp_db | gzip > /var/www/backups/tradifyerp_$(date +\%Y\%m\%d).sql.gz

# Weekly full system backup
0 3 * * 0 tar -czf /var/www/backups/tradifyerp_full_$(date +\%Y\%m\%d).tar.gz /var/www/tradifyerp
```

## Security Considerations

- Always use strong passwords for PostgreSQL
- Enable firewall and only allow necessary ports
- Use SSL/TLS certificates (Let's Encrypt recommended)
- Keep Django SECRET_KEY unique for each server
- Set `DEBUG = False` in production
- Use environment variables for sensitive configuration
- Regularly update packages and security patches

## Branch Information

**Branch:** `production-backup`  
**Last Updated:** December 9, 2025  
**Includes:** PostgreSQL migration, CSRF security fixes, all modules working  
**Status:** Production-ready for secondary server deployment

For latest updates, check GitHub: https://github.com/tradifyglobal/Zubair-ERP-Project
