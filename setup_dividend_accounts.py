#!/usr/bin/env python
"""
Setup Drawings Accounts for Existing Stakeholders
Creates 3200-XX drawings/distribution accounts for all active stakeholders
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import Entity, Stakeholder
from accounting.stakeholder_account_helpers import bulk_setup_stakeholder_accounts

print("=" * 60)
print("STAKEHOLDER DIVIDEND ACCOUNT SETUP")
print("=" * 60)
print()
print("This script will create:")
print("  - Capital Accounts (3100-XX) for stakeholder investments")
print("  - Drawings Accounts (3200-XX) for profit distributions")
print()
print("=" * 60)
print()

# Get all active entities
entities = Entity.objects.filter(is_active=True)

if not entities.exists():
    print("⚠️  No active entities found!")
    exit(1)

print(f"Found {entities.count()} active entity/entities:")
for entity in entities:
    print(f"  • {entity.name}")
print()

# Confirm before proceeding
response = input("Proceed with account setup? (yes/no): ").strip().lower()
if response not in ['yes', 'y']:
    print("\n❌ Setup cancelled.")
    exit(0)

print()
print("=" * 60)
print("PROCESSING STAKEHOLDERS...")
print("=" * 60)
print()

total_summary = {
    'total_stakeholders': 0,
    'capital_accounts_created': 0,
    'drawings_accounts_created': 0,
    'errors': []
}

for entity in entities:
    print(f"\n📊 Entity: {entity.name}")
    print("-" * 60)
    
    # Get summary for this entity
    summary = bulk_setup_stakeholder_accounts(entity)
    
    # Update totals
    total_summary['total_stakeholders'] += summary['total_stakeholders']
    total_summary['capital_accounts_created'] += summary['capital_accounts_created']
    total_summary['drawings_accounts_created'] += summary['drawings_accounts_created']
    total_summary['errors'].extend(summary['errors'])
    
    # Print entity summary
    print(f"  Stakeholders processed: {summary['total_stakeholders']}")
    print(f"  Capital accounts created: {summary['capital_accounts_created']}")
    print(f"  Drawings accounts created: {summary['drawings_accounts_created']}")
    
    if summary['errors']:
        print(f"  ⚠️  Errors: {len(summary['errors'])}")
        for error in summary['errors']:
            print(f"    - {error}")

print()
print("=" * 60)
print("FINAL SUMMARY")
print("=" * 60)
print(f"Total stakeholders processed: {total_summary['total_stakeholders']}")
print(f"Capital accounts created: {total_summary['capital_accounts_created']}")
print(f"Drawings accounts created: {total_summary['drawings_accounts_created']}")

if total_summary['errors']:
    print(f"\n⚠️  Total errors: {len(total_summary['errors'])}")
    print("\nError details:")
    for error in total_summary['errors']:
        print(f"  - {error}")
else:
    print("\n✅ All accounts created successfully!")

print()
print("=" * 60)
print("ACCOUNT STRUCTURE CREATED:")
print("=" * 60)
print()
print("📁 3100 - Capital / Equity")
print("   ├── 3100-01 - [Stakeholder Name] - Capital")
print("   ├── 3100-02 - [Stakeholder Name] - Capital")
print("   └── ... (one per stakeholder)")
print()
print("📁 3200 - Drawings / Distributions (Contra-Equity)")
print("   ├── 3200-01 - [Stakeholder Name] - Drawings")
print("   ├── 3200-02 - [Stakeholder Name] - Drawings")
print("   └── ... (one per stakeholder)")
print()
print("=" * 60)
print()
print("✨ Setup complete!")
print()
