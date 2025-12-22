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
    CashPaymentLine, Account, LedgerEntry
)
from django.db.models import Sum

print("=== ANALYZING FAYAZUDDIN TRANSACTIONS & CALCULATIONS ===")

# Find Fayazuddin stakeholder
stakeholder = Stakeholder.objects.filter(
    first_name__icontains='Fayazuddin'
).first()

if not stakeholder:
    print("❌ Fayazuddin stakeholder not found")
    sys.exit(1)

print(f"Found stakeholder: {stakeholder.first_name} {stakeholder.middle_name} {stakeholder.last_name}")
print(f"Entity: {stakeholder.entity}")

print("\n=== 1. CAPITAL CONTRIBUTIONS ===")
contributions = CapitalContribution.objects.filter(stakeholder=stakeholder).order_by('created_at')
total_contributions = 0

for contrib in contributions:
    print(f"Contribution {contrib.id}:")
    print(f"  Amount: {contrib.amount} {contrib.currency.code}")
    print(f"  Amount Company Currency: {contrib.amount_company_currency}")
    print(f"  Status: {contrib.status}")
    print(f"  Reference: {contrib.reference_number}")
    print(f"  Date: {contrib.contribution_date}")
    print(f"  Created: {contrib.created_at}")
    print()
    
    if contrib.status == 'COMPLETED':
        total_contributions += float(contrib.amount_company_currency or 0)

print(f"💰 Total from Capital Contributions: {total_contributions:,.2f}")

print("\n=== 2. CASH RECEIPTS ===")
cash_receipts = CashReceiptLine.objects.filter(
    account__name__icontains='Fayazuddin'
).order_by('created_at')
total_receipts = 0

for receipt in cash_receipts:
    print(f"Cash Receipt {receipt.id} - {receipt.reference_number}:")
    print(f"  Account: {receipt.account}")
    print(f"  Credit Account: {receipt.credit_account}")
    print(f"  Amount: {receipt.debit_amount}")
    print(f"  Status: {receipt.workflow_status}")
    print(f"  Date: {receipt.date}")
    print()
    
    if receipt.workflow_status in ['AUTHORIZED', 'POSTED']:
        total_receipts += float(receipt.debit_amount or 0)

print(f"💰 Total from Cash Receipts: {total_receipts:,.2f}")

print("\n=== 3. CASH PAYMENTS ===")
cash_payments = CashPaymentLine.objects.filter(
    account__name__icontains='Fayazuddin'
).order_by('created_at')
total_payments = 0

for payment in cash_payments:
    print(f"Cash Payment {payment.id} - {payment.reference_number}:")
    print(f"  Account: {payment.account}")
    print(f"  Credit Account: {payment.credit_account}")
    print(f"  Amount: {payment.debit_amount}")
    print(f"  Status: {payment.workflow_status}")
    print(f"  Date: {payment.date}")
    print()
    
    if payment.workflow_status in ['AUTHORIZED', 'POSTED']:
        total_payments += float(payment.debit_amount or 0)

print(f"💰 Total from Cash Payments: {total_payments:,.2f}")

print("\n=== 4. LEDGER ENTRIES ===")
capital_account = Account.objects.filter(
    name__icontains='Fayazuddin'
).filter(
    name__icontains='Capital'
).first()

if capital_account:
    print(f"Capital Account: {capital_account.account_number} - {capital_account.name}")
    
    ledger_entries = LedgerEntry.objects.filter(account=capital_account).order_by('created_at')
    total_debits = 0
    total_credits = 0
    
    for entry in ledger_entries:
        print(f"Ledger Entry {entry.id}:")
        print(f"  Type: {entry.entry_type}")
        print(f"  Amount: {entry.amount}")
        print(f"  Description: {entry.description}")
        print(f"  Reference: {entry.reference_number}")
        print(f"  Date: {entry.entry_date}")
        print()
        
        if entry.entry_type == 'DEBIT':
            total_debits += float(entry.amount or 0)
        else:
            total_credits += float(entry.amount or 0)
    
    print(f"💰 Total Debits to Capital Account: {total_debits:,.2f}")
    print(f"💰 Total Credits to Capital Account: {total_credits:,.2f}")
    print(f"💰 Net Capital Balance: {total_debits - total_credits:,.2f}")

print("\n=== 5. SUMMARY & DISCREPANCY CHECK ===")
print(f"Cash Receipts: {total_receipts:,.2f}")
print(f"Cash Payments: {total_payments:,.2f}")
print(f"Expected Total: {total_receipts + total_payments:,.2f}")
print(f"Capital Contributions Total: {total_contributions:,.2f}")

if abs(total_contributions - (total_receipts + total_payments)) > 0.01:
    print("❌ DISCREPANCY FOUND!")
    print(f"Difference: {total_contributions - (total_receipts + total_payments):,.2f}")
else:
    print("✅ Amounts match correctly")

print("\n=== 6. CHECKING FOR DUPLICATES ===")
# Check if there are duplicate entries
all_refs = []
if cash_receipts:
    for receipt in cash_receipts:
        all_refs.append(f"Receipt: {receipt.reference_number}")
        
if cash_payments:
    for payment in cash_payments:
        all_refs.append(f"Payment: {payment.reference_number}")
        
if contributions:
    for contrib in contributions:
        all_refs.append(f"Contribution: {contrib.reference_number}")

print("All reference numbers:")
for ref in all_refs:
    print(f"  {ref}")

# Check for duplicate reference numbers
duplicate_refs = []
seen_refs = set()
for ref in [r.split(': ')[1] for r in all_refs if ': ' in r]:
    if ref in seen_refs and ref != 'None':
        duplicate_refs.append(ref)
    seen_refs.add(ref)

if duplicate_refs:
    print(f"⚠️ Duplicate references found: {duplicate_refs}")
else:
    print("✅ No duplicate references")