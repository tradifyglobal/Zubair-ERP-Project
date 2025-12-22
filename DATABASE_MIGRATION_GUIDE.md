# Database Migration Guide - Load Old Server Data to New PostgreSQL

## Current Status

✓ **Fixture files prepared locally:**
- `prod_data_full.json` - Complete 43,909 records from old server
- `prod_data_no_users.json` - Filtered 43,908 records (removed conflicting user)

✓ **PostgreSQL Connection verified:**
- Host: 192.168.2.59
- Database: tradify
- Current users: 2 (admin, zubair)
- Current entities: 1 (Main Company)

✓ **Fixture data contains:**
- 6 users (will add to existing 2 = 8 total)
- 5 entities (will add to existing 1 = 6 total)  
- 41,996 accounts
- 9 customers
- 3 vendors
- All accounting, sales, CRM, HR, and manufacturing data

## How to Load the Data

### Option 1: Simple Django Command (Recommended)

**When SSH is available, run on app server (192.168.2.69):**

```bash
ssh ubuntu@192.168.2.69

cd /var/www/tradifyerp

# Backup existing data (optional)
sudo -u postgres pg_dump tradify > /tmp/tradify_backup_$(date +%s).sql

# Ensure the fixture file is in the Django app directory
# If not already there, you can copy it via SCP from your local machine:
# scp prod_data_no_users.json ubuntu@192.168.2.69:/var/www/tradifyerp/

# Load the fixture data
python manage.py loaddata prod_data_no_users.json --settings=TradifyERP.settings_production -v 2

# Restart Gunicorn
sudo systemctl restart gunicorn

# Verify
python manage.py shell --settings=TradifyERP.settings_production << EOF
from django.contrib.auth.models import User
from accounting.models import Entity

print(f"Total Users: {User.objects.count()}")
print(f"Total Entities: {Entity.objects.count()}")
EOF
```

### Option 2: Direct PostgreSQL Restore (If fixtures fail)

```bash
# Restore directly from SQL dump
psql -h 192.168.2.59 -U zubair -d tradify < /path/to/backup.sql
```

## What Gets Loaded

**Users to be added:**
- 6 new users from fixture (keeping existing admin and zubair users)

**Business Data:**
- 5 entities (companies)
- 41,996 accounting accounts (Chart of Accounts)
- 9 customers
- 3 vendors
- Complete ledger entries, invoices, and transactions
- Sales orders and invoices
- HR records (employees, payroll, leaves)
- Manufacturing records (products, orders, shipments)
- CRM data (leads, opportunities, contacts)
- All module permissions and user roles

## After Loading - Next Steps

1. **Verify in Dashboard:**
   - Login: http://192.168.2.69/admin/
   - Check Dashboard: http://192.168.2.69/accounting/dashboard/
   - Check new entities in Admin > Accounting > Entities

2. **Assign Users to Entities:**
   - Some users may need to be linked to entities
   - Go to Admin > Accounting > User Entity
   - Verify UserEntity assignments are correct

3. **Test Each Module:**
   - Accounting > Chart of Accounts (should see 41,996+ accounts)
   - Sales > Invoices (should see 9+ invoices)
   - CRM > Leads (should see leads and opportunities)
   - HR > Employees (should see 2+ employees)

4. **Restart Services:**
   ```bash
   sudo systemctl restart gunicorn
   sudo systemctl restart nginx
   ```

## Fixture Files Location

**Local (your Windows machine):**
- `f:\ERP-Production\Zubair-ERP-Project\TradifyERP\prod_data_no_users.json` (43,908 records)
- `f:\ERP-Production\Zubair-ERP-Project\TradifyERP\prod_data_full.json` (43,909 records)

**Production Server:**
- Copy to: `/var/www/tradifyerp/prod_data_no_users.json`

## Troubleshooting

**If you get "duplicate key value" error:**
- This means a user/entity already exists
- The filtered file (`prod_data_no_users.json`) should prevent this
- Or manually delete conflicting records before loading

**If Django loaddata fails:**
- Check migrations: `python manage.py migrate --settings=TradifyERP.settings_production`
- Check database connections: `psql -h 192.168.2.59 -U zubair -d tradify -c "SELECT 1;"`
- Review logs: `journalctl -xeu gunicorn.service`

**If you see "transaction is aborted" errors:**
- This was already fixed in the dashboard view
- If occurs elsewhere, review the view code for SQL errors

## How to Copy Fixture File to Server

When SSH becomes available:

```powershell
# From Windows local machine
$localFile = "f:\ERP-Production\Zubair-ERP-Project\TradifyERP\prod_data_no_users.json"
$remoteServer = "ubuntu@192.168.2.69"
$remotePath = "/var/www/tradifyerp/"

scp $localFile ${remoteServer}:${remotePath}
```

Or if SCP doesn't work, use SFTP:

```bash
sftp ubuntu@192.168.2.69
cd /var/www/tradifyerp/
put prod_data_no_users.json
exit
```

## Quick Reference - SSH Commands

```bash
# SSH to app server
ssh ubuntu@192.168.2.69

# SSH to database server
ssh ubuntu@192.168.2.59

# Copy file via SCP
scp prod_data_no_users.json ubuntu@192.168.2.69:/var/www/tradifyerp/

# Run command remotely
ssh ubuntu@192.168.2.69 "python manage.py loaddata prod_data_no_users.json --settings=TradifyERP.settings_production"
```

## Current System Status

**App Server:** 192.168.2.69 (Ubuntu, Django/Gunicorn/Nginx)
**DB Server:** 192.168.2.59 (PostgreSQL 16)
**Database:** tradify
**Dashboard:** Working (returns 200 OK)
**Login:** Working with auth

---

**Next Action:** Wait for SSH authentication to recover, then copy fixture and run loaddata command.
