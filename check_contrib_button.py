from accounting.models import CapitalContribution

cc = CapitalContribution.objects.get(pk=3)
print(f'ID: {cc.id}')
print(f'Status: {cc.status}')
print(f'Workflow Status: {cc.workflow_status}')
print(f'Submitted by: {cc.submitted_by}')
print(f'Submitted at: {cc.submitted_at}')
print(f'Can show review button: {cc.workflow_status in ["SUBMITTED", "FIRST_REVIEW_COMPLETED"]}')
