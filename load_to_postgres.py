#!/usr/bin/env python3
"""
Load fixture directly into PostgreSQL on 192.168.20.11
"""

import os
import sys
import django
import json

# Setup Django with PostgreSQL settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

sys.path.insert(0, r'f:\ERP-Production\Zubair-ERP-Project')
os.chdir(r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP')

# Import Django settings and override with PostgreSQL
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
                'CONN_MAX_AGE': 600,
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.admin',
            'accounting',
            'ar',
            'ap',
            'cash_management',
            'crm',
            'expenses',
            'hr',
            'inventory',
            'manufacturing',
            'procurement',
            'projects',
            'sales',
            'shareholder',
            'us',
        ],
        SECRET_KEY='fixture-loader',
        USE_TZ=True,
    )

django.setup()

from django.core.management import call_command
from django.db import connection

fixture_file = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\prod_data_no_users.json'

print("\n" + "=" * 80)
print("LOADING FIXTURE INTO PostgreSQL (192.168.20.11)")
print("=" * 80)

print(f"\n[+] Database: {settings.DATABASES['default']['NAME']}")
print(f"[+] Host: {settings.DATABASES['default']['HOST']}")
print(f"[+] User: {settings.DATABASES['default']['USER']}")

# Test connection
print("\n[*] Testing connection to PostgreSQL...")
try:
    connection.ensure_connection()
    print("[+] Connected successfully!")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM auth_user;")
        count = cursor.fetchone()[0]
        print(f"[+] Current users: {count}")
except Exception as e:
    print(f"[-] Connection failed: {e}")
    sys.exit(1)

# Load fixture
print(f"\n[*] Loading fixture: {fixture_file}")
if not os.path.exists(fixture_file):
    print(f"[-] File not found!")
    sys.exit(1)

with open(fixture_file) as f:
    data = json.load(f)
    print(f"[+] Fixture has {len(data)} records")

try:
    call_command('loaddata', fixture_file, verbosity=2, database='default')
    print("\n[+] Fixture loaded successfully!")
    
    # Verify
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM auth_user;")
        users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM accounting_entity;")
        entities = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM accounting_account;")
        accounts = cursor.fetchone()[0]
        
        print(f"\n[RESULTS]")
        print(f"[+] Total users: {users}")
        print(f"[+] Total entities: {entities}")
        print(f"[+] Total accounts: {accounts}")
        
except Exception as e:
    print(f"[-] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("SUCCESS - Data migrated to PostgreSQL!")
print("=" * 80)
