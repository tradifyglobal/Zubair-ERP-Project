#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')
django.setup()

from django.contrib.auth.models import User

# Find and delete user
try:
    user = User.objects.get(username='Zubair25')
    print(f"Found user: {user.username} ({user.email})")
    print(f"Full name: {user.first_name} {user.last_name}")
    
    # Delete the user
    user.delete()
    print(f"\n✓ Successfully deleted user 'Zubair25'")
    
except User.DoesNotExist:
    print("✗ User 'Zubair25' not found")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error deleting user: {str(e)}")
    sys.exit(1)
