#!/usr/bin/env python
"""
Comprehensive GL Dashboard simulation for all entities
"""

import os
import sys
sys.path.append('/var/www/tradifyerp')

import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Account, LedgerEntry, Entity
from shareholder.models import CapitalContribution, Stakeholder

def simulate_gl_dashboard(entity):
    """Simulate exactly what GLDashboardView.get_context_data() would return"""
    print(f"\n=== GL DASHBOARD SIMULATION FOR: {entity.name} (ID: {entity.id}) ===")
    
    # Summary metrics - calculate total assets from debit balances (from view code)
    asset_accounts = entity.accounts.filter(account_type='ASSET')
    total_assets = Decimal('0.00')
    for acc in asset_accounts:
        debits = acc.ledger_entries.filter(entry_type='DEBIT').aggregate(
            total=django.db.models.Sum('amount')
        )['total'] or Decimal('0.00')
        credits = acc.ledger_entries.filter(entry_type='CREDIT').aggregate(
            total=django.db.models.Sum('amount')
        )['total'] or Decimal('0.00')
        total_assets += (debits - credits)
    
    print(f"Total Assets: {total_assets:,.2f}")
    
    # Calculate current balances for all accounts from GL entries (from view code)
    accounts = entity.accounts.all()
    accounts_with_balances = []
    
    print(f"Total Accounts: {accounts.count()}")
    print("\nAccount Balances (as shown in GL Dashboard):")
    print("-" * 80)
    
    cash_total = Decimal('0.00')
    equity_total = Decimal('0.00')
    suspicious_accounts = []
    
    for account in accounts:
        debits = account.ledger_entries.filter(entry_type='DEBIT').aggregate(
            total=django.db.models.Sum('amount')
        )['total'] or Decimal('0.00')
        credits = account.ledger_entries.filter(entry_type='CREDIT').aggregate(
            total=django.db.models.Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Determine if debit-based or credit-based account (from view code)
        is_debit_based = account.account_type in ['ASSET', 'EXPENSE']
        
        if is_debit_based:
            current_balance = debits - credits
        else:
            current_balance = credits - debits
        
        accounts_with_balances.append({
            'account': account,
            'current_balance': current_balance,
            'debits': debits,
            'credits': credits
        })
        
        # Track cash and equity
        if 'cash' in account.name.lower():
            cash_total += current_balance
            
        if account.account_type == 'EQUITY':
            equity_total += current_balance
        
        # Check for suspicious amounts (around 5 lakh)
        if abs(current_balance) >= 400000:
            suspicious_accounts.append((account, current_balance, debits, credits))
        
        # Show non-zero accounts
        if current_balance != 0:
            print(f"{account.account_type:8s} | {account.account_number:6s} | {account.name:25s} | {current_balance:>12,.2f}")
    
    print(f"\nCash Total: {cash_total:,.2f}")
    print(f"Equity Total: {equity_total:,.2f}")
    
    if suspicious_accounts:
        print(f"\nSUSPICIOUS LARGE BALANCES (400k+):")
        for account, balance, debits, credits in suspicious_accounts:
            print(f"  {account.name}: {balance:,.2f} (D:{debits:,.2f} C:{credits:,.2f})")
            
            # Show recent entries
            recent_entries = account.ledger_entries.all().order_by('-entry_date')[:3]
            for entry in recent_entries:
                print(f"    {entry.entry_date} | {entry.entry_type:6s} | {entry.amount:>10,.2f} | {entry.description[:30]}")
    
    return total_assets, accounts_with_balances

# Main execution
print("GL DASHBOARD COMPREHENSIVE CHECK")
print("=" * 70)

# Get all entities
entities = Entity.objects.all().order_by('id')
print("Available Entities:")
for entity in entities:
    print(f"  {entity.id}: {entity.name} (Active: {entity.is_active})")

print("\n" + "="*70)

# Simulate GL Dashboard for each entity
all_results = {}
for entity in entities:
    if entity.is_active:
        try:
            total_assets, accounts_data = simulate_gl_dashboard(entity)
            all_results[entity.name] = (total_assets, accounts_data)
        except Exception as e:
            print(f"Error processing {entity.name}: {e}")

# Summary across all entities
print(f"\n{'='*70}")
print("SUMMARY ACROSS ALL ENTITIES:")
print("="*70)

for entity_name, (total_assets, accounts_data) in all_results.items():
    print(f"\n{entity_name}:")
    print(f"  Total Assets: {total_assets:,.2f}")
    
    # Find accounts with exactly 500,000 or close to it
    for item in accounts_data:
        balance = item['current_balance']
        if abs(balance - 500000) < 1000:  # Within 1000 of 5 lakh
            print(f"  POTENTIAL 5 LAKH ISSUE: {item['account'].name} = {balance:,.2f}")

print("\nCHECK COMPLETE!")