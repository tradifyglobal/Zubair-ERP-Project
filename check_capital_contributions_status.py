#!/usr/bin/env python
"""Check workflow status of capital contributions for stakeholders."""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, '/git-app-repo/Zubair-ERP-Project')
django.setup()

from accounting.models import Stakeholder, CapitalContribution

# Get all stakeholders with capital contributions
stakeholders = Stakeholder.objects.filter(capital_contributions__isnull=False).distinct()

print("\n" + "="*80)
print("CAPITAL CONTRIBUTIONS BY STAKEHOLDER")
print("="*80)

for stakeholder in stakeholders:
    print(f"\n{stakeholder.full_name} (ID: {stakeholder.id})")
    print("-" * 80)
    
    contributions = stakeholder.capital_contributions.all()
    print(f"  Total contributions: {contributions.count()}")
    
    # Group by workflow_status
    statuses = {}
    for cc in contributions:
        if cc.workflow_status not in statuses:
            statuses[cc.workflow_status] = 0
        statuses[cc.workflow_status] += 1
    
    print("\n  Status breakdown:")
    for status, count in sorted(statuses.items()):
        print(f"    - {status}: {count}")
    
    # Show each contribution
    print("\n  Details:")
    for cc in contributions.order_by('contribution_date'):
        print(f"    - Date: {cc.contribution_date}")
        print(f"      Amount: {cc.amount_company_currency} {cc.currency if hasattr(cc, 'currency') else 'PKR'}")
        print(f"      Workflow Status: {cc.workflow_status}")
        print(f"      Status: {cc.status}")
        print()
    
    # Show calculated total_invested
    print(f"  Calculated total_invested: {stakeholder.total_invested}")
    print()

print("\n" + "="*80)
