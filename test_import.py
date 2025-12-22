#!/usr/bin/env python
import sys
sys.path.insert(0, '/var/www/tradifyerp')

try:
    from accounting.urls_trial_balance import urlpatterns
    print(f"SUCCESS: Loaded {len(urlpatterns)} URL patterns")
    for p in urlpatterns:
        if hasattr(p, 'name'):
            print(f"  - {p.name}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
