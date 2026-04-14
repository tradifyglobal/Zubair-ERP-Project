#!/usr/bin/env python3
import sys
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'TradifyERP.settings_production'
os.chdir('/var/www/tradifyerp')
sys.path.insert(0, '/var/www/tradifyerp')

print("Testing Django settings load...")
try:
    import django
    django.setup()
    print("SUCCESS: Django setup completed")
    
    from django.conf import settings
    print(f"INSTALLED_APPS count: {len(settings.INSTALLED_APPS)}")
    
    # Check if raw_materials is there
    if 'raw_materials.apps.RawMaterialsConfig' in settings.INSTALLED_APPS:
        print("SUCCESS: raw_materials found in INSTALLED_APPS")
    else:
        print("ERROR: raw_materials NOT in INSTALLED_APPS")
        print("First 20 apps:")
        for app in settings.INSTALLED_APPS[:20]:
            print(f"  - {app}")
    
    # Try to access apps registry
    from django.apps import apps
    print(f"\nRegistered apps: {len(apps.get_app_configs())}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
