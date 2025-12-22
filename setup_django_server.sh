#!/bin/bash

# Django Application Server Setup Script
# App Server: 192.168.2.69
# Created: December 13, 2025

echo "=========================================="
echo "Django Application Server Setup"
echo "=========================================="

# Variables
APP_USER="zubair"
APP_DIR="/var/www/tradifyerp"
VENV_DIR="${APP_DIR}/venv"
DB_HOST="192.168.2.59"
DB_NAME="tradify"
DB_USER="zubair"
DB_PASSWORD="zubair@0862"

# Update system
echo "[1/8] Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and dependencies
echo "[2/8] Installing Python 3.12 and dependencies..."
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev
sudo apt-get install -y python3-pip git curl wget
sudo apt-get install -y build-essential libpq-dev postgresql-client
sudo apt-get install -y nginx

# Create application directory
echo "[3/8] Creating application directory..."
sudo mkdir -p ${APP_DIR}
sudo chown -R ${APP_USER}:${APP_USER} ${APP_DIR}

# Create virtual environment
echo "[4/8] Creating Python virtual environment..."
cd ${APP_DIR}
python3.12 -m venv ${VENV_DIR}
source ${VENV_DIR}/bin/activate

# Install Python dependencies
echo "[5/8] Installing Python requirements..."
# Note: Will copy requirements.txt from local and install
pip install --upgrade pip
pip install gunicorn==23.0.0
pip install psycopg2-binary
# Add other requirements from your project

# Create settings file for PostgreSQL
echo "[6/8] Creating Django settings for PostgreSQL..."
cat > ${APP_DIR}/local_settings_prod.py << 'SETTINGSEOF'
# PostgreSQL Production Settings
import os
from pathlib import Path

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tradify',
        'USER': 'zubair',
        'PASSWORD': 'zubair@0862',
        'HOST': '192.168.2.59',
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
    }
}

# Security Settings
DEBUG = False
ALLOWED_HOSTS = ['192.168.2.69', 'tradifyglobal.com', 'www.tradifyglobal.com']

# SSL/HTTPS
SECURE_SSL_REDIRECT = False  # Set to True after SSL setup
SESSION_COOKIE_SECURE = False  # Set to True after SSL setup
CSRF_COOKIE_SECURE = False  # Set to True after SSL setup

# Static and Media Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(Path(__file__).resolve().parent.parent, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(Path(__file__).resolve().parent.parent, 'media')

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/tradifyerp/django_error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'tradify-cache',
    }
}
SETTINGSEOF

# Create Gunicorn configuration
echo "[7/8] Creating Gunicorn configuration..."
cat > ${APP_DIR}/gunicorn_config.py << 'GUNICORNEOF'
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = True
daemon = False
debug = False
GUNICORNEOF

# Create systemd service file
echo "[8/8] Creating systemd service..."
sudo bash -c "cat > /etc/systemd/system/gunicorn_tradifyerp.service << 'SERVICEEOF'
[Unit]
Description=Gunicorn service for TradifyERP
After=network.target

[Service]
User=zubair
Group=www-data
WorkingDirectory=/var/www/tradifyerp
Environment="PATH=/var/www/tradifyerp/venv/bin"
ExecStart=/var/www/tradifyerp/venv/bin/gunicorn -c gunicorn_config.py TradifyERP.wsgi:application

[Install]
WantedBy=multi-user.target
SERVICEEOF"

sudo systemctl daemon-reload
sudo systemctl enable gunicorn_tradifyerp

echo "=========================================="
echo "Application Server Setup Complete!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Copy your Django application to: ${APP_DIR}"
echo "2. Copy requirements.txt and run: pip install -r requirements.txt"
echo "3. Update ${APP_DIR}/TradifyERP/settings.py with database config"
echo "4. Run migrations: python manage.py migrate"
echo "5. Collect static files: python manage.py collectstatic"
echo "6. Start Gunicorn: sudo systemctl start gunicorn_tradifyerp"
echo "7. Configure Nginx (see nginx_config.conf)"
echo "8. Test connection: curl http://localhost:8000"
echo "=========================================="
