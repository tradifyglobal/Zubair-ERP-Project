import os
import sys
import django

sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')
sys.path.insert(0, '/var/www/tradifyerp')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
os.chdir('/var/www/tradifyerp/TradifyERP')

django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# Get the Zubair user
try:
    zubair = User.objects.get(username='Zubair')
    
    # Set new password
    new_password = 'Zub@ir0861'
    zubair.set_password(new_password)
    zubair.save()
    
    print(f'✓ Password reset for Zubair to: {new_password}')
    
    # Verify it works
    user = authenticate(username='Zubair', password=new_password)
    if user:
        print(f'✓ Authentication test PASSED')
    else:
        print(f'✗ Authentication test FAILED')
        
except User.DoesNotExist:
    print('Zubair user not found!')
