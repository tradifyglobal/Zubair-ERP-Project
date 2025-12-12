import os
import sys
import django

sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
os.chdir('/var/www/tradifyerp/TradifyERP')
django.setup()

from accounting.models import Stakeholder

model_fields = [f.name for f in Stakeholder._meta.get_fields()]
print("start_date in model:", "start_date" in model_fields)
print("end_date in model:", "end_date" in model_fields)
print("Total fields:", len(model_fields))
print("All fields:", model_fields)
