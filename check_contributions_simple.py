from accounting.models import CapitalContribution, Stakeholder
from datetime import datetime, date

# Search for entries from Dec 15, 2025
target_date = date(2025, 12, 15)
contributions = CapitalContribution.objects.filter(contribution_date=target_date)
print(f'Found {contributions.count()} contributions on Dec 15, 2025:')

for contrib in contributions:
    print(f'- ID: {contrib.id}, Stakeholder: {contrib.stakeholder.full_name}, Amount: {contrib.amount}, Status: {contrib.status}, Workflow Status: {contrib.workflow_status}')

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
            
            # Get recent contributions for this stakeholder
            recent_contribs = CapitalContribution.objects.filter(
                stakeholder=stakeholder
            ).order_by('-contribution_date')[:5]
            
            print(f'Total contributions: {CapitalContribution.objects.filter(stakeholder=stakeholder).count()}')
            print('Recent contributions:')
            for contrib in recent_contribs:
                print(f'  - Date: {contrib.contribution_date}, Amount: {contrib.amount}, Status: {contrib.status}, Workflow: {contrib.workflow_status}, Ref: {contrib.reference_number}')
        else:
            print(f'No stakeholder found for: {name}')

# Check specifically for the mentioned reference numbers
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

print('\n=== Checking workflow status filtering ===')
# Check what statuses exist and might be filtering out the entries
all_contributions = CapitalContribution.objects.all()
print(f'Total contributions in system: {all_contributions.count()}')

status_counts = {}
workflow_status_counts = {}

for contrib in all_contributions:
    status = contrib.status or 'NULL'
    workflow_status = contrib.workflow_status or 'NULL'
    
    status_counts[status] = status_counts.get(status, 0) + 1
    workflow_status_counts[workflow_status] = workflow_status_counts.get(workflow_status, 0) + 1

print('\nStatus distribution:')
for status, count in status_counts.items():
    print(f'  {status}: {count}')

print('\nWorkflow status distribution:')
for workflow_status, count in workflow_status_counts.items():
    print(f'  {workflow_status}: {count}')