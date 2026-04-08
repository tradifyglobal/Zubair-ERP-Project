#!/usr/bin/env python3
import sys
sys.path.insert(0, '/var/www/tradifyerp')
import os
os.chdir('/var/www/tradifyerp')

print("Attempting to import raw_materials...")
try:
    import raw_materials
    print("SUCCESS: raw_materials imported OK")
except Exception as e:
    print(f"ERROR importing raw_materials: {e}")
    import traceback
    traceback.print_exc()

print("\nChecking for admin.py syntax...")
try:
    import raw_materials.admin
    print("SUCCESS: admin.py imports OK")
except Exception as e:
    print(f"ERROR in admin.py: {e}")

print("\nChecking models...")
try:
    import raw_materials.models
    print("SUCCESS: models.py imports OK")
except Exception as e:
    print(f"ERROR in models.py: {e}")
    import traceback
    traceback.print_exc()
