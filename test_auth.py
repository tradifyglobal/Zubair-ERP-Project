import os
import sys
import django
from django.contrib.auth import authenticate

sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')
sys.path.insert(0, '/var/www/tradifyerp')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
os.chdir('/var/www/tradifyerp/TradifyERP')

django.setup()

from django.contrib.auth.models import User

# Check Zubair user
try:
    zubair = User.objects.get(username='Zubair')
    print(f'Zubair found!')
    print(f'  Email: {zubair.email}')
    print(f'  Is active: {zubair.is_active}')
    print(f'  Is staff: {zubair.is_staff}')
    print(f'  Is superuser: {zubair.is_superuser}')
    print(f'  Password hash: {zubair.password[:50]}...')
    
    # Try to authenticate
    user = authenticate(username='Zubair', password='Zub@ir0861')
    if user is not None:
        print(f'\n✓ Authentication SUCCESSFUL with Zub@ir0861')
    else:
        print(f'\n✗ Authentication FAILED with Zub@ir0861')
        
        # Try other common passwords
        test_passwords = ['Zubair123', 'test', 'password', '123456', 'Zubair@123']
        print(f'\n  Trying other passwords...')
        for pwd in test_passwords:
            user = authenticate(username='Zubair', password=pwd)
            if user:
                print(f'    ✓ Password found: {pwd}')
                break
        else:
            print(f'    No matching password found')
            
except User.DoesNotExist:
    print('Zubair user not found!')
