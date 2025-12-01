#!/usr/bin/env python
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from manufacturing.models import DistributorPerformance

# Get all records
all_records = DistributorPerformance.objects.all().order_by('distributor', 'performance_year', 'performance_month')

print(f"📊 Total DistributorPerformance records: {all_records.count()}\n")

if all_records.count() > 0:
    print("Current records in database:")
    for record in all_records:
        print(f"  • {record.distributor.distributor_name}: {record.performance_month:02d}/{record.performance_year} (created: {record.created_at.strftime('%Y-%m-%d %H:%M:%S')})")
    
    # Find duplicates
    from django.db.models import Count
    
    duplicates = DistributorPerformance.objects.values('distributor', 'performance_month', 'performance_year').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    if duplicates.exists():
        print(f"\n⚠️ Found {duplicates.count()} duplicate combinations:")
        for dup in duplicates:
            print(f"  • Distributor {dup['distributor']}: Month {dup['performance_month']}/{dup['performance_year']} - {dup['count']} records")
            # Get the records and keep only the latest
            records = DistributorPerformance.objects.filter(
                distributor_id=dup['distributor'],
                performance_month=dup['performance_month'],
                performance_year=dup['performance_year']
            ).order_by('-created_at')
            
            to_delete = records[1:]  # Keep the first (latest), delete the rest
            count = to_delete.count()
            to_delete.delete()
            print(f"    ✓ Deleted {count} duplicate record(s), kept 1")
        
        print(f"\n✅ Cleanup complete! Remaining records: {DistributorPerformance.objects.count()}")
    else:
        print("\n✅ No duplicates found.")
else:
    print("No records found in database.")
