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

# Render full field HTML
print("Full field rendering:\n")
print("total_items_reconciled field:")
html = str(form['total_items_reconciled'])
print(html)
print(f"\nLength: {len(html)}")

print("\n\ndiscrepancies_found field:")
html = str(form['discrepancies_found'])
print(html)

print("\n\nstatus field:")
html = str(form['status'])
print(html[:300])
