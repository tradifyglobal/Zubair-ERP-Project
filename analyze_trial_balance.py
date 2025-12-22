#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import LedgerEntry, Entity
from django.db.models import Sum, Q
from decimal import Decimal

def analyze_trial_balance():
    entity = Entity.objects.first()
    print(f'Entity: {entity.name}')
    print('\n=== LEDGER ENTRIES ANALYSIS ===')

    # Get all ledger entries
    entries = LedgerEntry.objects.filter(entity=entity)
    print(f'Total Ledger Entries: {entries.count()}')

    if entries.exists():
        # Calculate totals by entry type
        debits = entries.filter(entry_type='DEBIT').aggregate(total=Sum('amount'))['total'] or Decimal('0')
        credits = entries.filter(entry_type='CREDIT').aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        print(f'\nTotal Debits: ₹{debits:,.2f}')
        print(f'Total Credits: ₹{credits:,.2f}')
        print(f'Difference: ₹{abs(debits - credits):,.2f}')
        print(f'Is Balanced: {abs(debits - credits) < Decimal("0.01")}')
        
        # Show recent entries
        print('\n=== RECENT LEDGER ENTRIES ===')
        recent_entries = entries.order_by('-created_at')[:10]
        for entry in recent_entries:
            print(f'{entry.entry_date} | {entry.entry_type} | {entry.account.account_number} - {entry.account.name} | ₹{entry.amount:,.2f}')
            
        # Check for any incomplete transactions (single entries without matching pair)
        print('\n=== CHECKING FOR INCOMPLETE TRANSACTIONS ===')
        
        # Group by transaction reference or date and check if debits = credits
        transactions = entries.values('reference_number', 'entry_date').annotate(
            total_debits=Sum('amount', filter=Q(entry_type='DEBIT')),
            total_credits=Sum('amount', filter=Q(entry_type='CREDIT'))
        )
        
        imbalanced_transactions = []
        for txn in transactions:
            debit_amt = txn['total_debits'] or Decimal('0')
            credit_amt = txn['total_credits'] or Decimal('0')
            if abs(debit_amt - credit_amt) >= Decimal('0.01'):
                imbalanced_transactions.append(txn)
        
        if imbalanced_transactions:
            print(f"Found {len(imbalanced_transactions)} imbalanced transactions:")
            for txn in imbalanced_transactions[:5]:  # Show first 5
                print(f"  Date: {txn['entry_date']} | Ref: {txn['reference_number']} | Debits: ₹{txn['total_debits'] or 0:,.2f} | Credits: ₹{txn['total_credits'] or 0:,.2f}")
        else:
            print("All individual transactions are balanced")
            
    else:
        print('No ledger entries found')

if __name__ == "__main__":
    analyze_trial_balance()