#!/usr/bin/env python3

import os
import sys
import django

# Add the project path
sys.path.append('/var/www/tradifyerp')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tradifyerp.settings')
django.setup()

from accounting.models import CapitalContribution, Stakeholder
from datetime import datetime, date

def check_missing_contributions():
    """Check for the specific missing contributions mentioned by user"""
    print("=== Checking for Missing Capital Contributions ===")
    
    # Search for entries from Dec 15, 2025
    target_date = date(2025, 12, 15)
    contributions = CapitalContribution.objects.filter(contribution_date=target_date)
    print(f'\nFound {contributions.count()} contributions on Dec 15, 2025:')
    
    for contrib in contributions:
        print(f'- ID: {contrib.id}')
        print(f'  Stakeholder: {contrib.stakeholder.full_name}')
        print(f'  Amount: {contrib.amount} {contrib.currency.code if contrib.currency else "N/A"}')
        print(f'  Status: {contrib.status}')
        print(f'  Workflow Status: {contrib.workflow_status}')
        print(f'  Reference: {contrib.reference_number}')
        print()
    
    # Search by stakeholder names mentioned in the user report
    stakeholder_names = ['Syed Safi', 'Burhanuddin Shaik', 'Ansaar Mohammed']
    
    for name in stakeholder_names:
        print(f'\n=== Checking contributions for: {name} ===')
        parts = name.split()
        if len(parts) >= 2:
            first_name = parts[0]
            last_name = ' '.join(parts[1:])
            
            # Try exact match first
            stakeholder = Stakeholder.objects.filter(
                first_name__iexact=first_name, 
                last_name__iexact=last_name
            ).first()
            
            # If not found, try partial match
            if not stakeholder:
                stakeholder = Stakeholder.objects.filter(
                    first_name__icontains=first_name, 
                    last_name__icontains=last_name
                ).first()
            
            if stakeholder:
                print(f'Found stakeholder: {stakeholder.full_name} (ID: {stakeholder.id})')
                
                # Get all contributions for this stakeholder
                all_contribs = CapitalContribution.objects.filter(
                    stakeholder=stakeholder
                ).order_by('-contribution_date')
                
                print(f'Total contributions: {all_contribs.count()}')
                
                # Show recent contributions
                recent_contribs = all_contribs[:5]
                print('Recent contributions:')
                for contrib in recent_contribs:
                    print(f'  - Date: {contrib.contribution_date}')
                    print(f'    Amount: {contrib.amount} {contrib.currency.code if contrib.currency else "N/A"}')
                    print(f'    Status: {contrib.status}')
                    print(f'    Workflow Status: {contrib.workflow_status}')
                    print(f'    Reference: {contrib.reference_number}')
                    print()
            else:
                print(f'No stakeholder found for: {name}')
    
    # Check specifically for the mentioned reference numbers/amounts
    print('\n=== Checking by Reference Numbers ===')
    ref_numbers = ['3000-16', '3000-18', '3000-09']
    
    for ref in ref_numbers:
        contributions = CapitalContribution.objects.filter(
            reference_number__icontains=ref
        )
        print(f'Reference {ref}: {contributions.count()} contributions found')
        for contrib in contributions:
            print(f'  - ID: {contrib.id}, Date: {contrib.contribution_date}, Stakeholder: {contrib.stakeholder.full_name}, Status: {contrib.status}, Workflow: {contrib.workflow_status}')
    
    # Check by amounts mentioned
    print('\n=== Checking by Amounts ===')
    amounts = [5000.00, 6000.00]
    
    for amount in amounts:
        contributions = CapitalContribution.objects.filter(
            amount=amount,
            contribution_date__gte=date(2025, 12, 1)  # This month
        )
        print(f'Amount {amount}: {contributions.count()} contributions found')
        for contrib in contributions:
            print(f'  - ID: {contrib.id}, Date: {contrib.contribution_date}, Stakeholder: {contrib.stakeholder.full_name}, Status: {contrib.status}, Workflow: {contrib.workflow_status}')

if __name__ == '__main__':
    check_missing_contributions()