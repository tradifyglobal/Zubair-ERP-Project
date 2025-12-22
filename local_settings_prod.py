"""
Production local settings for TradifyERP
Configures PostgreSQL database on remote server
"""

# Production PostgreSQL database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tradifyerp_db',
        'USER': 'tradifyerp_user',
        'PASSWORD': 'Tradify@PostgreSQL2024',
        'HOST': '192.168.20.11',
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
    }
}

# Production settings
DEBUG = True  # Temporarily enabled
ALLOWED_HOSTS = ['tradifyglobal.com', 'www.tradifyglobal.com', '192.168.20.10', '192.168.20.11', 'localhost', '127.0.0.1', '*']
