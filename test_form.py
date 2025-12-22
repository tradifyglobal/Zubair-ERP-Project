import os
import sys
import django

# Set up Django
sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
os.chdir('/var/www/tradifyerp/TradifyERP')
django.setup()

from accounting.stakeholder_forms import StakeholderForm
from accounting.models import Stakeholder

# Create a form instance
form = StakeholderForm()

# Check if fields are present
print("start_date in form.fields:", "start_date" in form.fields)
print("end_date in form.fields:", "end_date" in form.fields)
print("Total fields in form:", len(form.fields))

# Check the layout
print("\nLayout fields count:", len(form.helper.layout.fields))

# Check if Profit Calculation Period is in layout
for i, field in enumerate(form.helper.layout.fields):
    if hasattr(field, 'legend'):
        print(f"Fieldset {i}: {field.legend}")
    else:
        print(f"Field {i}: {type(field).__name__}")
