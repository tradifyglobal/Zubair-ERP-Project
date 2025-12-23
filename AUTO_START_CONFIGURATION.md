# ERP System Auto-Start Configuration Guide
**Date**: December 23, 2025  
**Status**: ✓ PERMANENT AUTO-START ENABLED

---

## Overview
The ERP system is now configured to automatically start all required services even after server reboots. The application will maintain its database connection permanently.

---

## System Configuration

### Database Server (192.168.20.11)

#### PostgreSQL Service Status
```
Service Name:    postgresql@16-main
Unit File State: enabled
Current Status:  active (running)
Auto-Start:      ✓ YES - Will start on reboot
Port:            5432 (listening on 0.0.0.0:5432 and [::]:5432)
```

**Systemd Configuration:**
- Service symlink: `/etc/systemd/system/multi-user.target.wants/postgresql@16-main.service`
- Service unit: `/usr/lib/systemd/system/postgresql@.service`
- Preset: enabled (auto-starts with multi-user.target)

---

### App Server (192.168.20.10)

#### Gunicorn Service Status
```
Service Name:    gunicorn
Unit File State: enabled
Current Status:  active (running)
Auto-Start:      ✓ YES - Will start on reboot
Port:            8000 (listening on 127.0.0.1:8000)
Workers:         2
Configuration:   /etc/systemd/system/gunicorn.service
```

#### Nginx Service Status
```
Service Name:    nginx
Unit File State: enabled
Current Status:  active (running)
Auto-Start:      ✓ YES - Will start on reboot
Port:            80 (listening on 0.0.0.0:80)
Configuration:   /etc/systemd/system/nginx.service
```

#### Health Check Service (Optional)
```
Service Name:    erp-health-check
Unit File State: enabled
Type:            oneshot
Purpose:         Verify system health after reboot
Runs After:      network-online.target
Logs To:         /var/log/erp_startup_health.log
```

---

## Reboot Behavior

### Single Server Reboot

**Database Server Only (192.168.20.11) Reboot:**
1. Server starts → PostgreSQL@16-main auto-starts (~5-10 seconds)
2. Database becomes available on port 5432
3. App server will auto-reconnect to database
4. Users maintain connection if session is persistent

**App Server Only (192.168.20.10) Reboot:**
1. Server starts → Nginx auto-starts (~3-5 seconds)
2. Server continues → Gunicorn auto-starts (~5-10 seconds)
3. Gunicorn tries to connect to PostgreSQL (already running on DB server)
4. Connection established immediately

---

### Both Servers Reboot Simultaneously

**Reboot Sequence:**
```
0:00  Database Server starts
0:05  PostgreSQL@16-main starts ✓
0:10  App Server starts
0:13  Nginx starts ✓
0:15  Gunicorn starts ✓
0:18  Gunicorn connects to PostgreSQL ✓
0:20  ERP System FULLY OPERATIONAL
```

**Expected Timeline:** 20-60 seconds total recovery time

---

## Verification Commands

### Check Auto-Start Status

**Database Server:**
```bash
ssh zubair@192.168.20.11
sudo systemctl is-enabled postgresql@16-main
# Output: enabled
```

**App Server:**
```bash
ssh zubair@192.168.20.10
systemctl is-enabled gunicorn
systemctl is-enabled nginx
# Output: enabled (for both)
```

### Check Current Service Status

**Database Server:**
```bash
ssh zubair@192.168.20.11
systemctl status postgresql@16-main
sudo ss -tlnp | grep 5432
```

**App Server:**
```bash
ssh zubair@192.168.20.10
systemctl status gunicorn
systemctl status nginx
ss -tlnp | grep -E '8000|80'
```

### Test Database Connectivity

**From App Server:**
```bash
ssh zubair@192.168.20.10
python3 << 'EOF'
import psycopg2
try:
    conn = psycopg2.connect(
        host='192.168.20.11',
        port='5432',
        user='tradifyerp_user',
        password='Tradify@PostgreSQL2024',
        database='tradifyerp_db'
    )
    print("✓ Database connection successful")
    conn.close()
except Exception as e:
    print(f"✗ Connection failed: {e}")
EOF
```

---

## Health Check Script

A health check script is configured to run automatically after server reboot.

**Script Location:** `/usr/local/bin/health_check_startup.sh`  
**Log File:** `/var/log/erp_startup_health.log`

**Manual Run:**
```bash
ssh zubair@192.168.20.10
sudo /usr/local/bin/health_check_startup.sh
```

**Check Startup Logs:**
```bash
ssh zubair@192.168.20.10
sudo journalctl -u erp-health-check -n 50
```

---

## Configuration Files

### PostgreSQL Configuration

**Config Files:**
- `/etc/postgresql/16/main/postgresql.conf` - Main PostgreSQL config
- `/etc/postgresql/16/main/pg_hba.conf` - Authentication config (✓ FIXED: md5sql → md5)

**Important Setting:**
```
LISTEN_ADDRESSES = '*'  # PostgreSQL listens on all interfaces
PORT = 5432
```

### Gunicorn Configuration

**Service Unit:** `/etc/systemd/system/gunicorn.service`  
**Environment:** `/var/www/tradifyerp/venv/bin/python3.12`  
**Settings:**
- Workers: 2
- Bind: 127.0.0.1:8000
- Timeout: 300 seconds
- WSGI: TradifyERP.wsgi:application

### Nginx Configuration

**Config File:** `/etc/nginx/sites-enabled/tradifyerp` (or similar)  
**Proxy To:** http://127.0.0.1:8000 (Gunicorn)  
**Listen:** 0.0.0.0:80

### Django Database Configuration

**File:** `/var/www/tradifyerp/TradifyERP/settings_production.py`  
**Database Connection:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tradifyerp_db',
        'USER': 'tradifyerp_user',
        'PASSWORD': 'Tradify@PostgreSQL2024',
        'HOST': '192.168.20.11',  # Database server IP
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,  # Connection pooling (10 minutes)
    }
}
```

---

## Troubleshooting

### If Services Don't Auto-Start After Reboot

**1. Check Service Status:**
```bash
ssh zubair@192.168.20.10
sudo systemctl status gunicorn
sudo systemctl status nginx
```

**2. Enable Services If Disabled:**
```bash
ssh zubair@192.168.20.10
sudo systemctl enable gunicorn
sudo systemctl enable nginx
```

**3. Check systemd Logs:**
```bash
journalctl -u gunicorn -n 50
journalctl -u nginx -n 50
```

### If Database Connection Fails After Reboot

**1. Check PostgreSQL:**
```bash
ssh zubair@192.168.20.11
systemctl status postgresql@16-main
sudo ss -tlnp | grep 5432
```

**2. Enable PostgreSQL if Disabled:**
```bash
ssh zubair@192.168.20.11
sudo systemctl enable postgresql@16-main
sudo systemctl start postgresql@16-main
```

**3. Check pg_hba.conf for syntax errors:**
```bash
ssh zubair@192.168.20.11
sudo tail -20 /etc/postgresql/16/main/postgresql.conf
```

**4. Check PostgreSQL logs:**
```bash
ssh zubair@192.168.20.11
sudo tail -50 /var/log/postgresql/postgresql-16-main.log
```

---

## Network Verification

### Port Listening Verification

**Database Server Ports:**
```bash
ssh zubair@192.168.20.11
sudo ss -tlnp | grep 5432
# Should show: LISTEN 0.0.0.0:5432 and [::]:5432
```

**App Server Ports:**
```bash
ssh zubair@192.168.20.10
ss -tlnp | grep -E ':80|:8000'
# Should show both ports listening
```

### Network Path Verification

```bash
# From app server to database
ssh zubair@192.168.20.10
ping -c 3 192.168.20.11
nc -zv 192.168.20.11 5432
```

---

## Monitoring & Alerts

### Enable Systemd Notifications

To get alerts if a service fails to start:

```bash
# Check if notification email is configured
sudo systemctl cat gunicorn | grep -i onFailure
```

### View Service Logs

```bash
# Real-time gunicorn logs
sudo journalctl -u gunicorn -f

# Real-time nginx logs
sudo journalctl -u nginx -f

# PostgreSQL error logs
sudo tail -f /var/log/postgresql/postgresql-16-main.log
```

---

## Summary

✅ **All services configured for permanent auto-start**
- PostgreSQL: enabled
- Gunicorn: enabled
- Nginx: enabled
- Health Check: enabled

✅ **Tested and verified to auto-start on reboot**

✅ **Database and app connection will persist through restarts**

✅ **Expected recovery time: 20-60 seconds after server reboot**

---

*Last Updated: December 23, 2025*  
*Configuration Status: PRODUCTION READY*
