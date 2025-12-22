#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity

print("Available Entities:")
for e in Entity.objects.all():
    print(f"  ID: {e.id}, Code: '{e.code}', Name: '{e.name}'")
