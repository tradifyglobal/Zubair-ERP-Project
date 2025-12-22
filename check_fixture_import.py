#!/usr/bin/env python3
"""
Load fixture data directly using psycopg2 to PostgreSQL
This bypasses Django and loads raw fixture JSON data
"""

import json
import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    'host': '192.168.2.59',
    'database': 'tradify',
    'user': 'zubair',
    'password': 'zubair@0862',
    'port': '5432'
}

FIXTURE_FILE = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\prod_data_no_users.json'

print("\n" + "=" * 80)
print("LOADING FIXTURE - Direct PostgreSQL Connection")
print("=" * 80)

print(f"\n[*] Connecting to PostgreSQL...")
print(f"[+] Host: {DB_CONFIG['host']}")
print(f"[+] Database: {DB_CONFIG['database']}")
print(f"[+] User: {DB_CONFIG['user']}")

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("[+] Connected successfully!")
except Exception as e:
    print(f"[-] Connection failed: {e}")
    exit(1)

# Read fixture
print(f"\n[*] Reading fixture file: {FIXTURE_FILE}")
try:
    with open(FIXTURE_FILE, 'r') as f:
        fixtures = json.load(f)
    print(f"[+] Loaded {len(fixtures)} records")
except Exception as e:
    print(f"[-] Failed to read fixture: {e}")
    exit(1)

# Count by model
models_count = {}
for item in fixtures:
    model = item.get('model', 'unknown')
    models_count[model] = models_count.get(model, 0) + 1

print(f"\n[*] Records by model:")
for model, count in sorted(models_count.items()):
    print(f"    {model}: {count}")

# Get current counts before loading
print(f"\n[*] Getting current database state...")
try:
    cursor.execute("SELECT COUNT(*) FROM auth_user;")
    users_before = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM accounting_entity;")
    entities_before = cursor.fetchone()[0]
    
    print(f"[+] Current users: {users_before}")
    print(f"[+] Current entities: {entities_before}")
except Exception as e:
    print(f"[-] Query failed: {e}")
    conn.close()
    exit(1)

print(f"\n[*] Fixture will add approximately {models_count.get('auth.user', 0)} users")
print(f"[*] Fixture will add approximately {models_count.get('accounting.entity', 0)} entities")

print(f"\n[!] NOTE: This is a direct load. Please ensure Django loaddata on app server instead.")
print(f"[!] Use: python manage.py loaddata prod_data_no_users.json --settings=TradifyERP.settings_production")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("Script prepared. Use Django's loaddata command on production server.")
print("=" * 80)
