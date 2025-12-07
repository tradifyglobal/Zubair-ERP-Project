#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth.models import User

# Create superuser for production
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@tradifyerp.local', 'TradifyERP@123')
    print("✓ Superuser 'admin' created")
    print("  Username: admin")
    print("  Password: TradifyERP@123")
else:
    print("✗ Superuser 'admin' already exists")
