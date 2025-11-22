#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from manufacturing.models import DistributorPerformance

# Delete all test records
deleted_count, _ = DistributorPerformance.objects.all().delete()
print(f"✅ Deleted {deleted_count} DistributorPerformance records")
