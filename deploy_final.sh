#!/bin/bash

set -e

echo "=========================================="
echo "Phase 1 Final Deployment Script"
echo "=========================================="

cd /var/www/tradifyerp

# Step 1: Add to INSTALLED_APPS
echo ""
echo "STEP 1: Adding raw_materials to INSTALLED_APPS..."
python3 << 'EOFPYTHON'
settings_file = '/var/www/tradifyerp/TradifyERP/settings_production.py'
with open(settings_file, 'r') as f:
    content = f.read()

if "'raw_materials'" not in content:
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "'ar.apps.ArConfig'" in line:
            lines.insert(i+1, "    'raw_materials',  # Raw Materials Management")
            break
    with open(settings_file, 'w') as f:
        f.write('\n'.join(lines))
    print("rawmaterials_added_to_settings")
else:
    print("raw_materials_already_in_settings")
EOFPYTHON

# Step 2: Create migrations
echo ""
echo "STEP 2: Creating migrations..."
./venv/bin/python manage.py makemigrations raw_materials
echo "migrations_created"

# Step 3: Apply migrations
echo ""
echo "STEP 3: Applying migrations..."
./venv/bin/python manage.py migrate raw_materials
echo "migrations_applied"

# Step 4: Load data
echo ""
echo "STEP 4: Loading raw materials data..."
./venv/bin/python manage.py load_raw_materials
echo "data_loaded"

# Step 5: Restart Gunicorn
echo ""
echo "STEP 5: Restarting Gunicorn..."
systemctl restart gunicorn
sleep 2
systemctl status gunicorn | head -3
echo "gunicorn_restarted"

# Step 6: Verify
echo ""
echo "STEP 6: Verifying data..."
./venv/bin/python << 'EOFVERIFY'
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from raw_materials.models import RawMaterial, Supplier, RawMaterialCategory, Stock

print(f"Raw Materials: {RawMaterial.objects.count()}")
print(f"Categories: {RawMaterialCategory.objects.count()}")
print(f"Suppliers: {Supplier.objects.count()}")
print(f"Stock Records: {Stock.objects.count()}")
EOFVERIFY

echo ""
echo "=========================================="
echo "DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Open browser: http://192.168.20.10/admin"
echo "2. Login with admin credentials"
echo "3. You should see 'Raw Materials Management' section"
echo "4. Verify 15 materials, 5 suppliers, 5 categories are present"
echo ""
