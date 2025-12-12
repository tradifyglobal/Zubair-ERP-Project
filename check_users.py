import os
import sys
import django

sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')
sys.path.insert(0, '/var/www/tradifyerp')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
os.chdir('/var/www/tradifyerp/TradifyERP')

django.setup()

from django.contrib.auth.models import User

print(f'Total users: {User.objects.count()}')
if User.objects.exists():
    for user in User.objects.all()[:10]:
        print(f'  - {user.username} ({user.email})')
else:
    print('  No users found in database!')
