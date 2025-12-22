#!/usr/bin/env python
import os
import django
import sys

sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

# Get the permission
content_type = ContentType.objects.get(app_label='accounting', model='capitalcontribution')
reviewer_perm = Permission.objects.get(
    content_type=content_type,
    codename='workflow_reviewer'
)

# Get all active users
all_users = User.objects.filter(is_active=True).order_by('first_name', 'last_name')

print("=" * 70)
print("ACTIVE USERS AND REVIEWER PERMISSION STATUS")
print("=" * 70)

reviewers = []
non_reviewers = []

for user in all_users:
    has_perm = user.user_permissions.filter(pk=reviewer_perm.pk).exists()
    if has_perm:
        reviewers.append(user)
        status = "✅ HAS reviewer permission"
    else:
        non_reviewers.append(user)
        status = "❌ MISSING reviewer permission"
    
    print(f"{user.get_full_name() or user.username:30} | {status}")

print("\n" + "=" * 70)
print(f"REVIEWERS CONFIGURED: {len(reviewers)}")
print(f"NON-REVIEWERS: {len(non_reviewers)}")
print("=" * 70)

if reviewers:
    print("\n✅ Current Reviewers:")
    for user in reviewers:
        print(f"   - {user.get_full_name() or user.username}")
else:
    print("\n❌ NO REVIEWERS CONFIGURED - Submit will be disabled!")

if non_reviewers:
    print(f"\n📝 To add reviewers, go to Admin → Users and check 'Can review capital contributions' for:")
    for user in non_reviewers:
        print(f"   - {user.get_full_name() or user.username}")
