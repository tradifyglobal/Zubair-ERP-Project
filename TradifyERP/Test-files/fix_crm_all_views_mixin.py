#!/usr/bin/env python
"""
Add SessionEntityMixin to all remaining CRM views
"""

import re

# Read the file
with open('crm/views.py', 'r') as f:
    content = f.read()

# Pattern to find class declarations with LoginRequiredMixin
# We need to be careful not to replace ones already with SessionEntityMixin
pattern = r'class\s+(\w+)\((SessionEntityMixin,\s+)?LoginRequiredMixin,\s+(\w+View)\):'

def replace_class(match):
    class_name = match.group(1)
    has_mixin = match.group(2)
    view_type = match.group(3)
    
    if has_mixin:
        # Already has SessionEntityMixin
        return match.group(0)
    else:
        # Add SessionEntityMixin
        return f'class {class_name}(SessionEntityMixin, LoginRequiredMixin, {view_type}):'

content = re.sub(pattern, replace_class, content)

# Write the file back
with open('crm/views.py', 'w') as f:
    f.write(content)

print("✅ CRM views updated with SessionEntityMixin!")
print("   - All List, Detail, Create, Update, Delete views now inherit SessionEntityMixin")
