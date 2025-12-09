"""
WSGI config for TradifyERP project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Add the Django project directory (parent of this file) to path
# This allows imports like "from TradifyERP.settings import ..."
PROJECT_DIR = str(Path(__file__).resolve().parent.parent)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

os.chdir(PROJECT_DIR)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')

application = get_wsgi_application()
