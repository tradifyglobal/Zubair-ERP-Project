#!/usr/bin/env python3
"""
Clear existing database and load fresh fixture data
"""

import os
import sys
import django

# Add TradifyERP to path
sys.path.insert(0, r'f:\ERP-Production\Zubair-ERP-Project')
os.chdir(r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

django.setup()

from django.core.management import call_command
from django.db import connection

fixture_file = r'f:\ERP-Production\Zubair-ERP-Project\TradifyERP\prod_data_full.json'

print("\n" + "=" * 80)
print("CLEAR & RELOAD DATABASE FIXTURE")
print("=" * 80)

# Get current counts
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM auth_user;")
    user_count = cursor.fetchone()[0]
    print(f"\n[*] Current users in database: {user_count}")

# Flush database
print("\n[*] Clearing all application data...")
try:
    call_command('flush', interactive=False, verbosity=1)
    print("[+] Database cleared successfully!")
except Exception as e:
    print(f"[-] Error flushing: {e}")
    sys.exit(1)

# Verify flush
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM auth_user;")
    after_flush = cursor.fetchone()[0]
    print(f"[+] Users after flush: {after_flush}")

# Load fixture
print(f"\n[*] Loading fixture: {fixture_file}")
try:
    call_command('loaddata', fixture_file, verbosity=1)
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
        
        print("\n" + "=" * 80)
        print("SUCCESS - DATABASE MIGRATED WITH ALL OLD SERVER DATA!")
        print("=" * 80)
        
except Exception as e:
    print(f"\n[-] Error loading fixture: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
