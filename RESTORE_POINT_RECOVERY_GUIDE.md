# TradifyERP - Restore Point & Recovery Plan
**Created**: April 7, 2026  
**Purpose**: Safe rollback point before major enhancements

---

## 📦 BACKUP SNAPSHOTS CREATED

### 1. App Server Backup
**File**: `tradifyerp_backup_2026-04-07_pre-enhancement.tar.gz`
- **Location**: `/backups/restore_points/` on App Server (192.168.20.10)
- **Size**: 44 MB (compressed, excludes venv & cache)
- **Contents**:
  - All Django application code
  - All 14 ERP modules
  - All configuration files (settings.py, urls.py, etc.)
  - All templates and static files
  - Database migrations
  - Management scripts
  - User uploaded media files
  
- **Excludes** (not backed up):
  - Python virtual environment (venv/) - can be reinstalled
  - Python cache (__pycache__) - regenerated automatically
  - .git directory - version control history

**Status**: ✅ **COMPLETED** - Ready for restore

---

### 2. Database Backup
**Creating SQL dump of tradifyerp_db...**

**Backup Location**: App Server at  `/backups/restore_points/`
**Database**: tradifyerp_db
**Database User**: zubair
**Size**: Will depend on data volume

**Why Full Data Backup Is Critical**:
- Preserves all financial records, transactions, customer data
- Allows point-in-time recovery
- Eliminates need to re-enter historical data
- Required for compliance and audit trails

---

## 🔄 HOW TO RESTORE FROM BACKUP

### Option 1: Restore App Server Code & Configuration

**Step 1: SSH to App Server**
```powershell
ssh root@192.168.20.10
```

**Step 2: Stop Gunicorn Service**
```bash
sudo systemctl stop gunicorn
```

**Step 3: Backup Current Code (Optional but recommended)**
```bash
cd /var/www
tar -czf tradifyerp_backup_current.tar.gz tradifyerp/
```

**Step 4: Extract Restore Point**
```bash
cd /var/www
rm -rf tradifyerp/  # Remove current version
tar -xzf /backups/restore_points/tradifyerp_backup_2026-04-07_pre-enhancement.tar.gz
cd tradifyerp
```

**Step 5: Reinstall Virtual Environment (if needed)**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # If requirements.txt exists
# OR reinstall from pip list
pip install Django==5.2.9 djangorestframework==3.14.0 gunicorn==23.0.0 psycopg2-binary==2.9.9 ...
```

**Step 6: Run Migrations (if database schema changed)**
```bash
python manage.py migrate --settings=TradifyERP.settings_production
```

**Step 7: Restart Services**
```bash
sudo systemctl start gunicorn
sudo systemctl restart nginx
```

**Step 8: Verify**
```bash
curl http://localhost:80  # Check Nginx is responding
systemctl status gunicorn
```

---

### Option 2: Restore Database (tradifyerp_db)

**Prerequisites**: 
- Database backup file in SQL format
- PostgreSQL access on DB server

**Step 1: SSH to DB Server**
```powershell
ssh zubair@192.168.20.11
```

**Step 2: Create a New Database (if current is corrupted)**
```bash
sudo -u postgres createdb tradifyerp_db_restored
```

**Step 3: Restore from SQL Backup**
```bash
# If backup is SQL file:
cat tradifyerp_db_backup_2026-04-07_pre-enhancement.sql | psql -h localhost -U zubair tradifyerp_db

# If backup is compressed:
gunzip -c tradifyerp_db_backup_2026-04-07_pre-enhancement.sql.gz | psql -h localhost -U zubair tradifyerp_db
```

**Step 4: Verify Restoration**
```bash
psql -h localhost -U zubair -d tradifyerp_db -c "SELECT COUNT(*) FROM information_schema.tables;"
```

**Step 5: Drop Old Database (if successful)**
```bash
sudo -u postgres dropdb tradifyerp_db_old
```

---

### Option 3: Complete System Restore

**Restore both app server AND database in sequence**:

1. Follow **Option 1** (Restore App Server)
2. Follow **Option 2** (Restore Database)
3. Test full application flow
4. Verify all modules are working

---

### Option 4: Emergency Rollback (Quickest)

**If everything is broken and you need fast recovery:**

```powershell
# From your Windows machine:
ssh root@192.168.20.10

# On app server:
cd /var/www
rm -rf tradifyerp/
tar -xzf /backups/restore_points/tradifyerp_backup_2026-04-07_pre-enhancement.tar.gz

sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

**Expected Time**: 2-5 minutes

---

## 📋 RESTORE CHECKLIST

### Before Starting Restore
- [ ] You have SSH access to both servers
- [ ] You have passwordless SSH configured (or know passwords)
- [ ] You have a backup copy of current code (RECOMMENDED)
- [ ] All users are notified of maintenance window

### After Restore
- [ ] Gunicorn service is running: `systemctl status gunicorn`
- [ ] Nginx is running: `systemctl status nginx`
- [ ] Database connection works: `psql -h 192.168.20.11 -U zubair -d tradifyerp_db -c "SELECT 1;"`
- [ ] Application loads in browser
- [ ] All 14 modules load correctly
- [ ] Sample transaction can be created and saved
- [ ] No ERROR messages in logs

### Verify Restore Success

```powershell
# Check application is accessible
curl http://192.168.20.10/admin/  # Should show login page

# Check database
psql -h 192.168.20.11 -U zubair -d tradifyerp_db -c "SELECT version();"

# Check application logs
ssh root@192.168.20.10 "tail -50 /var/log/gunicorn/error.log"
```

---

## 🛠️ RESTORE SCRIPTS (One-Liners)

### Quick App Server Restore
```bash
cd /var/www && rm -rf tradifyerp && tar -xzf /backups/restore_points/tradifyerp_backup_2026-04-07_pre-enhancement.tar.gz && systemctl restart gunicorn nginx
```

### Quick Database Restore
```bash
psql -h localhost -U zubair -d tradifyerp_db < /path/to/backup.sql
```

---

## 💾 BACKUP VERIFICATION

### App Server Backup
```powershell
ssh root@192.168.20.10

# Check backup exists
ls -lh /backups/restore_points/tradifyerp_backup_2026-04-07_pre-enhancement.tar.gz

# Verify integrity
tar -tzf /backups/restore_points/tradifyerp_backup_2026-04-07_pre-enhancement.tar.gz | head -20

# Check size
du -sh /backups/restore_points/tradifyerp_backup_2026-04-07_pre-enhancement.tar.gz
```

### Database Backup  
```powershell
ssh zubair@192.168.20.11

# Check backup exists
ls -lh ~/backups/tradifyerp_db_backup_*.sql

# Check if SQL file has data
wc -l ~/backups/tradifyerp_db_backup_*.sql
head -20 ~/backups/tradifyerp_db_backup_*.sql
```

---

## 📊 BACKUP SUMMARY

| Component | Backup Method | Location | Size | Status | Restore Time |
|-----------|---------------|----------|------|--------|--------------|
| **App Code & Config** | tar.gz archiv | `/backups/restore_points/` | 44 MB | ✅ Ready | 2-5 min |
| **Database (SQL Dump)** | pg_dump SQL | `/backups/restore_points/` | TBD | 🔄 In Progress | 5-15 min |
| **Database (WAL)** | PostgreSQL WAL | `/var/lib/postgresql/16/` | Live | Continuous | - |
| **Static Files** | Included in tar.gz | `/backups/restore_points/` | Included | ✅ Ready | - |

---

## ⚠️ IMPORTANT NOTES

### Before Making Changes
1. **Backup Current State**: This restore point captures the CURRENT stable state
2. **Don't Delete Backups**: Keep backup files safe, even after successful restore
3. **Test Changes First**: Use a development environment to test new features
4. **Document Changes**: Keep notes of what was changed and why

### If Restore Needed
1. **Quick Response**: You can restore within 5 minutes if needed
2. **Zero Data Loss**: Database restore recovers all transactions up to backup time
3. **Version Control**: If issues occur, git history is not backed up (use git pull instead)

### Backup Retention
- **Keep backup files safe** for at least 30 days
- **Test restore quarterly** to ensure backups are valid
- **Store offsite copy** on external drive or cloud storage
- **Document procedures** for future reference

---

## 📞 RECOVERY CONTACTS & COMMANDS

### If Something Goes Wrong

**Check logs first**:
```powershell
# App server errors
ssh root@192.168.20.10 "tail -100 /var/log/gunicorn/error.log"

# Database errors
ssh zubair@192.168.20.11 "sudo tail -100 /var/log/postgresql/postgresql.log"

# Nginx errors
ssh root@192.168.20.10 "tail -100 /var/log/nginx/error.log"
```

**Quick diagnostics**:
```powershell
# Is app running?
ssh root@192.168.20.10 "systemctl status gunicorn"

# Is database running?
ssh zubair@192.168.20.11 "sudo systemctl status postgresql"

# Can we connect to DB?
psql -h 192.168.20.11 -U zubair -d tradifyerp_db -c "SELECT NOW();"
```

---

## 🎯 NEXT STEPS FOR ENHANCEMENT

Now that you have a safe restore point:

1. **Create a development branch** in git
2. **Test new features** on a dev server first
3. **Use this restore point** if dev changes go wrong
4. **After successful testing**, merge to production
5. **Create new restore points** after each major change

---

**Restore Point Date**: April 7, 2026  
**TradifyERP Version**: 5.2.9 (Django)  
**Database**: PostgreSQL 16.13  
**Total Modules**: 14 ERP + 4 Utility  

---

## 📝 BACKUP CHECKLIST FOR OPERATIONS TEAM

- [x] App server backup created and verified
- [ ] Database backup created and verified
- [ ] Backups accessible and tested
- [ ] Restore procedure documented
- [ ] Team trained on restore process
- [ ] Backup retention policy established
- [ ] Off-site copy created (optional but recommended)
- [ ] Restore tested successfully (should do quarterly)

---

**Document Version**: 1.0  
**Last Updated**: April 7, 2026  
**Next Review**: After enhancement completion
