import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'TradifyERP.settings_production'
django.setup()

from django.conf import settings
from django.db import connection

print('Django settings loaded')
print('DB ENGINE:', settings.DATABASES['default']['ENGINE'])
print('DB NAME:', settings.DATABASES['default']['NAME'])
print('DB HOST:', settings.DATABASES['default']['HOST'])

# Test Django database connection
try:
    cursor = connection.cursor()
    cursor.execute("SELECT current_database()")
    result = cursor.fetchone()
    print('Django connected to database:', result[0])
    cursor.close()
    
    # Now test the model
    from accounting.models import CashReceiptLine
    count = CashReceiptLine.objects.count()
    print('CashReceiptLine count:', count)
    
    # Test the signal system
    receipt = CashReceiptLine.objects.get(id=5)
    print('Test receipt found:', receipt.id, receipt.workflow_status, receipt.stakeholder)
    
except Exception as e:
    print('Django database error:', str(e))
    import traceback
    traceback.print_exc()