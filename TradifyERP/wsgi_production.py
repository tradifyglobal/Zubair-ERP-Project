#!/var/www/tradifyerp/venv/bin/python
"""
Gunicorn application entry point for TradifyERP production.
Handles proper path setup before Django initialization.
"""
import os
import sys

# Set the project directory
PROJECT_DIR = '/var/www/tradifyerp/TradifyERP'

# Add project to Python path
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

# Change to project directory
os.chdir(PROJECT_DIR)

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
