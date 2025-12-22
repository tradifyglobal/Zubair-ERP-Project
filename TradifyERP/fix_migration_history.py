"""
Manually fix migration history by inserting the missing 0002_add_exchange_rate_fields migration
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.db import connection

# Insert the missing migration record
with connection.cursor() as cursor:
    # First, check if it exists
    cursor.execute("""
        SELECT id FROM django_migrations 
        WHERE app = 'accounting' AND name = '0002_add_exchange_rate_fields'
    """)
    result = cursor.fetchone()
    
    if result:
        print("Migration 0002_add_exchange_rate_fields already exists")
    else:
        # Just insert it with current timestamp
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied) 
            VALUES ('accounting', '0002_add_exchange_rate_fields', datetime('now'))
        """)
        print("Successfully inserted migration 0002_add_exchange_rate_fields")
