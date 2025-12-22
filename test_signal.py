#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import CashReceiptLine, CapitalContribution

# Test the signal manually
print("Testing automatic capital contribution creation...")

# Get the test cash receipt
receipt = CashReceiptLine.objects.get(id=5)
print(f"Cash Receipt ID: {receipt.id}")
print(f"Stakeholder: {receipt.stakeholder}")
print(f"Amount: {receipt.debit_amount}")
print(f"Currency: {receipt.currency}")
print(f"Workflow Status: {receipt.workflow_status}")
print(f"Is Capital Contribution Posted: {receipt.is_capital_contribution_posted}")

# Check if capital contribution exists
existing_contributions = CapitalContribution.objects.filter(source_cash_receipt_id=receipt.id)
print(f"Existing contributions from this receipt: {existing_contributions.count()}")

if existing_contributions.exists():
    for contrib in existing_contributions:
        print(f"  - Contribution ID {contrib.id}: {contrib.amount} {contrib.currency.code} -> {contrib.currency_destination.code}")

# Trigger the signal by saving (this should create capital contribution)
print("\nTriggering signal by saving the receipt...")
receipt.save()

# Check again after save
receipt.refresh_from_db()
print(f"Is Capital Contribution Posted (after save): {receipt.is_capital_contribution_posted}")

# Check for new contributions
new_contributions = CapitalContribution.objects.filter(source_cash_receipt_id=receipt.id)
print(f"Capital contributions after save: {new_contributions.count()}")

if new_contributions.exists():
    for contrib in new_contributions:
        print(f"  - Contribution ID {contrib.id}: {contrib.amount} {contrib.currency.code} -> {contrib.currency_destination.code}")
        print(f"    Entity currency: {contrib.entity.company_currency}")
        print(f"    Auto posted: {contrib.is_auto_posted}")

print("Test completed.")