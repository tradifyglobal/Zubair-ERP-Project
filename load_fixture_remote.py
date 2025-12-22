#!/usr/bin/env python3
"""
Load Django fixture data into remote PostgreSQL server
This script loads prod_data_full.json into the new PostgreSQL database
"""

import os
import sys
import django
import json
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp')

django.setup()

from django.core.management import call_command
from django.db import connection

fixture_path = '/tmp/prod_data_full.json'

print("=" * 70)
print("Loading Database Fixture - prod_data_full.json")
print("=" * 70)

# Check current user count
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM auth_user;")
    current_users = cursor.fetchone()[0]
    print(f"\n✓ Current database connected: {connection.settings_dict['HOST']}")
    print(f"✓ Current users in database: {current_users}")

print(f"\n▶ Loading fixture from: {fixture_path}")

try:
    # Load the fixture
    call_command('loaddata', fixture_path, verbosity=2)
    
    # Verify data loaded
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM auth_user;")
        new_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM accounting_entity;")
        entities = cursor.fetchone()[0]
        
        print("\n" + "=" * 70)
        print("✅ FIXTURE LOADED SUCCESSFULLY")
        print("=" * 70)
        print(f"✓ Total users: {new_users}")
        print(f"✓ Total entities: {entities}")
        
except Exception as e:
    print(f"\n❌ Error loading fixture: {e}")
    sys.exit(1)

print("\n✓ Data migration complete!")
