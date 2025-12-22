#!/usr/bin/env python3
"""
Migrate database from old server backup to new PostgreSQL server
Uses Django's loaddata to restore prod_data_full.json fixture
"""

import os
import sys
import json

# Add TradifyERP to path
sys.path.insert(0, r'f:\ERP-Production\Zubair-ERP-Project')
os.chdir(r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

# Configure Django with PostgreSQL settings
from django.conf import settings
if not settings.configured:
    settings.configure(
        DEBUG=False,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'tradify',
                'USER': 'zubair',
                'PASSWORD': 'zubair@0862',
                'HOST': '192.168.20.11',
                'PORT': '5432',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.admin',
        ],
        SECRET_KEY='temporary-key-for-fixture-loading',
        USE_TZ=True,
    )

django.setup()

from django.core.management import call_command
from django.db import connection

fixture_file = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\prod_data_full.json'

print("\n" + "=" * 80)
print("DATABASE MIGRATION TOOL - Load Fixture to New PostgreSQL Server")
print("=" * 80)

print(f"\n[+] Django Settings: TradifyERP.settings")
print(f"[+] Database: {settings.DATABASES['default']['NAME']}")
print(f"[+] Host: {settings.DATABASES['default']['HOST']}")
print(f"[+] User: {settings.DATABASES['default']['USER']}")

# Check connection
print("\n[*] Testing database connection...")
try:
    connection.ensure_connection()
    print("[+] Connection successful!")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM auth_user;")
        current_count = cursor.fetchone()[0]
        print(f"[+] Current users in database: {current_count}")
except Exception as e:
    print(f"[-] Connection failed: {e}")
    sys.exit(1)

# Check fixture file
print(f"\n[*] Loading fixture: {fixture_file}")
if not os.path.exists(fixture_file):
    print(f"[-] Fixture file not found: {fixture_file}")
    sys.exit(1)

# Count fixture records
with open(fixture_file, 'r') as f:
    fixtures = json.load(f)
    print(f"[+] Fixture contains {len(fixtures)} records")

# Load fixture
print("\n[*] Loading fixture into database...")
try:
    call_command('loaddata', fixture_file, verbosity=2)
    print("\n[+] Fixture loaded successfully!")
    
    # Verify
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM auth_user;")
        new_count = cursor.fetchone()[0]
        print(f"\n[+] Users after migration: {new_count}")
        
        cursor.execute("SELECT COUNT(*) FROM accounting_entity;")
        entities = cursor.fetchone()[0]
        print(f"[+] Entities: {entities}")
        
        print("\n" + "=" * 80)
        print("SUCCESS - MIGRATION COMPLETE - All data loaded successfully!")
        print("=" * 80)
        
except Exception as e:
    print(f"\n[-] Error during load: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
