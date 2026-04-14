import os
import sys
import django
from django.contrib.sessions.models import Session
from django.utils import timezone
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TradifyERP.settings_production")
sys.path.insert(0, '/var/www/tradifyerp')
django.setup()

# Get the most recent session (typically the logged-in user's session)
sessions = Session.objects.order_by('-expire_date')

if sessions.exists():
    session_obj = sessions.first()
    session_data = session_obj.get_decoded()
    print(f"Current session entity_id: {session_data.get('selected_entity_id')}")
    
    # Set entity to 9 (Pristine Planet)
    session_data['selected_entity_id'] = 9
    session_obj.session_data = session_obj.objects.model(session_json=json.dumps(session_data)).session_data
    session_obj.save()
    print(f"Updated session to entity_id: 9")
else:
    print("No sessions found")
