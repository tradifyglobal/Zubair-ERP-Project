#!/usr/bin/env python
"""
Diagnostic script for expense notification visibility issues
Run with: python manage.py shell < test_burhan_notifications.py
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

import django
django.setup()

from django.contrib.auth.models import User
from accounting.module_permissions import ModulePermission
from expenses.models import EmployeeExpenseReport
from expenses.notifications import (
    get_pending_reviews_for_user,
    get_pending_approvals_for_user,
    get_pending_final_approvals_for_user,
    get_all_pending_for_user
)

print("\n" + "="*70)
print("EXPENSE NOTIFICATION DIAGNOSTIC REPORT")
print("="*70)

# Get Burhan
try:
    burhan = User.objects.get(username='Burhan')
    print(f"\n✓ Found user: Burhan (ID: {burhan.id})")
except User.DoesNotExist:
    print("\n✗ ERROR: User 'Burhan' not found!")
    exit(1)

# Check user status
print(f"\nUser Status:")
print(f"  - is_active: {burhan.is_active}")
print(f"  - is_staff: {burhan.is_staff}")
print(f"  - is_superuser: {burhan.is_superuser}")

# Check ModulePermissions
print(f"\nModule Permissions for Burhan:")
perms = ModulePermission.objects.filter(user=burhan)
if perms.exists():
    for perm in perms:
        print(f"  - {perm.module}: can_view={perm.can_view}, can_approve={perm.can_approve}")
else:
    print(f"  ⚠ WARNING: No ModulePermission records found for Burhan!")
    print(f"             (Will fall back to is_staff check)")

# Check pending reports
print(f"\nPending Expense Reports in System:")
all_pending = EmployeeExpenseReport.objects.filter(status='PENDING_APPROVAL')
all_pending_review = EmployeeExpenseReport.objects.filter(status='PENDING_REVIEW')
print(f"  - PENDING_APPROVAL: {all_pending.count()} reports")
print(f"  - PENDING_REVIEW: {all_pending_review.count()} reports")

if all_pending.exists():
    print(f"\n  PENDING_APPROVAL Reports:")
    for report in all_pending[:5]:
        print(f"    • {report.report_number} - {report.total_amount}")

# Test notification functions
print(f"\nTesting Notification Functions for Burhan:")
print(f"  " + "-"*66)

# Test reviews
reviews = get_pending_reviews_for_user(burhan)
print(f"  - Pending Reviews: {reviews.count()}")
if reviews.exists():
    for report in reviews[:3]:
        print(f"      • {report.report_number}")

# Test approvals
approvals = get_pending_approvals_for_user(burhan)
print(f"  - Pending Approvals: {approvals.count()}")
if approvals.exists():
    for report in approvals[:3]:
        print(f"      • {report.report_number}")

# Test final approvals
final_approvals = get_pending_final_approvals_for_user(burhan)
print(f"  - Pending Final Approvals: {final_approvals.count()}")
if final_approvals.exists():
    for report in final_approvals[:3]:
        print(f"      • {report.report_number}")

# Get aggregated results
all_pending_for_burhan = get_all_pending_for_user(burhan)
total = all_pending_for_burhan.get('total_pending', 0)
print(f"\n  TOTAL PENDING for Burhan: {total}")

# Recommendations
print(f"\n" + "="*70)
print("RECOMMENDATIONS:")
print("="*70)

if total == 0:
    print("\n⚠ No pending notifications found for Burhan")
    print("\nPossible causes:")
    print("  1. No pending approval reports exist in system")
    print("  2. Reports exist but Burhan is not assigned as approver")
    print("  3. Reports are in wrong status")
    print("\nActions:")
    print("  1. Create test expense report and move to PENDING_APPROVAL")
    print("  2. Assign Burhan as approver in ExpenseApprovalWorkflow")
    print("  3. Verify report status is exactly 'PENDING_APPROVAL'")
elif not burhan.is_staff:
    print("\n✗ CRITICAL: Burhan is NOT a staff user!")
    print("\nFix: Make Burhan a staff user:")
    print("  burhan.is_staff = True")
    print("  burhan.save()")
elif not perms.filter(module='expenses', can_approve=True).exists():
    print("\n⚠ Burhan doesn't have explicit ModulePermission")
    print("\nBut is_staff=True, so should work with new fallback code")
    print("\nOptional: Create explicit permission for clarity:")
    print("  ModulePermission.objects.create(")
    print("      user=burhan,")
    print("      module='expenses',")
    print("      can_view=True,")
    print("      can_approve=True)")
else:
    print("\n✓ All checks passed!")
    print(f"\nBurhan should see {total} pending approval(s)")

print(f"\n" + "="*70)
print("END DIAGNOSTIC REPORT")
print("="*70 + "\n")
