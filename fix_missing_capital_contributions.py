#!/usr/bin/env python3

import os
import sys
import django
from decimal import Decimal
from datetime import date

# Add the project path
sys.path.append('/var/www/tradifyerp')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tradifyerp.settings')
django.setup()

from accounting.models import (
    CapitalContribution, Stakeholder, Entity, Currency, 
    CashReceiptLine, Account
)

def create_missing_capital_contributions():
    """Create the missing capital contributions from cash receipt data"""
    
    print("=== Creating Missing Capital Contributions ===")
    
    # Get the entity (Testing entity where the cash receipts exist)
    entity = Entity.objects.get(id=7, name='Testing')
    print(f"Using entity: {entity.name} (ID: {entity.id})")
    
    # Get default currency (assuming USD or company currency)
    currency = Currency.objects.filter(is_default=True).first()
    if not currency:
        currency = Currency.objects.first()
    print(f"Using currency: {currency.code}")
    
    # Get stakeholders
    syed_safi = Stakeholder.objects.get(id=3, first_name='Syed', last_name='Safi')
    burhanuddin_shaik = Stakeholder.objects.get(id=18, first_name='Burhanuddin', last_name='Shaik')
    ansaar_mohammed = Stakeholder.objects.get(id=7, first_name='Ansaar', last_name='Mohammed')
    
    print(f"Found stakeholders:")
    print(f"- {syed_safi.first_name} {syed_safi.last_name} (ID: {syed_safi.id})")
    print(f"- {burhanuddin_shaik.first_name} {burhanuddin_shaik.last_name} (ID: {burhanuddin_shaik.id})")
    print(f"- {ansaar_mohammed.first_name} {ansaar_mohammed.last_name} (ID: {ansaar_mohammed.id})")
    
    contributions_to_create = [
        {
            'stakeholder': syed_safi,
            'amount': Decimal('5000.00'),
            'reference_number': '3000-16',
            'description': 'Capital contribution from test5 cash receipt'
        },
        {
            'stakeholder': burhanuddin_shaik,
            'amount': Decimal('6000.00'),
            'reference_number': '3000-18',
            'description': 'Capital contribution from test5 cash receipt'
        },
        {
            'stakeholder': ansaar_mohammed,
            'amount': Decimal('3000.00'),  # Assuming the user meant 3000, not 200
            'reference_number': '3000-09',
            'description': 'Capital contribution from test6 cash receipt (corrected amount)'
        }
    ]
    
    print(f"\n=== Creating Capital Contributions ===")
    
    for contrib_data in contributions_to_create:
        try:
            # Check if contribution already exists
            existing = CapitalContribution.objects.filter(
                stakeholder=contrib_data['stakeholder'],
                contribution_date=date(2025, 12, 15),
                amount=contrib_data['amount']
            ).first()
            
            if existing:
                print(f"✓ Capital contribution already exists for {contrib_data['stakeholder'].first_name} {contrib_data['stakeholder'].last_name}")
                continue
            
            # Create the capital contribution
            contribution = CapitalContribution.objects.create(
                entity=entity,
                stakeholder=contrib_data['stakeholder'],
                contribution_date=date(2025, 12, 15),
                amount=contrib_data['amount'],
                currency=currency,
                currency_destination=currency,
                exchange_rate=Decimal('1.00'),
                amount_company_currency=contrib_data['amount'],
                status='COMPLETED',
                workflow_status='APPROVED',  # Set as approved so it shows in reports
                payment_mode='CASH',
                reference_number=contrib_data['reference_number'],
                notes=contrib_data['description']
            )
            
            print(f"✓ Created capital contribution:")
            print(f"  - ID: {contribution.id}")
            print(f"  - Stakeholder: {contribution.stakeholder.first_name} {contribution.stakeholder.last_name}")
            print(f"  - Amount: {contribution.amount}")
            print(f"  - Reference: {contribution.reference_number}")
            print(f"  - Status: {contribution.status} / {contribution.workflow_status}")
            
        except Exception as e:
            print(f"✗ Error creating contribution for {contrib_data['stakeholder'].first_name} {contrib_data['stakeholder'].last_name}: {str(e)}")
    
    print(f"\n=== Summary ===")
    
    # Count contributions by stakeholder
    for stakeholder in [syed_safi, burhanuddin_shaik, ansaar_mohammed]:
        count = CapitalContribution.objects.filter(stakeholder=stakeholder).count()
        print(f"- {stakeholder.first_name} {stakeholder.last_name}: {count} contributions")
    
    # Total contributions on Dec 15, 2025
    dec15_contributions = CapitalContribution.objects.filter(contribution_date=date(2025, 12, 15))
    print(f"\nTotal contributions on Dec 15, 2025: {dec15_contributions.count()}")
    for contrib in dec15_contributions:
        print(f"  - {contrib.stakeholder.first_name} {contrib.stakeholder.last_name}: {contrib.amount} ({contrib.workflow_status})")

if __name__ == '__main__':
    create_missing_capital_contributions()