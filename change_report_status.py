#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from TradifyERP.expenses.models import EmployeeExpenseReport, ExpenseApprovalWorkflow
from TradifyERP.accounting.models import AuditLog
from django.utils import timezone

# Find the report ID 1 (the one from your list)
report = EmployeeExpenseReport.objects.get(id=1)

print(f"Report ID: {report.id}")
print(f"Employee: {report.employee.user.first_name} {report.employee.user.last_name}")
print(f"Current Status: {report.status}")
print(f"Amount: ${report.total_amount}")
print(f"Submitted: {report.submitted_at}")

# Change status back to DRAFT
if report.status == 'PENDING_REVIEW':
    old_status = report.status
    report.status = 'DRAFT'
    report.submitted_by = None
    report.submitted_at = None
    report.save()
    
    # Reset workflow
    try:
        workflow = report.approval_workflow
        workflow.status = 'DRAFT'
        workflow.save()
    except ExpenseApprovalWorkflow.DoesNotExist:
        pass
    
    # Create audit log
    AuditLog.objects.create(
        entity=report.entity,
        action='UPDATE_STATUS',
        model_name='EmployeeExpenseReport',
        object_id=str(report.id),
        user='admin',
        description=f"Admin changed expense report status back to DRAFT: {report}",
        old_values={'status': old_status},
        new_values={'status': 'DRAFT'}
    )
    
    print(f"✓ Status changed to DRAFT")
else:
    print(f"Report is in {report.status} status, no change made")
