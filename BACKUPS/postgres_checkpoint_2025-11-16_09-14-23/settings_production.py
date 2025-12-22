# PostgreSQL Production Settings for TradifyERP
# Database Server: 192.168.2.59
# Application Server: 192.168.2.69

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Database Configuration - PostgreSQL on remote server
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tradify',
        'USER': 'zubair',
        'PASSWORD': 'zubair@0862',
        'HOST': '192.168.2.59',  # Remote PostgreSQL server
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
        'AUTOCOMMIT': True,
        'CONNECT_TIMEOUT': 10,
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c default_transaction_isolation=read_committed'
        }
    }
}

# Security Settings
DEBUG = False
ALLOWED_HOSTS = [
    '192.168.2.69',
    'tradifyglobal.com',
    'www.tradifyglobal.com',
    'localhost',
    '127.0.0.1'
]

# SSL/HTTPS (enable after certificate setup)
SECURE_SSL_REDIRECT = False  # Set to True with SSL
SESSION_COOKIE_SECURE = False  # Set to True with SSL
CSRF_COOKIE_SECURE = False  # Set to True with SSL
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = True

# Static and Media Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR.parent, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR.parent, 'media')

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/tradifyerp/django_error.log',
            'formatter': 'verbose',
        },
        'db_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/var/log/tradifyerp/db_connection.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['db_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'tradify-prod-cache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'  # Configure before use
# EMAIL_HOST_PASSWORD = 'your-app-password'  # Configure before use
DEFAULT_FROM_EMAIL = 'noreply@tradifyglobal.com'

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF Configuration
CSRF_COOKIE_AGE = 31449600  # 1 year
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Timezone
TIME_ZONE = 'UTC'
USE_TZ = True

# File Upload Settings
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
FILE_UPLOAD_PERMISSIONS = 0o644

# Middleware for Production
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Security Headers
SECURE_HSTS_SECONDS = 0  # Set to 31536000 after SSL setup
SECURE_HSTS_INCLUDE_SUBDOMAINS = False  # Set to True with HSTS
SECURE_HSTS_PRELOAD = False  # Set to True with HSTS
X_FRAME_OPTIONS = 'DENY'

# Application Insights (if using Azure)
# APPINSIGHTS_INSTRUMENTATION_KEY = 'your-key'

# Performance Optimization
CONN_HEALTH_CHECKS = True
KEEP_ALIVE_TIMEOUT = 5

print("=" * 60)
print("PostgreSQL Production Settings Loaded")
print("Database Host: 192.168.2.59")
print("Database Name: tradify")
print("=" * 60)
