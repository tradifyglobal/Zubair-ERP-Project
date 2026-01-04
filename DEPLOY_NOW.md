# Production Deployment - Web Server 192.168.20.10 & DB Server 192.168.20.11

## Server Details

### Web Server (Application)
```
IP Address: 192.168.20.10
SSH User: zubair
SSH Password: erp
Sudo Password: erp
OS: Ubuntu/Debian Linux
```

### Database Server (PostgreSQL)
```
IP Address: 192.168.20.11
SSH User: zubair
SSH Password: sql
Sudo Password: sql
Database: PostgreSQL
Database Name: tradifyerp_db
Database User: tradifyerp_user
Database Password: Tradify@PostgreSQL2024
```

---

## Quick Start - Deploy Now!

### Option 1: Automated Deployment (Recommended)

**From your Windows machine:**

```powershell
# Navigate to project
cd F:\ERP-Production\Zubair-ERP-Project

# Ensure code is committed
git add -A
git commit -m "Ready for production deployment"
git push origin changes

# Run Python deployment script (requires sshpass installed)
# Install sshpass: choco install sshpass -y

python deploy.py
```

### Option 2: Manual Deployment

**Step 1: SSH to Web Server**
```bash
ssh zubair@192.168.20.10
# Password: erp
```

**Step 2: Switch to Root**
```bash
sudo su
# Password: erp
```

**Step 3: Run Deployment Script**
```bash
cd /tmp
wget https://raw.githubusercontent.com/tradifyglobal/Zubair-ERP-Project/changes/deploy-server.sh
chmod +x deploy-server.sh
bash deploy-server.sh

# Wait 5-10 minutes for completion
```

**Step 4: Verify Installation**
```bash
# Check service status
sudo systemctl status tradifyerp

# Check application
curl http://127.0.0.1

# Check logs
tail -f /var/log/tradifyerp/error.log
```

**Step 5: Create Admin User**
```bash
cd /opt/tradifyerp/TradifyERP
source venv/bin/activate
python manage.py createsuperuser

# Enter:
# Username: admin
# Email: admin@tradifyglobal.com
# Password: (secure password)
```

---

## Access Application

### URLs
```
Application: http://192.168.20.10
Admin Panel: http://192.168.20.10/admin
Audit Logs: http://192.168.20.10/admin/audit_logging/
```

### Default Admin Account
```
Username: admin
Password: (created in Step 5 above)
```

---

## Verification Checklist

After deployment, verify everything works:

```bash
# SSH to web server
ssh zubair@192.168.20.10

# 1. Check service is running
sudo systemctl status tradifyerp
# Should show: active (running)

# 2. Check Nginx is running
sudo systemctl status nginx
# Should show: active (running)

# 3. Check Redis is running
sudo systemctl status redis-server
# Should show: active (running)

# 4. Test database connection
cd /opt/tradifyerp/TradifyERP
source venv/bin/activate
python manage.py dbshell
# Should connect, then type: \q to exit

# 5. Check static files are collected
ls -la /opt/tradifyerp/TradifyERP/staticfiles/
# Should show admin, rest_framework directories

# 6. Monitor logs for errors
tail -f /var/log/tradifyerp/error.log
# Should show: Started Gunicorn... (no errors)

# 7. Test web server with curl
curl -I http://127.0.0.1
# Should return: HTTP/1.1 200 OK
```

---

## Security Features Active

After deployment, you have:

✅ **Audit Logging** - All user actions tracked
✅ **Rate Limiting** - 100 requests/5 min per IP
✅ **SQL Injection Protection** - Automatic detection
✅ **Data Encryption** - Ready to use
✅ **Security Headers** - Active on all responses
✅ **Django Admin** - Full monitoring dashboard
✅ **Redis Caching** - Performance optimization
✅ **Nginx Reverse Proxy** - Load balancing ready

---

## Common Issues & Solutions

### Issue: Service won't start

```bash
# Check logs
sudo journalctl -u tradifyerp -n 20

# Try manual start
cd /opt/tradifyerp/TradifyERP
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# If it works, restart service
sudo systemctl restart tradifyerp
```

### Issue: Database connection error

```bash
# Test connection to DB server
telnet 192.168.20.11 5432

# Check credentials in .env
sudo cat /opt/tradifyerp/TradifyERP/.env | grep DB_

# Test PostgreSQL manually
psql -h 192.168.20.11 -U tradifyerp_user -d tradifyerp_db
# Password: Tradify@PostgreSQL2024
```

### Issue: Static files not loading

```bash
# Recollect static files
cd /opt/tradifyerp/TradifyERP
source venv/bin/activate
python manage.py collectstatic --noinput --clear

# Check permissions
sudo chown -R tradifyapp:tradifyapp /opt/tradifyerp/TradifyERP/staticfiles

# Restart service
sudo systemctl restart tradifyerp
```

### Issue: Port 8000 already in use

```bash
# Find what's using port 8000
sudo lsof -i :8000

# Kill the process (get PID from above)
sudo kill -9 <PID>

# Restart service
sudo systemctl restart tradifyerp
```

---

## Configuration Files

### .env Location
```
/opt/tradifyerp/TradifyERP/.env
```

### Edit Configuration
```bash
sudo nano /opt/tradifyerp/TradifyERP/.env

# After editing, restart service
sudo systemctl restart tradifyerp
```

### Important Settings
```
# Debug Mode (should be False in production)
DEBUG=False

# Database
DB_HOST=192.168.20.11
DB_NAME=tradifyerp_db
DB_USER=tradifyerp_user
DB_PASSWORD=Tradify@PostgreSQL2024

# Email (update if you have your own SMTP)
EMAIL_HOST_USER=noreply@tradifyglobal.com
EMAIL_HOST_PASSWORD=your-app-password

# Security
SECURE_SSL_REDIRECT=False  # Change to True when HTTPS ready
DEBUG=False
```

---

## Monitoring & Logs

### View Real-time Logs
```bash
# Application errors
tail -f /var/log/tradifyerp/error.log

# Access logs
tail -f /var/log/tradifyerp/access.log

# Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# System
sudo journalctl -u tradifyerp -f
```

### Check Service Status
```bash
# Service status
sudo systemctl status tradifyerp

# View full logs
sudo systemctl status tradifyerp --no-pager

# Restart service
sudo systemctl restart tradifyerp

# Stop service
sudo systemctl stop tradifyerp

# Start service
sudo systemctl start tradifyerp
```

---

## Maintenance

### Daily
```bash
# Check service is running
sudo systemctl status tradifyerp

# Check logs for errors
tail /var/log/tradifyerp/error.log
```

### Weekly
```bash
# Review audit logs via admin panel
# http://192.168.20.10/admin/audit_logging/

# Check security events
# Look for failed logins, rate limit violations, etc.

# Check system resources
free -h  # Memory
df -h    # Disk space
top -b -n 1  # CPU usage
```

### Monthly
```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade

# Update Python packages
cd /opt/tradifyerp/TradifyERP
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Database maintenance
sudo -u postgres vacuumdb tradifyerp_db
```

---

## Backup & Recovery

### Manual Backup
```bash
# SSH to web server
ssh zubair@192.168.20.10

# Create backup directory
mkdir -p /backups

# Backup database
pg_dump -h 192.168.20.11 -U tradifyerp_user tradifyerp_db > /backups/tradifyerp_$(date +%Y%m%d_%H%M%S).sql

# Backup application files
tar -czf /backups/tradifyerp_app_$(date +%Y%m%d).tar.gz /opt/tradifyerp
```

### Restore Database
```bash
# Restore from backup
psql -h 192.168.20.11 -U tradifyerp_user tradifyerp_db < /backups/tradifyerp_YYYYMMDD_HHMMSS.sql
```

---

## SSL/HTTPS Setup (Optional - For Future)

When you have a domain name, enable HTTPS:

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate (requires domain)
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Update .env
sudo nano /opt/tradifyerp/TradifyERP/.env
# Change: SECURE_SSL_REDIRECT=True
# Change: SESSION_COOKIE_SECURE=True

# Restart
sudo systemctl restart tradifyerp nginx
```

---

## Support

### Check Everything is Working
```bash
# Go to: http://192.168.20.10
# You should see the ERP application

# Check Admin: http://192.168.20.10/admin
# Login with admin credentials created earlier

# Check Audit Logs: http://192.168.20.10/admin/audit_logging/
# Should show audit logs and security events
```

### Get Help
```bash
# Check error logs
sudo tail -50 /var/log/tradifyerp/error.log

# Check service status
sudo systemctl status tradifyerp -n 50

# Restart service to clear temporary issues
sudo systemctl restart tradifyerp

# SSH to get more info
ssh zubair@192.168.20.10
```

---

**Deployment Date:** January 4, 2026  
**Status:** READY FOR PRODUCTION  
**Estimated Setup Time:** 5-10 minutes
