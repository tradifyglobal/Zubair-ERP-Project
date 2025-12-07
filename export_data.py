#!/usr/bin/env python
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

# Export data
from django.core import serializers
from django.apps import apps

print("Exporting all data...")
data = serializers.serialize(
    'json',
    [model._base_manager.all() for model in apps.get_models()],
    use_natural_foreign_keys=True,
    use_natural_primary_keys=True,
    stream=None
)

# Write with proper UTF-8 encoding (no BOM)
with open('dev_full_data.json', 'w', encoding='utf-8') as f:
    f.write(data)

size = os.path.getsize('dev_full_data.json')
print(f"Export complete: {size} bytes ({size/1024:.2f} KB)")
