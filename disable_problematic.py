#!/usr/bin/env python3
import os
import glob
import re

os.chdir('/var/www/tradifyerp/TradifyERP')

# Disable problematic migrations
problematic = [
    r'crm/migrations/0004_.*\.py$',
    r'crm/migrations/0005_.*\.py$',
    r'sales/migrations/0003_.*\.py$',
    r'sales/migrations/0004_.*\.py$',
    r'sales/migrations/0005_.*\.py$',
    r'sales/migrations/0006_.*\.py$',
]

disabled = 0
for pattern in problematic:
    for f in glob.glob('**/*.py', recursive=True):
        if re.search(pattern, f) and not f.endswith('.disabled'):
            new_name = f + '.disabled'
            os.rename(f, new_name)
            print(f"Disabled: {os.path.basename(f)}")
            disabled += 1

print(f"\nTotal disabled: {disabled}")

# Count remaining disabled
remaining_disabled = len(glob.glob('**/*.disabled', recursive=True))
print(f"Total .disabled files: {remaining_disabled}")
