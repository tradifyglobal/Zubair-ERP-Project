#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/var/www/tradifyerp')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import (
    Stakeholder, CapitalContribution, CashReceiptLine, 
    CashPaymentLine, Account, LedgerEntry, Entity
)
from django.db.models import Sum

print("=== CHECKING VIEW CALCULATION LOGIC ===")

# Find Testing entity  
entity = Entity.objects.filter(name__icontains='Testing').first()
if not entity:
    entity = Entity.objects.first()  # Fallback to first entity
entity_id = entity.id
print(f"Entity: {entity} (ID: {entity_id})")

print("\n=== 1. CASH POSITION VIEW LOGIC ===")
# Simulate CashPositionView calculation
all_contributions = CapitalContribution.objects.filter(entity_id=entity_id)
completed = all_contributions.filter(status='COMPLETED')

print("Capital Contributions (COMPLETED):")
total_contrib_amount = 0
for contrib in completed:
    amount = float(contrib.amount_company_currency or 0)
    total_contrib_amount += amount
    print(f"  {contrib.id}: {amount:,.2f} (Ref: {contrib.reference_number})")

print(f"💰 Capital Contributions Total: {total_contrib_amount:,.2f}")

# Cash accounts calculation
cash_accounts = Account.objects.filter(
    entity_id=entity_id,
    account_type='ASSET'
).filter(
    account_number__startswith='100'
)

print("\nCash Accounts:")
total_cash_balance = 0
for account in cash_accounts:
    debits = LedgerEntry.objects.filter(
        account=account, entry_type='DEBIT'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    credits = LedgerEntry.objects.filter(
        account=account, entry_type='CREDIT'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    balance = float(debits) - float(credits)
    total_cash_balance += balance
    
    print(f"  {account.account_number} - {account.name}: {balance:,.2f}")

print(f"💰 Total Cash Balance: {total_cash_balance:,.2f}")

print("\n=== 2. INVESTMENT REPORT LOGIC ===")
# Simulate investment report calculation
stakeholder = Stakeholder.objects.filter(first_name__icontains='Fayazuddin').first()

# Check if investment report is summing both contributions AND transactions
cash_receipts_amount = CashReceiptLine.objects.filter(
    entity_id=entity_id,
    account__name__icontains='Fayazuddin'
).aggregate(total=Sum('debit_amount'))['total'] or 0

cash_payments_amount = CashPaymentLine.objects.filter(
    entity_id=entity_id,
    account__name__icontains='Fayazuddin'
).aggregate(total=Sum('debit_amount'))['total'] or 0

contrib_amount = CapitalContribution.objects.filter(
    entity_id=entity_id,
    stakeholder=stakeholder,
    status='COMPLETED'
).aggregate(total=Sum('amount_company_currency'))['total'] or 0

print(f"Cash Receipts Sum: {float(cash_receipts_amount):,.2f}")
print(f"Cash Payments Sum: {float(cash_payments_amount):,.2f}")  
print(f"Capital Contributions Sum: {float(contrib_amount):,.2f}")

# This might be where 5 lakh comes from:
potential_double_count = float(cash_receipts_amount) + float(cash_payments_amount) + float(contrib_amount)
print(f"❌ If adding all three: {potential_double_count:,.2f}")

print(f"✅ Correct total should be: {float(contrib_amount):,.2f}")

print("\n=== 3. DASHBOARD VIEW LOGIC ===")
# Check accounting dashboard calculation
contributions = CapitalContribution.objects.filter(
    entity_id=entity_id,
    status='COMPLETED'
)

dashboard_contrib_total = sum(float(c.amount_company_currency or 0) for c in contributions)
print(f"💰 Dashboard Capital Total: {dashboard_contrib_total:,.2f}")

# Check if dashboard is also adding cash transactions
total_capital_received_usd = sum(float(c.amount_usd or 0) for c in contributions)
print(f"💰 Dashboard USD Total: {total_capital_received_usd:,.2f}")

print("\n=== 4. TRIAL BALANCE IMPACT ===")
# Check capital account balance
capital_account = Account.objects.filter(
    entity_id=entity_id,
    name__icontains='Fayazuddin'
).first()

if capital_account:
    debits = LedgerEntry.objects.filter(
        account=capital_account, entry_type='DEBIT'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    credits = LedgerEntry.objects.filter(
        account=capital_account, entry_type='CREDIT'  
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    print(f"Capital Account {capital_account.account_number}:")
    print(f"  Debits: {float(debits):,.2f}")
    print(f"  Credits: {float(credits):,.2f}")
    print(f"  Net: {float(credits) - float(debits):,.2f} (Equity should be credit balance)")

print("\n=== CONCLUSION ===")
print("The correct calculation should be:")
print(f"  Cash Receipt: 100,000.00")
print(f"  Cash Payment: 200,000.00") 
print(f"  Total Capital: 300,000.00")
print("")
print("If any page shows 500,000.00, it's likely:")
print("1. Adding cash transactions + capital contributions (double counting)")
print("2. Incorrect view logic that sums multiple sources")
print("3. Missing deduplication in aggregation queries")