#!/usr/bin/env python
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')

try:
    from TradifyERP.wsgi import application
    print("✓ WSGI application imported successfully")
except Exception as e:
    print(f"✗ Failed to import WSGI: {e}")
    import traceback
    traceback.print_exc()
