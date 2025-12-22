import os
import sys
import django

sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')
sys.path.insert(0, '/var/www/tradifyerp')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
os.chdir('/var/www/tradifyerp/TradifyERP')

django.setup()

from django.contrib.auth.models import User

# Check if zubair exists
zubair = User.objects.filter(username='zubair').first()
print(f'Zubair user exists: {zubair is not None}')

# List all usernames
all_users = User.objects.values_list('username', flat=True)
print(f'All usernames: {list(all_users)}')

# Check if we can authenticate
if zubair:
    print(f'Zubair details: email={zubair.email}, is_active={zubair.is_active}, is_staff={zubair.is_staff}')
