#!/var/www/tradifyerp/venv/bin/python
"""
Gunicorn application entry point for TradifyERP production.
Handles proper path setup before Django initialization.
"""
import os
import sys

# Set the project directory
PROJECT_DIR = '/var/www/tradifyerp/TradifyERP'
PARENT_DIR = '/var/www/tradifyerp'

# Add both directories to Python path (correct order per Blueprint)
# STEP 2: sys.path must include both project root and parent
sys.path = [PROJECT_DIR, PARENT_DIR] + [p for p in sys.path if p not in (PROJECT_DIR, PARENT_DIR)]

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

# Change to project directory (STEP 1)
os.chdir(PROJECT_DIR)

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
