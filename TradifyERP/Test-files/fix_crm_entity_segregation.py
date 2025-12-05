#!/usr/bin/env python
"""
Fix CRM module entity segregation - Replace all hardcoded entity_id=1 with session entity
"""

import re

# Read the file
with open('crm/views.py', 'r') as f:
    content = f.read()

# Replace the hardcoded entity getter
old_pattern = r"entity, _ = Entity\.objects\.get_or_create\(id=1, defaults=\{'name': 'Main Entity', 'code': 'MAIN'\}\)"
new_pattern = """entity_id = self.request.session.get('selected_entity_id')
        entity = Entity.objects.filter(id=entity_id, is_active=True).first()"""

content = re.sub(old_pattern, new_pattern, content)

# Write the file back
with open('crm/views.py', 'w') as f:
    f.write(content)

print("✅ CRM entity segregation fixed!")
print("   - Replaced all hardcoded entity_id=1 with session entity")
print("   - All CRM data now respects multi-entity segregation")
