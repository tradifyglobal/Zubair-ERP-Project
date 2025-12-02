import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from accounting.models import CapitalContribution

# Update all SUBMITTED contributions to DRAFT
updated_count = CapitalContribution.objects.filter(workflow_status='SUBMITTED').update(workflow_status='DRAFT')

print(f"✓ Updated {updated_count} contributions from SUBMITTED to DRAFT status")

# Show the results
print("\nWorkflow status distribution:")
submissions = CapitalContribution.objects.values('workflow_status').distinct()
for status_dict in submissions:
    status = status_dict['workflow_status']
    count = CapitalContribution.objects.filter(workflow_status=status).count()
    print(f"  - {status}: {count} contributions")

print("\nDone!")
