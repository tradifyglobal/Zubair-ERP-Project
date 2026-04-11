#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from accounting.models import Entity
pp = Entity.objects.filter(name='Pristine Planet').first()
print(pp.id if pp else 'NOT FOUND')
