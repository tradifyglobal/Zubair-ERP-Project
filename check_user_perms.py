#!/usr/bin/env python
"""
Check Zubair user permissions for expenses module.
Run from TradifyERP directory: python check_user_perms.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

User = get_user_model()
u = User.objects.get(username='zubair')

print(f'User: {u.username}')
print(f'Is Staff: {u.is_staff}')
print(f'Is Superuser: {u.is_superuser}')
print(f'Groups: {[g.name for g in u.groups.all()]}')

# Check expenses app permissions
from expenses.models import EmployeeExpenseReport, ExpenseBudget, ExpenseReimbursement

print("\n=== Expenses Module Permissions ===")
print(f'Can view EmployeeExpenseReport: {u.has_perm("expenses.view_employeeexpensereport")}')
print(f'Can add EmployeeExpenseReport: {u.has_perm("expenses.add_employeeexpensereport")}')
print(f'Can view ExpenseBudget: {u.has_perm("expenses.view_expensebudget")}')
print(f'Can view ExpenseReimbursement: {u.has_perm("expenses.view_expensereimbursement")}')

# Check if user can see module
try:
    ct = ContentType.objects.get_for_model(EmployeeExpenseReport)
    perms = Permission.objects.filter(content_type=ct)
    print(f'\nAll permissions for expenses app: {[p.codename for p in perms]}')
except Exception as e:
    print(f'Error getting permissions: {e}')
