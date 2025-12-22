#!/bin/bash
#
# Load production database fixture on app server
# This script should be run on the production app server (192.168.20.10)
# It loads the prod_data_full.json into the PostgreSQL database
#

set -e

REPO_PATH="/var/www/tradifyerp"
FIXTURE_FILE="$REPO_PATH/prod_data_full.json"
LOG_FILE="/var/log/tradifyerp/fixture_load.log"

echo "[$(date)] Starting fixture load..." | tee -a $LOG_FILE

cd $REPO_PATH

# Backup current database
echo "[*] Backing up current database..." | tee -a $LOG_FILE
sudo -u postgres pg_dump tradify > /tmp/tradify_backup_$(date +%s).sql
echo "[+] Backup created" | tee -a $LOG_FILE

# Flush Django database (clearing all app data except system tables)
echo "[*] Flushing application data..." | tee -a $LOG_FILE
python manage.py flush --noinput --settings=TradifyERP.settings_production 2>&1 | tee -a $LOG_FILE

# Load fixture
echo "[*] Loading fixture from $FIXTURE_FILE..." | tee -a $LOG_FILE
python manage.py loaddata $FIXTURE_FILE --settings=TradifyERP.settings_production -v 2 2>&1 | tee -a $LOG_FILE

# Verify data
echo "[*] Verifying data..." | tee -a $LOG_FILE
python manage.py shell --settings=TradifyERP.settings_production << PYEND
from django.contrib.auth.models import User
from accounting.models import Entity

users = User.objects.count()
entities = Entity.objects.count()

print(f"\n========== DATA SUMMARY ==========")
print(f"Total Users: {users}")
print(f"Total Entities: {entities}")
print(f"==================================\n")
PYEND

# Restart Gunicorn
echo "[*] Restarting Gunicorn..." | tee -a $LOG_FILE
sudo systemctl restart gunicorn

echo "[+] Done! $(date)" | tee -a $LOG_FILE
