import os
import sys
import django

sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
os.chdir('/var/www/tradifyerp/TradifyERP')
django.setup()

from django.core.management import call_command
call_command('showmigrations', 'accounting')
