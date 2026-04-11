#!/bin/bash

# Test script to check what the investment report view is returning
# Outputs to a file that we can read back

export DJANGO_SETTINGS_MODULE=tradifyerp.settings
export PYTHONUNBUFFERED=1

cd /var/www/tradifyerp

python3 << 'EOF' > /tmp/context_check_output.txt 2>&1
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tradifyerp.settings")
django.setup()

from shareholder.views import ShareholderInvestmentReportView
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from shareholder.models import SessionEntityMixin
from decimal import Decimal

print("Starting context data check...")

try:
    # Create a fake request
    factory = RequestFactory()
    request = factory.get('/shareholder/investment-report/')

    # Add session
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)

    # Add user
    request.user = User.objects.filter(is_superuser=True).first()

    # Create view and get context  
    view = ShareholderInvestmentReportView()
    view.request = request

    # Manually set entity to Pristine Planet (ID 9)
    request.session['entity_id'] = 9

    context = view.get_context_data()

    print("=" * 60)
    print("CONTEXT DATA INSPECTION")
    print("=" * 60)
    print(f"Investment Data Dict Keys: {len(context.get('investment_data', {}))}")
    print()

    # Find target stakeholders
    for name, inv_data in context.get('investment_data', {}).items():
        if any(target in name for target in ['Rafi', 'Sanaullah', 'Atif', 'Safi']):
            pending = inv_data.get('pending_in_foreign_bank')
            print(f"Stakeholder: {name}")
            print(f"  - pending_in_foreign_bank: {pending}")
            print(f"  - Type: {type(pending).__name__}")
            print(f"  - Repr: {repr(pending)}")
            print(f"  - Bool value: {bool(pending)}")
            if pending:
                print(f"  - pending > 0: {pending > 0}")
            print()

    print("=" * 60)
    total = context.get('total_pending_in_foreign_bank')
    print(f"Total Pending: {total}")
    print(f"Type: {type(total).__name__}")
    print("=" * 60)

except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    print(traceback.format_exc())

EOF

echo "Output written to /tmp/context_check_output.txt"
cat /tmp/context_check_output.txt
