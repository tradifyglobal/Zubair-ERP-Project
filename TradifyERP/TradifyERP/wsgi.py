"""
WSGI config for TradifyERP project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

# Add the project root to the path so Django can find settings
# Use absolute path for production deployment
PROJECT_ROOT = '/var/www/tradifyerp/TradifyERP'
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.chdir(PROJECT_ROOT)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

application = get_wsgi_application()
