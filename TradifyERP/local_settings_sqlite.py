# Local Settings for SQLite3 Development/Production
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

# Use SQLite3 for this environment
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Disable any PostgreSQL-specific settings
if 'tradifydb' in str(DATABASES.get('default', {}).get('ENGINE', '')):
    # Remove any old custom backend references
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
