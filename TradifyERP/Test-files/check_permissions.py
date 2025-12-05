#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.contrib.auth.models import User

admin = User.objects.filter(username='admin').first()
if admin:
    has_perm = admin.has_perm('accounting.change_vendorpayment')
    print(f'Admin has change_vendorpayment: {has_perm}')
    print(f'Admin is_superuser: {admin.is_superuser}')
    if admin.is_superuser:
        print('Admin is superuser, so has all permissions')
else:
    print('Admin user not found')
