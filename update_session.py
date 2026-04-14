#!/usr/bin/env python3
import os
import sys
import django
from django.contrib.sessions.models import Session
import json

os.environ['DJANGO_SETTINGS_MODULE'] = 'TradifyERP.settings_production'
sys.path.insert(0, '/var/www/tradifyerp')

# Configure Django BEFORE importing models
django.setup()

# Now we can import and use Session
sessions = Session.objects.order_by('-expire_date')
if sessions.exists():
    session_obj = sessions.first()
    session_data = session_obj.get_decoded()
    print(f"Current entity_id: {session_data.get('selected_entity_id')}")
    
    # Update to Pristine Planet (id=9)
    session_data['selected_entity_id'] = 9
    session_obj.session_data = json.dumps(session_data)
    session_obj.save()
    print(f"Updated entity_id to: 9")
    print(f"Session key: {session_obj.session_key}")
else:
    print("No sessions found")
