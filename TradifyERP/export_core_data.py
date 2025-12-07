#!/usr/bin/env python3
"""
Export core master data (entities, users, shareholders) without transactional data
to avoid FK relationship and signal issues during loaddata.
"""
import os
import sys
import django
import json

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.core.management import call_command
from io import StringIO

# Core models to export (master data only, no transactional records)
# Note: Users not included due to group/permission dependencies on development-only apps
CORE_MODELS = [
    'accounting.entity',
    'accounting.stakeholder',
    'accounting.shareholding',
]

output = StringIO()
try:
    call_command(
        'dumpdata',
        *CORE_MODELS,
        '--natural-foreign',
        '--natural-primary',
        stdout=output,
        stderr=StringIO()
    )
    
    json_data = output.getvalue()
    parsed = json.loads(json_data)
    
    # Fix null boolean values to False
    for obj in parsed:
        if 'fields' in obj:
            for key, value in obj['fields'].items():
                if value is None and 'is_' in key or 'same_as_' in key:
                    obj['fields'][key] = False
    
    print(f"✓ Exported {len(parsed)} core master data objects", file=sys.stderr)
    
    # Write with explicit UTF-8 encoding (no BOM)
    with open('dev_core_data.json', 'w', encoding='utf-8') as f:
        json.dump(parsed, f)
    
    size = os.path.getsize('dev_core_data.json')
    print(f"✓ Written to dev_core_data.json ({size} bytes)", file=sys.stderr)
    
except Exception as e:
    print(f"✗ Error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
