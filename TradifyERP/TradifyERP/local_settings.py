from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Development database: SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Quick local overrides
DEBUG = True
ALLOWED_HOSTS = ['*']
