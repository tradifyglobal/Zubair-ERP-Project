import os
import sys
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TradifyERP.settings_production")
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

from django.test import RequestFactory
from shareholder.views import ShareholderInvestmentReportView
from django.contrib.auth.models import User
from accounting.models import Entity

# Create a fake request
factory = RequestFactory()
request = factory.get('/shareholder/investment-report/')

# Add a session to the request
from django.contrib.sessions.middleware import SessionMiddleware
middleware = SessionMiddleware(lambda x: None)
middleware.process_request(request)
request.session.save()

# Set the entity to Pristine Planet (ID 9)
request.session['selected_entity_id'] = 9

# Add user
request.user = User.objects.filter(username='zubair').first() or User.objects.first()

# Get the view and call get_context_data
view = ShareholderInvestmentReportView()
view.request = request

# Initialize the view
view.setup(request)

# Get context
context = view.get_context_data()

# Print investment data for verification
if 'investment_data' in context and context['investment_data']:
    print(f"Total records: {len(context['investment_data'])}")
    print(f"\nChecking for pending amounts:")
    for inv in context['investment_data']:
        pending = inv.get('pending_in_foreign_bank')
        if pending:
            print(f"  {inv['stakeholder'].full_name}: {pending} (type: {type(pending).__name__})")
    
    print(f"\nTotal pending in foreign bank: {context.get('total_pending_in_foreign_bank')}")
else:
    print("No investment_data in context!")
