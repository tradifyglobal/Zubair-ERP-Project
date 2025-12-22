from accounting.models import CapitalContribution

cc = CapitalContribution.objects.get(pk=3)
print(f'Status: {cc.status}')
print(f'Workflow Status: {cc.workflow_status}')
print(f'Submitted by: {cc.submitted_by}')
print(f'First Reviewer: {cc.first_reviewer}')
print(f'Second Reviewer: {cc.second_reviewer}')
print(f'Approved by: {cc.approved_by}')

