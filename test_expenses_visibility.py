#!/usr/bin/env python
"""
Test that expenses module shows in navigation for Zubair user.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.template import Template, Context

User = get_user_model()
zubair = User.objects.get(username='Zubair')

# Load the permission_tags module
from accounting.templatetags import permission_tags

# Test the filter directly
result = permission_tags.has_module_permission(zubair, 'expenses')
print(f"User: {zubair.username}")
print(f"Is Superuser: {zubair.is_superuser}")
print(f"has_module_permission filter for 'expenses': {result}")

# Test template rendering
template_str = "{% load permission_tags %}{% if user|has_module_permission:'expenses' %}VISIBLE{% else %}HIDDEN{% endif %}"
template = Template(template_str)
context = Context({'user': zubair})
rendered = template.render(context)

print(f"Template render result: {rendered}")
print(f"\n✓ Expense module should be {rendered} in navigation for Zubair")
