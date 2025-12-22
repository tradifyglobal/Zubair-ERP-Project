#!/usr/bin/env python3
"""
Fix sequence reset
"""
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

# Setup Django
django.setup()

from django.db import connection

print("FIXING SEQUENCE RESET")
print("====================")

try:
    with connection.cursor() as cursor:
        cursor.execute("ALTER SEQUENCE accounting_cashreceiptline_id_seq RESTART WITH 1")
        print("✅ Sequence reset to start from 1")
        
        # Verify
        cursor.execute("SELECT nextval('accounting_cashreceiptline_id_seq')")
        next_id = cursor.fetchone()[0]
        print(f"Next ID will be: {next_id}")
        
        # Reset it back since we just consumed one
        cursor.execute("SELECT setval('accounting_cashreceiptline_id_seq', 1, false)")
        print("✅ Sequence properly reset - next receipt will be ID 1")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("Sequence fix complete!")