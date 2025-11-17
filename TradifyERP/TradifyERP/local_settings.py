from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Local development database: SQLite (safe fallback)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Quick local overrides
DEBUG = True
ALLOWED_HOSTS = ['*']
