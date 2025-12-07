"""
Find CreateViews that are missing form_valid
"""
import re

with open('TradifyERP/manufacturing/views.py', 'r') as f:
    content = f.read()

# Find all CreateView classes
create_views = re.findall(r'class (\w+CreateView).*?(?=class |\Z)', content, re.DOTALL)

# Check which ones have form_valid
for view_text in create_views:
    if 'form_valid' not in view_text:
        # Extract just the class name
        class_name = re.search(r'(\w+CreateView)', view_text)
        if class_name:
            print(f"❌ Missing form_valid: {class_name.group(1)}")
    else:
        class_name = re.search(r'(\w+CreateView)', view_text)
        if class_name:
            print(f"✅ Has form_valid: {class_name.group(1)}")
