#!/usr/bin/env python
import os
import sys

# Add the project directory to the path
sys.path.insert(0, '/var/www/tradifyerp')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')

import django
django.setup()

from django.db import connection

# Check which migrations are marked in DB
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM django_migrations WHERE app='accounting' ORDER BY name;")
    rows = cursor.fetchall()
    migrations = [row[0] for row in rows]
    
    print("\n" + "="*80)
    print("MIGRATIONS MARKED AS APPLIED IN DATABASE")
    print("="*80)
    print(f"\nTotal: {len(migrations)}")
    print("\nMigrations (last 10):")
    for name in migrations[-10:]:
        print(f"  ✓ {name}")
    
    # Check if 0020 is marked as applied
    if "0020_alter_capitalcontribution_options_and_more" in migrations:
        print("\n✓ Migration 0020 IS marked as applied in django_migrations table")
    else:
        print("\n✗ Migration 0020 NOT marked in django_migrations table")
        
    # Check if 0019 is marked as applied
    if "0019_add_workflow_to_capital_contribution" in migrations:
        print("✓ Migration 0019 IS marked as applied")
    else:
        print("✗ Migration 0019 NOT marked as applied")
