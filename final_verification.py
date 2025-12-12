import os
import sys
import django

sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
os.chdir('/var/www/tradifyerp/TradifyERP')
django.setup()

from accounting.stakeholder_forms import StakeholderForm
from accounting.models import Stakeholder

# Test 1: Model has fields
print("=== MODEL CHECK ===")
model_fields = [f.name for f in Stakeholder._meta.get_fields()]
print(f"start_date in model: {('start_date' in model_fields)}")
print(f"end_date in model: {('end_date' in model_fields)}")

# Test 2: Form includes fields
print("\n=== FORM FIELDS CHECK ===")
form = StakeholderForm()
print(f"start_date in form.fields: {('start_date' in form.fields)}")
print(f"end_date in form.fields: {('end_date' in form.fields)}")

# Test 3: Layout includes fieldset
print("\n=== FORM LAYOUT CHECK ===")
fieldset_names = [f.legend if hasattr(f, 'legend') else None for f in form.helper.layout.fields]
has_profit_section = 'Profit Calculation Period (Optional)' in fieldset_names
print(f"Profit Calculation Period fieldset in layout: {has_profit_section}")

# Test 4: HTML rendering
print("\n=== HTML RENDERING CHECK ===")
html = str(form)
has_start_date_html = 'id_start_date' in html
has_end_date_html = 'id_end_date' in html
print(f"start_date input in HTML: {has_start_date_html}")
print(f"end_date input in HTML: {has_end_date_html}")

# Summary
print("\n=== SUMMARY ===")
all_good = all([
    'start_date' in model_fields,
    'end_date' in model_fields,
    'start_date' in form.fields,
    'end_date' in form.fields,
    has_profit_section,
    has_start_date_html,
    has_end_date_html
])

if all_good:
    print("✓ ALL CHECKS PASSED! The form is ready to use.")
    print("\nYou should now be able to:")
    print("1. Visit /admin/accounting/stakeholder/ to add/edit shareholders")
    print("2. See the 'Profit Calculation Period' section in the form")
    print("3. Enter start_date and end_date values")
else:
    print("✗ Some checks failed. Details above.")
