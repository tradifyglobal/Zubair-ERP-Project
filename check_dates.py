#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, '/var/www/tradifyerp')
sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Stakeholder
from django.db import connection

# Check if columns exist in database
cursor = connection.cursor()
cursor.execute("PRAGMA table_info(accounting_stakeholder)")
columns = cursor.fetchall()

print("Checking database columns for accounting_stakeholder:")
print("=" * 60)
for col in columns:
    if 'date' in str(col).lower():
        print(col)

print("\n" + "=" * 60)
print("\nChecking model fields:")
print("=" * 60)
model_fields = [f.name for f in Stakeholder._meta.get_fields()]
print("start_date in model:", 'start_date' in model_fields)
print("end_date in model:", 'end_date' in model_fields)

print("\nAll date-related fields:")
for field in Stakeholder._meta.get_fields():
    if 'date' in field.name.lower():
        print(f"  - {field.name} ({field.__class__.__name__})")

print("\n" + "=" * 60)
print("\nChecking first stakeholder records:")
print("=" * 60)
stakeholders = Stakeholder.objects.all()[:3]
for s in stakeholders:
    print(f"{s.full_name}: start_date={getattr(s, 'start_date', 'NOT FOUND')}, end_date={getattr(s, 'end_date', 'NOT FOUND')}")
