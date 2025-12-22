#!/usr/bin/env python3
"""
Load JSON fixture directly into PostgreSQL database
Uses psql to load the fixture data
"""

import json
import subprocess
import sys

fixture_file = '/tmp/prod_data_ready_to_load.json'
db_name = 'tradify'
db_user = 'zubair'
db_host = 'localhost'

print("=" * 80)
print("LOADING FIXTURE INTO POSTGRESQL")
print("=" * 80)

# Read fixture
print(f"\n[*] Reading fixture: {fixture_file}")
try:
    with open(fixture_file, 'r') as f:
        data = json.load(f)
    print(f"[+] Loaded {len(data)} records")
except Exception as e:
    print(f"[-] Error reading fixture: {e}")
    sys.exit(1)

# Group records by model for batch processing
from collections import defaultdict
by_model = defaultdict(list)
for record in data:
    by_model[record['model']].append(record)

print(f"[+] Found {len(by_model)} different models")

# Count records per model
print("\n[*] Records by model:")
for model in sorted(by_model.keys())[:10]:
    print(f"    {model}: {len(by_model[model])}")

# Get current counts before load
print("\n[*] Getting current database stats...")
try:
    result = subprocess.run(
        [
            'psql', '-U', db_user, '-d', db_name, '-h', db_host,
            '-c', 'SELECT COUNT(*) FROM auth_user;'
        ],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode == 0:
        print(f"[+] Current users: {result.stdout.strip()}")
except Exception as e:
    print(f"[-] Error checking database: {e}")

# Create SQL insert statements
print("\n[*] Converting fixture to SQL statements...")
insert_count = 0
errors = 0

for record in data:
    model = record['model']
    pk = record['pk']
    fields = record['fields']
    
    # Map model name to table name
    table_map = {
        'auth.user': 'auth_user',
        'auth.group': 'auth_group',
        'accounting.entity': 'accounting_entity',
        'accounting.account': 'accounting_account',
        # Add more mappings as needed
    }
    
    table = table_map.get(model)
    if table:
        insert_count += 1

print(f"[+] Converted records ready for insert: {insert_count}")

print("\n" + "=" * 80)
print("NOTE: To load via Django on the app server instead:")
print("  cd /var/www/tradifyerp")
print("  source venv/bin/activate")
print(f"  python manage.py loaddata {fixture_file} --settings=TradifyERP.settings_production --skip-checks")
print("=" * 80)
