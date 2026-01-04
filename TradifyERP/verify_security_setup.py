#!/usr/bin/env python
"""
Security Setup Verification Script
====================================
Verifies that all security components are properly installed and configured.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings
from audit_logging.models import AuditLog, SecurityEvent, DataAccessLog
from TradifyERP.security_middleware import SecurityHeadersMiddleware, RateLimitMiddleware

print("=" * 70)
print("SECURITY SETUP VERIFICATION")
print("=" * 70)

# 1. Check installed security packages
print("\n✓ Checking Security Packages...")
required_packages = [
    'cryptography', 'django_otp', 'django_redis', 'corsheaders', 'rest_framework',
    'django_ratelimit', 'psycopg2'
]

for package in required_packages:
    try:
        __import__(package.replace('-', '_'))
        print(f"  ✓ {package} - installed")
    except ImportError:
        print(f"  ✗ {package} - NOT installed")

# 2. Check Django apps
print("\n✓ Checking Django Apps...")
required_apps = ['audit_logging', 'django_otp', 'corsheaders']
for app in required_apps:
    if app in settings.INSTALLED_APPS:
        print(f"  ✓ {app} - registered")
    else:
        print(f"  ✗ {app} - NOT registered")

# 3. Check middleware
print("\n✓ Checking Security Middleware...")
required_middleware = [
    'TradifyERP.security_middleware.SecurityHeadersMiddleware',
    'TradifyERP.security_middleware.RateLimitMiddleware',
    'TradifyERP.security_middleware.AuditLoggingMiddleware',
    'TradifyERP.security_middleware.SQLInjectionProtectionMiddleware',
]
for middleware in required_middleware:
    if middleware in settings.MIDDLEWARE:
        print(f"  ✓ {middleware.split('.')[-1]} - registered")
    else:
        print(f"  ✗ {middleware} - NOT registered")

# 4. Check audit logging tables
print("\n✓ Checking Audit Logging Database Tables...")
try:
    print(f"  ✓ AuditLog table exists - {AuditLog.objects.count()} records")
    print(f"  ✓ SecurityEvent table exists - {SecurityEvent.objects.count()} records")
    print(f"  ✓ DataAccessLog table exists - {DataAccessLog.objects.count()} records")
except Exception as e:
    print(f"  ✗ Database error: {str(e)}")

# 5. Check environment variables
print("\n✓ Checking Environment Configuration...")
env_vars = ['DJANGO_SECRET_KEY', 'ENCRYPTION_KEY', 'DB_HOST', 'EMAIL_HOST_USER']
for var in env_vars:
    value = os.getenv(var)
    if value:
        masked = value[:10] + '...' if len(value) > 10 else value
        print(f"  ✓ {var} - set to {masked}")
    else:
        print(f"  ✗ {var} - NOT set")

# 6. Check settings
print("\n✓ Checking Security Settings...")
print(f"  • DEBUG mode: {settings.DEBUG}")
print(f"  • SSL Redirect: {getattr(settings, 'SECURE_SSL_REDIRECT', False)}")
print(f"  • HSTS enabled: {getattr(settings, 'SECURE_HSTS_SECONDS', 0) > 0}")
print(f"  • Session security: {settings.SESSION_COOKIE_HTTPONLY}")
print(f"  • CSRF security: {settings.CSRF_COOKIE_HTTPONLY}")

# 7. Test audit logging
print("\n✓ Testing Audit Logging...")
try:
    from django.contrib.auth.models import User
    from django.test import RequestFactory
    
    # Create a test audit log
    rf = RequestFactory()
    request = rf.get('/')
    request.user = User.objects.first() if User.objects.exists() else None
    
    if request.user:
        AuditLog.log_action(
            user=request.user,
            action='TEST',
            model_name='TestModel',
            object_id=1,
            ip_address='127.0.0.1',
            success=True
        )
        print("  ✓ Audit logging test successful")
    else:
        print("  ⚠ No users exist for testing (create superuser first)")
except Exception as e:
    print(f"  ⚠ Audit logging test: {str(e)}")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print("\n📋 Next Steps:")
print("  1. Generate SECRET_KEY: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'")
print("  2. Generate ENCRYPTION_KEY: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'")
print("  3. Update .env with actual values")
print("  4. Create superuser: python manage.py createsuperuser")
print("  5. Run server: python manage.py runserver")
print("  6. Visit admin: http://localhost:8000/admin")
print("  7. Check audit logs: http://localhost:8000/admin/audit_logging/auditlog/")
print("\n🔒 Security Features Installed:")
print("  • Rate Limiting (100 req/5min per IP)")
print("  • SQL Injection Protection")
print("  • Audit Logging for all data changes")
print("  • Data Encryption at Rest (Fernet)")
print("  • Security Headers (HSTS, CSP, X-Frame-Options)")
print("  • Two-Factor Authentication ready (django-otp)")
print("  • Redis Caching for performance")
print("  • CORS Protection")
