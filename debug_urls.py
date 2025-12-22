#!/usr/bin/env python
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp')

import django
django.setup()

print("Testing import of urls_trial_balance...")

try:
    from accounting.urls_trial_balance import urlpatterns as trial_balance_urlpatterns
    print(f"SUCCESS! Imported {len(trial_balance_urlpatterns)} URL patterns:")
    for p in trial_balance_urlpatterns:
        if hasattr(p, 'name'):
            print(f"  - {p.name}")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n\nNow testing the actual import from accounting/urls.py...")
try:
    from accounting import urls
    print(f"accounting.urls has {len(urls.urlpatterns)} total patterns")
    trial_patterns = [p for p in urls.urlpatterns if hasattr(p, 'name') and p.name and 'trial' in p.name.lower()]
    print(f"Found {len(trial_patterns)} trial-related patterns:")
    for p in trial_patterns:
        print(f"  - {p.name}")
except Exception as e:
    print(f"Error loading accounting.urls: {e}")
    import traceback
    traceback.print_exc()
