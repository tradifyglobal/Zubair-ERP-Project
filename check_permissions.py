#!/usr/bin/env python
import os
import django
import sys

sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from accounting.models import CapitalContribution

ct = ContentType.objects.get(app_label='accounting', model='capitalcontribution')
perms = Permission.objects.filter(content_type=ct)

print("=" * 70)
print("Existing permissions for CapitalContribution:")
print("=" * 70)
for p in perms:
    print(f"  - {p.codename}: {p.name}")

# Check if workflow permissions exist
reviewer_exists = Permission.objects.filter(content_type=ct, codename='workflow_reviewer').exists()
approver_exists = Permission.objects.filter(content_type=ct, codename='workflow_approver').exists()

print(f"\nWorkflow Reviewer permission exists: {reviewer_exists}")
print(f"Workflow Approver permission exists: {approver_exists}")

# Show users with these permissions if they exist
if reviewer_exists:
    reviewer_perm = Permission.objects.get(content_type=ct, codename='workflow_reviewer')
    users_with_reviewer = User.objects.filter(user_permissions=reviewer_perm)
    print(f"\nUsers with 'Workflow Reviewer' permission: {users_with_reviewer.count()}")
    for u in users_with_reviewer:
        print(f"  - {u.get_full_name()}")

if approver_exists:
    approver_perm = Permission.objects.get(content_type=ct, codename='workflow_approver')
    users_with_approver = User.objects.filter(user_permissions=approver_perm)
    print(f"\nUsers with 'Workflow Approver' permission: {users_with_approver.count()}")
    for u in users_with_approver:
        print(f"  - {u.get_full_name()}")
