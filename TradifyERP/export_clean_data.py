#!/usr/bin/env python
"""Export development database to clean UTF-8 JSON without any BOM."""
import os
import sys
import json

# Add Django to path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

# Setup Django
import django
django.setup()

from django.core.management import call_command
from io import StringIO

# Export to StringIO buffer
output = StringIO()
try:
    call_command('dumpdata', '--all', '--natural-foreign', '--natural-primary',
                 stdout=output, stderr=StringIO())  # Suppress warnings
    json_data = output.getvalue()
    
    # Validate JSON
    parsed = json.loads(json_data)
    print(f"✓ Exported {len(parsed)} objects", file=sys.stderr)
    
    # Write to file with explicit UTF-8 encoding (no BOM)
    with open('dev_data_export.json', 'w', encoding='utf-8-sig') as f:
        # Remove BOM that utf-8-sig adds by writing without it first
        with open('dev_data_export.json', 'w', encoding='utf-8') as clean_f:
            clean_f.write(json_data)
    
    size = os.path.getsize('dev_data_export.json')
    print(f"✓ Written to dev_data_export.json ({size} bytes)", file=sys.stderr)
    
except Exception as e:
    print(f"✗ Error: {e}", file=sys.stderr)
    sys.exit(1)
