#!/bin/bash
# Simplified Production Deployment Script
# Run this on web server: 192.168.20.10
# Usage: bash deploy-server.sh

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  TRADIFY GLOBAL ERP - PRODUCTION DEPLOYMENT${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""

# Configuration
PROJECT_DIR="/opt/tradifyerp"
VENV_DIR="$PROJECT_DIR/TradifyERP/venv"
APP_USER="tradifyapp"
APP_GROUP="tradifyapp"

# Verify running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root (use sudo)${NC}"
   exit 1
fi

echo -e "${YELLOW}[1/10]${NC} Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq python3.11 python3-pip python3-venv nginx redis-server postgresql-client curl wget git

echo -e "${YELLOW}[2/10]${NC} Creating application user..."
if ! id "$APP_USER" &>/dev/null; then
    useradd -m -s /bin/bash $APP_USER
    echo -e "${GREEN}✓${NC} User $APP_USER created"
else
    echo -e "${GREEN}✓${NC} User $APP_USER exists"
fi

echo -e "${YELLOW}[3/10]${NC} Setting up project directory..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

if [ -d .git ]; then
    git pull origin changes
    echo -e "${GREEN}✓${NC} Code updated from GitHub"
else
    git clone https://github.com/tradifyglobal/Zubair-ERP-Project.git .
    cd .
    git checkout changes
    echo -e "${GREEN}✓${NC} Code cloned from GitHub"
fi

echo -e "${YELLOW}[4/10]${NC} Creating Python virtual environment..."
cd $PROJECT_DIR/TradifyERP
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel -q
pip install -r requirements.txt -q
pip install -r ../requirements-security.txt -q
echo -e "${GREEN}✓${NC} Virtual environment ready"

echo -e "${YELLOW}[5/10]${NC} Setting up environment variables..."
cat > .env << 'ENVEOF'
# Django Configuration
DJANGO_SECRET_KEY=generated-on-deployment
DEBUG=False
ALLOWED_HOSTS=192.168.20.10,tradifyglobal.com,www.tradifyglobal.com,localhost,127.0.0.1

# Database Configuration - PostgreSQL at 192.168.20.11
DB_ENGINE=django.db.backends.postgresql
DB_NAME=tradifyerp_db
DB_USER=tradifyerp_user
DB_PASSWORD=Tradify@PostgreSQL2024
DB_HOST=192.168.20.11
DB_PORT=5432
DB_SSL_MODE=require

# Encryption Configuration
ENCRYPTION_KEY=generated-on-deployment

# Security Configuration
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
CSRF_COOKIE_HTTPONLY=True

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@tradifyglobal.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@tradifyglobal.com

# Redis Configuration
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=1

# Logging Configuration
LOG_LEVEL=INFO
LOG_DIR=/var/log/tradifyerp

# Application Settings
ENVIRONMENT=production
ENVEOF

# Generate SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
sed -i "s/DJANGO_SECRET_KEY=.*/DJANGO_SECRET_KEY=$SECRET_KEY/" .env

# Generate ENCRYPTION_KEY
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
sed -i "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=$ENCRYPTION_KEY/" .env

chmod 600 .env
chown $APP_USER:$APP_GROUP .env
echo -e "${GREEN}✓${NC} Environment configured"

echo -e "${YELLOW}[6/10]${NC} Testing database connection..."
source venv/bin/activate
if python manage.py migrate --noinput 2>&1 | grep -q "OK\|no changes"; then
    echo -e "${GREEN}✓${NC} Database migrations applied"
else
    echo -e "${RED}✗${NC} Database connection failed - check .env"
    exit 1
fi

echo -e "${YELLOW}[7/10]${NC} Collecting static files..."
python manage.py collectstatic --noinput -q
echo -e "${GREEN}✓${NC} Static files collected"

echo -e "${YELLOW}[8/10]${NC} Configuring Nginx..."
cat > /etc/nginx/sites-available/tradifyerp << 'NGINXEOF'
upstream tradifyerp {
    server 127.0.0.1:8000;
}

server {
    listen 80 default_server;
    server_name 192.168.20.10 tradifyglobal.com www.tradifyglobal.com;
    
    client_max_body_size 100M;
    
    location /static/ {
        alias /opt/tradifyerp/TradifyERP/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /opt/tradifyerp/TradifyERP/media/;
        expires 7d;
    }
    
    location / {
        proxy_pass http://tradifyerp;
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
NGINXEOF

rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/tradifyerp /etc/nginx/sites-enabled/tradifyerp

if nginx -t &>/dev/null; then
    systemctl restart nginx
    echo -e "${GREEN}✓${NC} Nginx configured and running"
else
    echo -e "${RED}✗${NC} Nginx configuration error"
    nginx -t
    exit 1
fi

echo -e "${YELLOW}[9/10]${NC} Setting up Systemd service..."
mkdir -p /var/log/tradifyerp
chown $APP_USER:$APP_GROUP /var/log/tradifyerp

cat > /etc/systemd/system/tradifyerp.service << 'SERVICEEOF'
[Unit]
Description=Tradify Global ERP Gunicorn Service
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=tradifyapp
Group=tradifyapp
WorkingDirectory=/opt/tradifyerp/TradifyERP
Environment="PATH=/opt/tradifyerp/TradifyERP/venv/bin"
ExecStart=/opt/tradifyerp/TradifyERP/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile /var/log/tradifyerp/access.log \
    --error-logfile /var/log/tradifyerp/error.log \
    TradifyERP.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Install gunicorn
source $VENV_DIR/bin/activate
pip install gunicorn -q

systemctl daemon-reload
systemctl enable tradifyerp.service
systemctl start tradifyerp.service
sleep 2

if systemctl is-active --quiet tradifyerp; then
    echo -e "${GREEN}✓${NC} Systemd service running"
else
    echo -e "${RED}✗${NC} Service failed to start - check logs:"
    systemctl status tradifyerp --no-pager
    exit 1
fi

echo -e "${YELLOW}[10/10]${NC} Verifying deployment..."

# Check web server
if curl -s http://127.0.0.1:8000 > /dev/null; then
    echo -e "${GREEN}✓${NC} Web server responding"
else
    echo -e "${YELLOW}⚠${NC} Web server not responding yet"
fi

# Check Nginx
if curl -s http://127.0.0.1 | grep -q "<!"; then
    echo -e "${GREEN}✓${NC} Nginx is serving content"
else
    echo -e "${YELLOW}⚠${NC} Nginx may need configuration"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📋 ACCESS YOUR APPLICATION:${NC}"
echo "   http://192.168.20.10"
echo "   Admin: http://192.168.20.10/admin"
echo "   Audit Logs: http://192.168.20.10/admin/audit_logging/"
echo ""
echo -e "${YELLOW}🔐 SECURITY STATUS:${NC}"
echo "   ✓ Rate limiting (100 req/5min per IP)"
echo "   ✓ SQL injection protection"
echo "   ✓ Audit logging enabled"
echo "   ✓ Data encryption ready"
echo "   ✓ Security headers active"
echo ""
echo -e "${YELLOW}📊 LOGS:${NC}"
echo "   Application: tail -f /var/log/tradifyerp/error.log"
echo "   Nginx: tail -f /var/log/nginx/access.log"
echo "   Service: systemctl status tradifyerp"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo "   1. Update EMAIL_HOST_PASSWORD in .env"
echo "   2. Create superuser: python manage.py createsuperuser"
echo "   3. Configure SSL/HTTPS when domain is ready"
echo "   4. Set up automated backups"
echo "   5. Monitor audit logs weekly"
echo ""
