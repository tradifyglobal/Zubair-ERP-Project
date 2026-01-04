# 🚀 DEPLOYMENT READY - DO THIS NOW

## Your Servers
```
Web Server (App):  192.168.20.10  (SSH: zubair/erp, Sudo: erp)
Database Server:   192.168.20.11  (SSH: zubair/sql, Sudo: sql)
```

---

## Deploy in 3 Simple Steps

### STEP 1: SSH to Web Server

Open terminal/PowerShell and run:
```bash
ssh zubair@192.168.20.10
```
When prompted for password, type: `erp`

### STEP 2: Switch to Root

```bash
sudo su
```
When prompted, type: `erp`

### STEP 3: Run Deployment Script

```bash
cd /tmp
wget https://raw.githubusercontent.com/tradifyglobal/Zubair-ERP-Project/changes/deploy-server.sh
chmod +x deploy-server.sh
bash deploy-server.sh
```

**⏱️ Wait 5-10 minutes** for the script to complete

---

## After Deployment

### Access Your Application

Open web browser and go to:
```
http://192.168.20.10
```

### Access Admin Panel

```
URL: http://192.168.20.10/admin
```

### Create Admin User

After deployment completes, the script will prompt you to create a superuser. Follow it:
```
Username: admin
Email: your-email@tradifyglobal.com
Password: (enter a strong password)
```

### View Audit Logs

```
http://192.168.20.10/admin/audit_logging/
```

---

## What Gets Installed

✅ Python 3.11 + Django 5.2  
✅ PostgreSQL client (connects to 192.168.20.11)  
✅ Nginx web server  
✅ Redis cache  
✅ Gunicorn application server  
✅ All security features  
✅ Audit logging system  
✅ Rate limiting  
✅ SQL injection protection  

---

## Verify Everything Works

After deployment, SSH to web server and run:

```bash
# Check service is running
sudo systemctl status tradifyerp

# Should show: ● tradifyerp.service - Tradify Global ERP Gunicorn Service
#              Loaded: loaded (/etc/systemd/system/tradifyerp.service; enabled; vendor preset: enabled)
#              Active: active (running) since ...

# Check logs for errors
tail -f /var/log/tradifyerp/error.log

# Should show: Started server process [1234]
#              Application startup complete
```

---

## Troubleshooting

### If service won't start:
```bash
# Check what went wrong
sudo journalctl -u tradifyerp -n 30

# Check if database is reachable
psql -h 192.168.20.11 -U tradifyerp_user -d tradifyerp_db
# Password: Tradify@PostgreSQL2024
```

### If database connection fails:
```bash
# Verify PostgreSQL server is running
# SSH to 192.168.20.11 and check:
sudo systemctl status postgresql

# Check credentials in .env
sudo cat /opt/tradifyerp/TradifyERP/.env | grep DB_
```

### If static files don't load:
```bash
# Recollect them
cd /opt/tradifyerp/TradifyERP
source venv/bin/activate
python manage.py collectstatic --noinput --clear

# Restart service
sudo systemctl restart tradifyerp
```

---

## Quick Reference

### View Logs
```bash
tail -f /var/log/tradifyerp/error.log          # Application errors
tail -f /var/log/tradifyerp/access.log         # Access logs
tail -f /var/log/nginx/access.log              # Nginx logs
```

### Restart Service
```bash
sudo systemctl restart tradifyerp
```

### Check Service Status
```bash
sudo systemctl status tradifyerp
```

### Edit Configuration
```bash
sudo nano /opt/tradifyerp/TradifyERP/.env
# After editing, restart:
sudo systemctl restart tradifyerp
```

---

## Security Features

Your deployment includes:

| Feature | Status | Details |
|---------|--------|---------|
| Audit Logging | ✅ Active | All user actions tracked |
| Rate Limiting | ✅ Active | 100 req/5min per IP |
| SQL Injection | ✅ Active | Auto-detection & blocking |
| Data Encryption | ✅ Ready | Available for use |
| Security Headers | ✅ Active | HSTS, CSP, X-Frame-Options |
| Django Admin | ✅ Active | Full monitoring dashboard |
| HTTPS | ⏳ Optional | Set up when domain ready |

---

## Deployment Timeline

| Step | Time | Status |
|------|------|--------|
| System prep | 1 min | Automatic |
| Package install | 2 min | Automatic |
| Code clone | 1 min | Automatic |
| Env setup | 1 min | Automatic |
| Database migration | 2 min | Automatic |
| Static files | 1 min | Automatic |
| Nginx config | 1 min | Automatic |
| Service start | 1 min | Automatic |
| **Total** | **~10 min** | **DONE!** |

---

## Important Notes

1. **Database Password:** `Tradify@PostgreSQL2024` (already configured)
2. **App User:** `tradifyapp` (created automatically)
3. **Project Location:** `/opt/tradifyerp/`
4. **Logs Location:** `/var/log/tradifyerp/`
5. **Configuration:** `/opt/tradifyerp/TradifyERP/.env`

---

## Next Steps (After Deployment)

1. ✅ Test application: http://192.168.20.10
2. ✅ Login to admin: http://192.168.20.10/admin
3. ⏳ Update EMAIL_HOST_PASSWORD in .env (for email alerts)
4. ⏳ Set up automated backups
5. ⏳ Configure HTTPS (when domain available)
6. ⏳ Monitor audit logs weekly

---

## Support

### Need Help?

1. **Check logs:**
   ```bash
   tail -f /var/log/tradifyerp/error.log
   ```

2. **Verify connection to DB:**
   ```bash
   psql -h 192.168.20.11 -U tradifyerp_user -d tradifyerp_db
   ```

3. **Restart service:**
   ```bash
   sudo systemctl restart tradifyerp
   ```

4. **Check admin panel:**
   ```
   http://192.168.20.10/admin
   ```

---

## Ready to Deploy?

### Copy & Paste This Command:

```bash
ssh zubair@192.168.20.10 && sudo su && cd /tmp && wget https://raw.githubusercontent.com/tradifyglobal/Zubair-ERP-Project/changes/deploy-server.sh && chmod +x deploy-server.sh && bash deploy-server.sh
```

**Then enter passwords when prompted:**
- SSH Password: `erp`
- Sudo Password: `erp`

---

**Status: ✅ PRODUCTION DEPLOYMENT READY**

**Estimated Time: 10 minutes**

**Go Deploy! 🚀**
