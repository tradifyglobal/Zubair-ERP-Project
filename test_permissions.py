#!/usr/bin/env python
"""
Test has_module_permission for Zubair user.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounting.module_permissions import ModulePermission

User = get_user_model()
u = User.objects.get(username='Zubair')

print(f"User: {u.username}")
print(f"Is Superuser: {u.is_superuser}")
print(f"Is Staff: {u.is_staff}")
print(f"Is Authenticated: {u.is_authenticated}")

# Test the filter logic directly
if u.is_superuser:
    result = True
else:
    result = ModulePermission.user_can_access_module(u, 'expenses')

print(f"\nhas_module_permission:'expenses' result: {result}")

# Also test each module
modules = ['accounting', 'shareholder', 'expenses', 'hr', 'manufacturing', 'sales', 'inventory', 'ap', 'procurement', 'cash_management', 'projects', 'crm', 'ar', 'maintenance']
print(f"\nModule visibility for Zubair:")
for module in modules:
    if u.is_superuser:
        visible = True
    else:
        visible = ModulePermission.user_can_access_module(u, module)
    print(f"  {module:20} - {'VISIBLE' if visible else 'HIDDEN'}")
