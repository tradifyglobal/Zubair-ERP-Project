import os
import sys
import django

sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
os.chdir('/var/www/tradifyerp/TradifyERP')
django.setup()

from accounting.forms_extended import QuickAddReconciliationRecordForm
from accounting.models import Entity

# Create a form instance
entity = Entity.objects.filter(is_active=True).first()
form = QuickAddReconciliationRecordForm(entity=entity)

# Check fields
print("Form fields:")
for field_name, field in form.fields.items():
    print(f"  {field_name}: {field.__class__.__name__}")
    print(f"    widget: {field.widget.__class__.__name__}")
    print(f"    widget attrs: {field.widget.attrs}")

# Render the form
print("\n\nForm HTML:\n")
for field_name, field in form.fields.items():
    html = str(form[field_name])
    print(f"\n{field_name}:")
    print(html[:200] if len(html) > 200 else html)
