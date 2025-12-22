#!/usr/bin/env python3
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TradifyERP.settings_production")
django.setup()

from accounting.models import Stakeholder
from django.db import connection

# Check if columns exist in database
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'accounting_stakeholder' 
        AND column_name IN ('start_date', 'end_date')
    """)
    columns = [row[0] for row in cursor.fetchall()]
    
print(f"Database columns found: {columns}")

# Check if model has the fields
stakeholder_fields = [f.name for f in Stakeholder._meta.get_fields()]
print(f"Model fields: start_date={'start_date' in stakeholder_fields}, end_date={'end_date' in stakeholder_fields}")
