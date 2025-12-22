#!/usr/bin/env python3

import os
import sys
import django

sys.path.append('/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, LedgerEntry, TrialBalance
from datetime import date

def check_all_entities():
    print("=== ALL ENTITIES ANALYSIS ===")
    
    entities = Entity.objects.all()
    print(f"Total entities: {entities.count()}")
    
    for entity in entities:
        print(f"\n--- Entity: {entity.name} (ID: {entity.id}) ---")
        print(f"Active: {entity.is_active}")
        
        # Check ledger entries
        entries = LedgerEntry.objects.filter(entity=entity)
        print(f"Ledger entries: {entries.count()}")
        
        if entries.count() > 0:
            print("Entries:")
            for entry in entries:
                print(f"  {entry.account.account_number} {entry.account.name} | {entry.entry_type} {entry.amount} | {entry.description}")
        
        # Check trial balances
        tbs = TrialBalance.objects.filter(entity=entity)
        print(f"Trial balance records: {tbs.count()}")
        
        if tbs.count() > 0:
            latest_tb = tbs.order_by('-as_of_date').first()
            print(f"Latest TB: {latest_tb.as_of_date} | Dr {latest_tb.total_debits} Cr {latest_tb.total_credits} | Balanced: {latest_tb.is_balanced}")

if __name__ == '__main__':
    check_all_entities()