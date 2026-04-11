import os
import sys
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings_production')
sys.path.insert(0, '/var/www/tradifyerp')

try:
    django.setup()
    print("Django setup successful")
    
    # Try to import the view
    from shareholder.views import ShareholderInvestmentReportView  
    print("View imported successfully")
    
    # Try to instantiate and check
    view = ShareholderInvestmentReportView.as_view()
    print("View instantiated successfully")
    
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
