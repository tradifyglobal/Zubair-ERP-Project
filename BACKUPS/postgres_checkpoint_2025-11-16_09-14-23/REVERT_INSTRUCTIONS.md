# PostgreSQL Checkpoint - Revert Instructions

**Checkpoint Date:** November 16, 2025 09:14:23

This checkpoint contains the PostgreSQL database configuration and settings before migration to MySQL.

## How to Revert Back to PostgreSQL

### Step 1: Stop the Django Server
```powershell
# If running, press Ctrl+C in the terminal
```

### Step 2: Restore the Settings File
```powershell
Copy-Item -Path "g:\TradifyERP\BACKUPS\postgres_checkpoint_2025-11-16_09-14-23\settings_postgres.py" `
    -Destination "g:\TradifyERP\TradifyERP\TradifyERP\settings.py" -Force
```

### Step 3: Verify PostgreSQL is Running
```powershell
# Check PostgreSQL service status
psql -U zubair -d tradify -c "SELECT version();"
```

### Step 4: Restart Django
```powershell
cd g:\TradifyERP\TradifyERP
python manage.py runserver 0.0.0.0:8000
```

### Step 5: Verify Connection
Visit http://localhost:8000/dashboard/ and confirm everything is working

---

## Database Configuration (Backup)

**Database Engine:** PostgreSQL
**Database Name:** tradify
**Username:** zubair
**Password:** zubair@0862
**Host:** localhost
**Port:** 5432

---

## Files in This Backup

- `settings_postgres.py` - Original Django settings with PostgreSQL configuration
- `REVERT_INSTRUCTIONS.md` - This file

---

## If You Need to Keep Both Databases

You can have MySQL running alongside PostgreSQL:
1. Keep PostgreSQL settings in this backup
2. Configure MySQL in the main settings.py
3. Both databases will remain intact

---

**Note:** Do not delete this folder unless you're absolutely sure you want to permanently commit to MySQL!
