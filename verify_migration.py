#!/usr/bin/env python
import os
import django
import sys

sys.path.insert(0, '/var/www/tradifyerp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
django.setup()

from accounting.models import CapitalContribution
from django.contrib.auth.models import Group

# Check if group fields exist in model
group_fields = [f.name for f in CapitalContribution._meta.get_fields() if 'group' in f.name.lower()]
print(f"✅ Group fields in model: {group_fields}")

# Check if Reviewers and Approvers groups exist
groups = Group.objects.filter(name__in=['Reviewers', 'Approvers'])
print(f"✅ Auth groups found: {[g.name for g in groups]}")

# Check database schema by querying all fields
db_fields = [f.name for f in CapitalContribution._meta.get_fields()]
print(f"✅ All CapitalContribution fields: {db_fields}")
