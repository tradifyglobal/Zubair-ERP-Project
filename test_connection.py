import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.conf import settings

print('DB ENGINE:', settings.DATABASES['default']['ENGINE'])
print('DB NAME:', settings.DATABASES['default']['NAME'])
print('DB HOST:', settings.DATABASES['default']['HOST'])
print('DB USER:', settings.DATABASES['default']['USER'])

# Test connection
from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute("SELECT current_database()")
    result = cursor.fetchone()
    print('Connected to database:', result[0])
    cursor.close()
except Exception as e:
    print('Database connection failed:', str(e))

# Test if signals are registered
from accounting import signals
print('Signals module loaded successfully')

# Test if the model exists  
from accounting.models import CashReceiptLine
count = CashReceiptLine.objects.count()
print('CashReceiptLine count:', count)