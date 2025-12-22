#!/bin/bash

# TradifyERP Complete Deployment Script
# Two-Server Architecture (Separate App & Database)
# Created: December 13, 2025

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_SERVER="192.168.20.10"
DB_SERVER="192.168.20.11"
APP_USER="zubair"
APP_DIR="/var/www/tradifyerp"
VENV_DIR="${APP_DIR}/venv"
LOCAL_PROJECT="/f/ERP-Production/Zubair-ERP-Project"

echo -e "${GREEN}"
echo "=========================================="
echo "TradifyERP Deployment Script"
echo "Two-Server Setup"
echo "=========================================="
echo -e "${NC}"

# Step 1: Verify Connectivity
echo -e "${YELLOW}[Step 1] Verifying server connectivity...${NC}"
echo "Testing App Server (${APP_SERVER})..."
ssh -o ConnectTimeout=10 zubair@${APP_SERVER} "echo 'App server OK'" || exit 1

echo "Testing DB Server (${DB_SERVER})..."
ssh -o ConnectTimeout=10 zubair@${DB_SERVER} "echo 'DB server OK'" || exit 1

echo -e "${GREEN}✓ Both servers are reachable${NC}"

# Step 2: Database Server Setup
echo -e "${YELLOW}[Step 2] Setting up PostgreSQL on database server...${NC}"
scp setup_postgresql_server.sh zubair@${DB_SERVER}:/tmp/
ssh zubair@${DB_SERVER} "chmod +x /tmp/setup_postgresql_server.sh && /tmp/setup_postgresql_server.sh"
echo -e "${GREEN}✓ PostgreSQL setup complete${NC}"

# Step 3: Application Server - Python & Dependencies
echo -e "${YELLOW}[Step 3] Setting up application server...${NC}"
scp setup_django_server.sh zubair@${APP_SERVER}:/tmp/
ssh zubair@${APP_SERVER} "chmod +x /tmp/setup_django_server.sh && /tmp/setup_django_server.sh"
echo -e "${GREEN}✓ Application server prepared${NC}"

# Step 4: Deploy Application Code
echo -e "${YELLOW}[Step 4] Deploying application code...${NC}"
echo "Creating application directory..."
ssh zubair@${APP_SERVER} "sudo mkdir -p ${APP_DIR} && sudo chown -R zubair:zubair ${APP_DIR}"

echo "Copying Django application files..."
scp -r ${LOCAL_PROJECT}/TradifyERP/* zubair@${APP_SERVER}:${APP_DIR}/
echo -e "${GREEN}✓ Application code deployed${NC}"

# Step 5: Install Python Requirements
echo -e "${YELLOW}[Step 5] Installing Python requirements...${NC}"
ssh zubair@${APP_SERVER} << 'INSTALLEOF'
source /var/www/tradifyerp/venv/bin/activate
pip install --upgrade pip
pip install psycopg2-binary
pip install gunicorn==23.0.0
pip install django==5.2.9
# Add more requirements as needed from requirements.txt
INSTALLEOF
echo -e "${GREEN}✓ Python requirements installed${NC}"

# Step 6: Configure Django Settings
echo -e "${YELLOW}[Step 6] Configuring Django settings for remote PostgreSQL...${NC}"
scp BACKUPS/postgres_checkpoint_2025-11-16_09-14-23/settings_production.py \
    zubair@${APP_SERVER}:${APP_DIR}/TradifyERP/settings_prod.py
echo -e "${GREEN}✓ Django settings configured${NC}"

# Step 7: Configure Nginx
echo -e "${YELLOW}[Step 7] Configuring Nginx...${NC}"
scp nginx_tradifyglobal_prod.conf zubair@${APP_SERVER}:/tmp/nginx_tradifyglobal.conf
ssh zubair@${APP_SERVER} << 'NGINXEOF'
sudo cp /tmp/nginx_tradifyglobal.conf /etc/nginx/sites-available/tradifyerp
sudo ln -sf /etc/nginx/sites-available/tradifyerp /etc/nginx/sites-enabled/tradifyerp
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
NGINXEOF
echo -e "${GREEN}✓ Nginx configured${NC}"

# Step 8: Database Migrations
echo -e "${YELLOW}[Step 8] Running Django migrations...${NC}"
ssh zubair@${APP_SERVER} << 'MIGRATIONEOF'
cd /var/www/tradifyerp
source /var/www/tradifyerp/venv/bin/activate
# Uncomment when ready:
# python manage.py migrate
MIGRATIONEOF
echo -e "${GREEN}✓ Migration script ready${NC}"

# Step 9: Collect Static Files
echo -e "${YELLOW}[Step 9] Collecting static files...${NC}"
ssh zubair@${APP_SERVER} << 'STATICEOF'
cd /var/www/tradifyerp
source /var/www/tradifyerp/venv/bin/activate
# Uncomment when ready:
# python manage.py collectstatic --noinput
STATICEOF
echo -e "${GREEN}✓ Static files collection ready${NC}"

# Step 10: Create Log Directory
echo -e "${YELLOW}[Step 10] Creating log directories...${NC}"
ssh zubair@${APP_SERVER} << 'LOGEOF'
sudo mkdir -p /var/log/tradifyerp
sudo chown -R zubair:www-data /var/log/tradifyerp
sudo chmod 755 /var/log/tradifyerp
LOGEOF
echo -e "${GREEN}✓ Log directories created${NC}"

# Step 11: Test Database Connection
echo -e "${YELLOW}[Step 11] Testing database connection...${NC}"
ssh zubair@${APP_SERVER} << 'TESTEOF'
source /var/www/tradifyerp/venv/bin/activate
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='192.168.20.11',
        database='tradify',
        user='zubair',
        password='zubair@0862'
    )
    print('✓ Database connection successful!')
    conn.close()
except Exception as e:
    print('✗ Database connection failed: ' + str(e))
    exit(1)
"
TESTEOF
echo -e "${GREEN}✓ Database connection verified${NC}"

echo -e "${GREEN}"
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo -e "${NC}"

echo ""
echo "Next Manual Steps:"
echo "1. SSH into app server: ssh zubair@${APP_SERVER}"
echo "2. Activate venv: source ${VENV_DIR}/bin/activate"
echo "3. Run migrations: python manage.py migrate"
echo "4. Create superuser: python manage.py createsuperuser"
echo "5. Collect static: python manage.py collectstatic --noinput"
echo "6. Import data: python manage.py loaddata prod_data_complete_backup.json"
echo "7. Start services:"
echo "   - sudo systemctl start gunicorn_tradifyerp"
echo "   - sudo systemctl start nginx"
echo "8. Test: curl http://localhost/ or visit http://${APP_SERVER}"
echo ""
echo "Database Details:"
echo "  Host: ${DB_SERVER}"
echo "  Database: tradify"
echo "  User: zubair"
echo "  Password: zubair@0862"
echo ""
echo "App Server Details:"
echo "  Address: ${APP_SERVER}"
echo "  User: ${APP_USER}"
echo "  App Dir: ${APP_DIR}"
echo ""
