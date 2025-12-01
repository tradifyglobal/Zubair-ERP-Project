import sys
import os
sys.path.insert(0, 'G:\\TradifyERP')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

import django
django.setup()

from accounting.models import LedgerEntry, Entity
from django.db.models import Count

print('=== TOTAL ENTRIES ===')
total = LedgerEntry.objects.count()
print(f'Total entries: {total}')

print('\n=== ENTRIES BY STATUS ===')
stats = LedgerEntry.objects.values('workflow_status').annotate(count=Count('id')).order_by('workflow_status')
for s in stats:
    print(f"{s['workflow_status']}: {s['count']}")

print('\n=== ENTRIES BY ENTITY ===')
entity_stats = LedgerEntry.objects.values('entity__name').annotate(count=Count('id')).order_by('entity__name')
for s in entity_stats:
    print(f"{s['entity__name']}: {s['count']}")

print('\n=== RECENT 5 ENTRIES ===')
for entry in LedgerEntry.objects.all().order_by('-id')[:5]:
    print(f"ID: {entry.id}, Entity: {entry.entity.name}, Account: {entry.account.name}, Amount: {entry.amount}, Status: {entry.workflow_status}, Posted: {entry.is_posted}")
