#!/bin/bash
# Load fixture data on production server

cd /var/www/tradifyerp

# Flush database
echo "[*] Flushing database..."
python manage.py flush --noinput --settings=TradifyERP.settings_production

# Load fixture
echo "[*] Loading fixture data..."
python manage.py loaddata prod_data_full.json --settings=TradifyERP.settings_production -v 2

# Verify
echo "[*] Verifying data..."
python manage.py shell --settings=TradifyERP.settings_production << PYEND
from django.contrib.auth.models import User
from accounting.models import Entity

user_count = User.objects.count()
entity_count = Entity.objects.count()

print(f"Total users: {user_count}")
print(f"Total entities: {entity_count}")
PYEND

echo "Done!"
