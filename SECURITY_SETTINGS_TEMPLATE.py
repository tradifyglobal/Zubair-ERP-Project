# Production Security Settings for TradifyERP
# Copy relevant settings to your settings.py

# ========== CRITICAL SECURITY SETTINGS ==========

# 1. NEVER expose SECRET_KEY in code
# Use environment variable instead:
import os
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable must be set")

# 2. DISABLE DEBUG in production
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
if not DEBUG:
    # Production settings
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')
    CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')

# 3. HTTPS/SSL Settings (Production Only)
SECURE_SSL_REDIRECT = not DEBUG  # Redirect HTTP to HTTPS
SESSION_COOKIE_SECURE = not DEBUG  # Only send cookie over HTTPS
CSRF_COOKIE_SECURE = not DEBUG  # Only send CSRF token over HTTPS
SECURE_BROWSER_XSS_FILTER = True  # XSS protection
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'", 'cdnjs.cloudflare.com'),
    'style-src': ("'self'", "'unsafe-inline'"),
    'img-src': ("'self'", 'data:'),
    'frame-ancestors': ("'self'",),
}
X_FRAME_OPTIONS = 'SAMEORIGIN'

# 4. Session Security
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# 5. CSRF Security
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_FAILURE_VIEW = 'security.views.csrf_failure'
CSRF_USE_SESSIONS = True

# 6. Encryption Settings
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')  # From environment
if not ENCRYPTION_KEY and not DEBUG:
    raise ValueError("ENCRYPTION_KEY environment variable must be set in production")

# 7. Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Require 12+ characters
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 8. Database Security
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'ATOMIC_REQUESTS': True,  # Wrap each request in transaction
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'sslmode': 'require',  # Require SSL connection
        } if not DEBUG else {}
    }
}

# 9. Security Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'TradifyERP.security_middleware.SecurityHeadersMiddleware',
    'TradifyERP.security_middleware.RateLimitMiddleware',
    'TradifyERP.security_middleware.AuditLoggingMiddleware',
    'TradifyERP.security_middleware.SQLInjectionProtectionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# 10. Logging Configuration
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
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/tradifyerp/security.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/tradifyerp/audit.log',
            'maxBytes': 1024 * 1024 * 50,  # 50 MB
            'backupCount': 20,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'TradifyERP': {
            'handlers': ['file', 'audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# 11. Cache Configuration (for rate limiting)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# 12. Email Configuration (for security alerts)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# Admin emails for security alerts
ADMINS = [
    ('Security Team', os.environ.get('SECURITY_ADMIN_EMAIL'))
]

# 13. File Upload Security
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
FILE_UPLOAD_PERMISSIONS = 0o644
ALLOWED_FILE_EXTENSIONS = ['pdf', 'xlsx', 'xls', 'csv', 'doc', 'docx', 'jpg', 'jpeg', 'png']

# 14. API Security
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# 15. HTTP Security Headers
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

print("✓ Security settings loaded")
