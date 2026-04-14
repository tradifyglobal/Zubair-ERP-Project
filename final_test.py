import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TradifyERP.settings_production")
sys.path.insert(0, '/var/www/tradifyerp')

import django
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User

from shareholder.views import ShareholderInvestmentReportView

# Create a test request
factory = RequestFactory()
request = factory.get('/shareholder/investment-report/')

# Add session middleware
from django.contrib.sessions.middleware import SessionMiddleware
middleware = SessionMiddleware(lambda x: None)
middleware.process_request(request)
request.session.save()

# Set entity to Pristine Planet
request.session['selected_entity_id'] = 9

# Add a user
user = User.objects.filter(is_active=True).first()
if user:
    request.user = user
else:
    print("No active user found!")
    sys.exit(1)

# Create the view and get context
view = ShareholderInvestmentReportView()
view.request = request
view.setup(request)

try:
    context = view.get_context_data()
    
    print(f"Total investment_data records: {len(context.get('investment_data', []))}")
    print(f"Total pending in foreign bank (context): {context.get('total_pending_in_foreign_bank')}")
    
    # Check specific stakeholders
    for inv in context.get('investment_data', []):
        stakeholder = inv['stakeholder']
        if stakeholder.first_name in ['Mohammed', 'Syed']:
            print(f"\n{stakeholder.first_name} {stakeholder.last_name}:")
            print(f"  pending_in_foreign_bank: {inv.get('pending_in_foreign_bank')}")
            print(f"  Type: {type(inv.get('pending_in_foreign_bank'))}")
            print(f"  Keys in dict: {list(inv.keys())}")
            
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
