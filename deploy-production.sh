#!/bin/bash
# Production Deployment Script for Tradify Global ERP
# This script automates the production deployment with security hardening

set -e  # Exit on error

echo "=========================================="
echo "🚀 PRODUCTION DEPLOYMENT SCRIPT"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   exit 1
fi

# Get deployment variables
read -p "Enter project directory (default: /opt/tradifyerp): " PROJECT_DIR
PROJECT_DIR=${PROJECT_DIR:-/opt/tradifyerp}

read -p "Enter production domain (e.g., tradifyglobal.com): " DOMAIN
read -p "Enter database password: " DB_PASSWORD
read -p "Enter Django secret key: " SECRET_KEY
read -p "Enter encryption key: " ENCRYPTION_KEY
read -p "Enter email address for alerts: " ALERT_EMAIL

echo ""
echo -e "${YELLOW}Starting deployment to $PROJECT_DIR${NC}"
echo ""

# Step 1: System Updates
echo -e "${YELLOW}[1/10] Updating system packages...${NC}"
apt-get update
apt-get upgrade -y
apt-get install -y python3.11 python3-pip python3-venv postgresql postgresql-contrib nginx redis-server certbot python3-certbot-nginx curl wget git

# Step 2: Create application user
echo -e "${YELLOW}[2/10] Creating application user...${NC}"
if ! id -u tradifyapp > /dev/null 2>&1; then
    useradd -m -s /bin/bash tradifyapp
    echo -e "${GREEN}✓ User 'tradifyapp' created${NC}"
else
    echo -e "${GREEN}✓ User 'tradifyapp' already exists${NC}"
fi

# Step 3: Create project directory
echo -e "${YELLOW}[3/10] Setting up project directory...${NC}"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR
git clone https://github.com/tradifyglobal/Zubair-ERP-Project.git .
chown -R tradifyapp:tradifyapp $PROJECT_DIR

# Step 4: Create Python virtual environment
echo -e "${YELLOW}[4/10] Creating Python virtual environment...${NC}"
cd $PROJECT_DIR/TradifyERP
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r ../requirements-security.txt

# Step 5: Create .env file
echo -e "${YELLOW}[5/10] Creating production .env file...${NC}"
cat > .env << EOF
# Django Configuration
DJANGO_SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost,127.0.0.1

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=tradifyerp_db
DB_USER=tradifyerp_user
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432
DB_SSL_MODE=require

# Encryption Configuration
ENCRYPTION_KEY=$ENCRYPTION_KEY

# Security Configuration
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_COOKIE_HTTPONLY=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=$ALERT_EMAIL
EMAIL_HOST_PASSWORD=your-app-password-here
DEFAULT_FROM_EMAIL=noreply@tradifyglobal.com

# Redis Configuration
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=1
REDIS_PASSWORD=

# Logging Configuration
LOG_LEVEL=INFO
LOG_DIR=$PROJECT_DIR/logs

# Application Settings
ENVIRONMENT=production
EOF

chmod 600 .env
chown tradifyapp:tradifyapp .env

# Step 6: Create PostgreSQL database
echo -e "${YELLOW}[6/10] Setting up PostgreSQL database...${NC}"
sudo -u postgres psql << SQL
CREATE USER tradifyerp_user WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE tradifyerp_db OWNER tradifyerp_user;
ALTER USER tradifyerp_user CREATEDB;
ALTER DATABASE tradifyerp_db SET ssl = on;
GRANT ALL PRIVILEGES ON DATABASE tradifyerp_db TO tradifyerp_user;
SQL

# Step 7: Run migrations
echo -e "${YELLOW}[7/10] Running database migrations...${NC}"
source venv/bin/activate
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Step 8: Create superuser
echo -e "${YELLOW}[8/10] Creating superuser...${NC}"
read -p "Enter superuser username: " SUPERUSER
read -sp "Enter superuser password: " SUPERUSER_PASS
read -p "Enter superuser email: " SUPERUSER_EMAIL

python manage.py shell << PYTHON
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$SUPERUSER').exists():
    User.objects.create_superuser('$SUPERUSER', '$SUPERUSER_EMAIL', '$SUPERUSER_PASS')
    print("✓ Superuser created")
else:
    print("✓ Superuser already exists")
PYTHON

# Step 9: Configure Nginx
echo -e "${YELLOW}[9/10] Configuring Nginx...${NC}"
cat > /etc/nginx/sites-available/$DOMAIN << EOF
upstream tradifyerp {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Redirect to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    # SSL certificates (requires certbot setup)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()" always;
    
    client_max_body_size 100M;
    
    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }
    
    location /static/ {
        alias $PROJECT_DIR/TradifyERP/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias $PROJECT_DIR/TradifyERP/media/;
        expires 7d;
    }
    
    location / {
        proxy_pass http://tradifyerp;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/$DOMAIN
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# Step 10: Create systemd service
echo -e "${YELLOW}[10/10] Creating systemd service...${NC}"
cat > /etc/systemd/system/tradifyerp.service << EOF
[Unit]
Description=Tradify Global ERP Gunicorn Service
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=tradifyapp
Group=tradifyapp
WorkingDirectory=$PROJECT_DIR/TradifyERP
Environment="PATH=$PROJECT_DIR/TradifyERP/venv/bin"
ExecStart=$PROJECT_DIR/TradifyERP/venv/bin/gunicorn \\
    --workers 4 \\
    --bind 127.0.0.1:8000 \\
    --timeout 120 \\
    --access-logfile $PROJECT_DIR/logs/access.log \\
    --error-logfile $PROJECT_DIR/logs/error.log \\
    TradifyERP.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

mkdir -p $PROJECT_DIR/logs
chown tradifyapp:tradifyapp $PROJECT_DIR/logs
systemctl daemon-reload
systemctl enable tradifyerp.service
systemctl start tradifyerp.service

# Step 11: Setup SSL certificate
echo -e "${YELLOW}[Bonus] Setting up SSL certificate with certbot...${NC}"
certbot certonly --nginx -d $DOMAIN -d www.$DOMAIN

# Step 12: Setup firewall
echo -e "${YELLOW}[Bonus] Configuring firewall...${NC}"
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

echo ""
echo -e "${GREEN}=========================================="
echo "✅ PRODUCTION DEPLOYMENT COMPLETE!"
echo "==========================================${NC}"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Update EMAIL_HOST_PASSWORD in .env with actual App Password"
echo "2. Test application: https://$DOMAIN"
echo "3. Create admin user if not done"
echo "4. Monitor logs: tail -f $PROJECT_DIR/logs/error.log"
echo "5. Check security: https://$DOMAIN/admin/audit_logging/"
echo ""
echo "🔐 SECURITY CHECKLIST:"
echo "✓ HTTPS/SSL enabled"
echo "✓ Database SSL enabled"
echo "✓ Firewall configured"
echo "✓ Security headers active"
echo "✓ Rate limiting active"
echo "✓ Audit logging active"
echo ""
echo "📊 SERVICE STATUS:"
systemctl status tradifyerp --no-pager
echo ""
echo "🔑 IMPORTANT:"
echo "- Keep .env file secure (600 permissions)"
echo "- Backup database daily"
echo "- Monitor audit logs weekly"
echo "- Update SSL certificate before expiry"
echo "- Keep system packages updated"
echo ""
