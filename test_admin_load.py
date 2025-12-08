#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')

django.setup()

try:
    from accounting.admin import CustomUserAdmin, ModulePermissionInline
    print('Admin classes loaded successfully!')
    print(f'CustomUserAdmin has inlines: {hasattr(CustomUserAdmin, "inlines")}')
    if hasattr(CustomUserAdmin, 'inlines') and CustomUserAdmin.inlines:
        print(f'Number of inlines: {len(CustomUserAdmin.inlines)}')
        for inline in CustomUserAdmin.inlines:
            print(f'  - {inline.__name__}')
    else:
        print('No inlines found or inlines is empty')
except Exception as e:
    print(f'Error loading admin: {e}')
    import traceback
    traceback.print_exc()
