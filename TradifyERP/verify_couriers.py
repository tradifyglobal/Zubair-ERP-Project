#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from manufacturing.models import Courier
from accounting.models import Entity

entity = Entity.objects.first()
if entity:
    couriers = Courier.objects.filter(entity=entity, is_active=True).order_by('name')
    print(f"\n✓ Total Active Couriers: {couriers.count()}\n")
    for i, courier in enumerate(couriers, 1):
        print(f"  {i}. {courier.name:40} ({courier.code})")
    print("\n✓ Courier Setup Complete!\n")
else:
    print("No entity found")
