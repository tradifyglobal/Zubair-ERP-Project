#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, '/var/www/tradifyerp')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import CapitalContribution

contributions = CapitalContribution.objects.all().order_by('-id')[:10]

print("\nCapital Contributions (Last 10):")
print("-" * 120)
print(f"{'ID':<5} {'Stakeholder':<25} {'Amount':<15} {'Status':<15} {'Workflow Status':<20} {'Auto Posted':<12}")
print("-" * 120)

for cc in contributions:
    stakeholder_name = cc.stakeholder.name if cc.stakeholder else "N/A"
    amount = cc.amount_company_currency if cc.amount_company_currency else 0
    print(f"{cc.id:<5} {stakeholder_name:<25} {amount:<15} {cc.status:<15} {cc.workflow_status:<20} {str(cc.is_auto_posted):<12}")

print("-" * 120)
print(f"\nTotal records: {CapitalContribution.objects.count()}")
print(f"Approved: {CapitalContribution.objects.filter(workflow_status='APPROVED').count()}")
print(f"Auto-posted: {CapitalContribution.objects.filter(is_auto_posted=True).count()}")
