#!/usr/bin/env python
"""
List all users in the database.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
users = User.objects.all()

print(f"Total users: {users.count()}\n")
for u in users:
    print(f"Username: {u.username:20} | Email: {u.email:40} | Staff: {u.is_staff} | Active: {u.is_active} | Superuser: {u.is_superuser}")
