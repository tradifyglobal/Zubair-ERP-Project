# PowerShell script to update server IPs on production environment
# App Server: 192.168.20.10
# Database Server: 192.168.20.11

Write-Host "======================================" -ForegroundColor Green
Write-Host "TradifyERP Server IP Update Script" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

$APP_SERVER = "192.168.20.10"
$DB_SERVER = "192.168.20.11"
$SSH_USER = "zubair"

Write-Host "`n[STEP 1] Updating App Server ($APP_SERVER)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Commands to run on app server
$APP_COMMANDS = @"
echo '=== Updating Django Settings ===' 
# Find and update settings files with new database IP
sudo find /var/www/tradifyerp -name 'settings*.py' -o -name 'local_settings.py' | xargs grep -l '192.168.2.59' 2>/dev/null

# Update settings.py
sudo sed -i "s/'HOST': '192.168.2.59'/'HOST': '192.168.20.11'/g" /var/www/tradifyerp/TradifyERP/settings.py 2>/dev/null || echo 'settings.py not found or already updated'

# Update local_settings.py if it exists
if [ -f /var/www/tradifyerp/local_settings.py ]; then
  sudo sed -i "s/'HOST': '192.168.2.59'/'HOST': '192.168.20.11'/g" /var/www/tradifyerp/local_settings.py
  echo 'Updated local_settings.py'
fi

# Update local_settings_prod.py if it exists
if [ -f /var/www/tradifyerp/local_settings_prod.py ]; then
  sudo sed -i "s/'HOST': '192.168.2.59'/'HOST': '192.168.20.11'/g" /var/www/tradifyerp/local_settings_prod.py
  echo 'Updated local_settings_prod.py'
fi

echo '=== Django settings updated ==='

echo '=== Restarting Gunicorn and Nginx ==='
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo '=== Checking service status ==='
sudo systemctl status gunicorn --no-pager
sudo systemctl status nginx --no-pager

echo '=== App Server Update Complete ==='
"@

# Execute commands on app server
Write-Host "Connecting to app server and executing commands..." -ForegroundColor Yellow
ssh -o StrictHostKeyChecking=no $SSH_USER@$APP_SERVER $APP_COMMANDS

Write-Host "`n[STEP 2] Updating Database Server ($DB_SERVER)" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Commands to run on database server
$DB_COMMANDS = @"
echo '=== Updating pg_hba.conf ==='
# Check current pg_hba.conf
echo 'Current pg_hba.conf entries for 192.168.2.69:'
sudo grep -n '192.168.2.69' /etc/postgresql/*/main/pg_hba.conf 2>/dev/null || echo 'No old entries found'

# Update pg_hba.conf - replace old app server IP with new one
sudo sed -i 's/192.168.2.69/192.168.20.10/g' /etc/postgresql/*/main/pg_hba.conf 2>/dev/null

# Add new entry if it doesn't exist
if ! sudo grep -q '192.168.20.10' /etc/postgresql/*/main/pg_hba.conf 2>/dev/null; then
  echo 'host    all    all    192.168.20.10/32    md5' | sudo tee -a /etc/postgresql/*/main/pg_hba.conf > /dev/null
fi

echo '=== pg_hba.conf updated ==='

echo '=== Reloading PostgreSQL ==='
sudo systemctl reload postgresql
sudo systemctl restart postgresql

echo '=== Checking PostgreSQL status ==='
sudo systemctl status postgresql --no-pager

echo '=== Database Server Update Complete ==='
"@

# Execute commands on database server
Write-Host "Connecting to database server and executing commands..." -ForegroundColor Yellow
ssh -o StrictHostKeyChecking=no $SSH_USER@$DB_SERVER $DB_COMMANDS

Write-Host "`n[STEP 3] Verifying Connectivity" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$VERIFY_COMMANDS = @"
echo '=== Testing Database Connectivity ==='
cd /var/www/tradifyerp
python manage.py dbshell < /dev/null && echo 'Database connection successful!' || echo 'Database connection failed!'

echo '=== Testing Django Configuration ==='
python manage.py check

echo '=== Verification Complete ==='
"@

Write-Host "Running verification on app server..." -ForegroundColor Yellow
ssh -o StrictHostKeyChecking=no $SSH_USER@$APP_SERVER $VERIFY_COMMANDS

Write-Host "`n======================================" -ForegroundColor Green
Write-Host "Server IP Update Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host "App Server: $APP_SERVER" -ForegroundColor Green
Write-Host "Database Server: $DB_SERVER" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
