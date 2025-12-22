import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, '/var/www/tradifyerp')
os.chdir('/var/www/tradifyerp')

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
    from accounting.models import CashReceiptLine, CapitalContribution
    count = CashReceiptLine.objects.count()
    print('CashReceiptLine count:', count)
    
    # Test the signal system
    receipt = CashReceiptLine.objects.get(id=5)
    print('Test receipt found:', receipt.id, receipt.workflow_status, receipt.stakeholder)
    
    # Check existing contributions
    existing_contributions = CapitalContribution.objects.filter(source_cash_receipt_id=5)
    print('Existing contributions for receipt 5:', existing_contributions.count())
    
    # Now trigger the signal by saving the receipt
    print('Triggering signal by saving receipt...')
    receipt.save()
    
    # Check if capital contribution was created
    new_contributions = CapitalContribution.objects.filter(source_cash_receipt_id=5)
    print('Contributions after save:', new_contributions.count())
    
    if new_contributions.exists():
        for contrib in new_contributions:
            print(f'  - ID: {contrib.id}, Amount: {contrib.amount}, Currency: {contrib.currency.code} -> {contrib.currency_destination.code}')
    
    # Check if the receipt was marked as posted
    receipt.refresh_from_db()
    print('Receipt is_capital_contribution_posted:', receipt.is_capital_contribution_posted)
    
except Exception as e:
    print('Django database error:', str(e))
    import traceback
    traceback.print_exc()