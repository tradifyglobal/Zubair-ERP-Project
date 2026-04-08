#!/usr/bin/env python3
"""
Simple column addition without constraints
"""

import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp')

import django
django.setup()

from django.db import connection, DatabaseError
from django.db.migrations.executor import MigrationExecutor

executor = MigrationExecutor(connection)
executor.migrate([('maintenance', '0003_maintenanceasset_purchase_account')], fake_initial=False)

print("✓ Migration applied")
