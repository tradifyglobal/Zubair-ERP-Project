"""
Script to generate migrations for ReportAccess model

Run this after saving models.py changes:
    python manage.py makemigrations
    python manage.py migrate
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

# Check if ReportAccess model exists
from django.apps import apps
from accounting.models import ReportAccess

print("✓ ReportAccess model is registered")
print(f"✓ Database table: {ReportAccess._meta.db_table}")
print(f"✓ Fields: {[f.name for f in ReportAccess._meta.fields]}")
