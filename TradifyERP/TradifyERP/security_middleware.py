"""
Advanced Security Middleware for Django ERP System
=====================================================
Provides comprehensive security layers including:
- Security headers (CSP, HSTS, X-Frame-Options, etc.)
- Rate limiting per IP
- SQL injection protection
- Audit logging for all requests
"""

import logging
import json
import hashlib
import re
from functools import wraps
from django.core.cache import cache
from django.http import HttpResponse
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.decorators import permission_required as django_permission_required

logger = logging.getLogger('security')
audit_logger = logging.getLogger('audit')


class SecurityHeadersMiddleware:
    """
    Adds comprehensive security headers to all responses.
    Protects against XSS, clickjacking, MIME sniffing, etc.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Prevent clickjacking attacks
        response['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS filtering in older browsers
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "font-src 'self' data: cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response['Content-Security-Policy'] = csp
        
        # HTTP Strict Transport Security
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (formerly Feature Policy)
        response['Permissions-Policy'] = (
            'accelerometer=(), camera=(), geolocation=(), gyroscope=(), '
            'magnetometer=(), microphone=(), payment=(), usb=()'
        )
        
        return response


class RateLimitMiddleware:
    """
    Implements rate limiting per IP address using Django cache.
    Default: 100 requests per 5 minutes per IP.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = getattr(settings, 'RATE_LIMIT_REQUESTS', 100)
        self.rate_limit_period = getattr(settings, 'RATE_LIMIT_PERIOD', 300)  # 5 minutes
    
    def __call__(self, request):
        client_ip = self.get_client_ip(request)
        cache_key = f'rate_limit:{client_ip}'
        
        request_count = cache.get(cache_key, 0)
        
        if request_count >= self.rate_limit:
            logger.warning(f'Rate limit exceeded for IP: {client_ip}')
            return HttpResponse('Rate limit exceeded. Please try again later.', status=429)
        
        cache.set(cache_key, request_count + 1, self.rate_limit_period)
        response = self.get_response(request)
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AuditLoggingMiddleware:
    """
    Logs all POST, PUT, DELETE, PATCH requests for sensitive paths.
    Tracks data changes for compliance and security auditing.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.sensitive_paths = [
            '/admin/',
            '/api/',
            '/accounting/',
            '/cash-management/',
            '/accounts-receivable/',
            '/accounts-payable/',
        ]
    
    def __call__(self, request):
        # Log request if it matches sensitive paths
        if self.is_sensitive_request(request):
            self.log_request(request)
        
        response = self.get_response(request)
        
        return response
    
    def is_sensitive_request(self, request):
        """Check if request modifies data"""
        if request.method not in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return False
        
        for path in self.sensitive_paths:
            if request.path.startswith(path):
                return True
        
        return False
    
    def log_request(self, request):
        """Log the sensitive request"""
        user = request.user.username if request.user.is_authenticated else 'AnonymousUser'
        ip_address = RateLimitMiddleware.get_client_ip(request)
        
        audit_logger.info(
            f'Action: {request.method} | Path: {request.path} | '
            f'User: {user} | IP: {ip_address} | '
            f'Timestamp: {now().isoformat()}'
        )


class SQLInjectionProtectionMiddleware:
    """
    Detects and blocks potential SQL injection attempts.
    Examines request parameters for common SQL injection patterns.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Common SQL injection patterns
        self.sql_patterns = [
            r'(\bunion\b.*\bselect\b)',  # UNION-based
            r'(--|#|\/\*)',              # Comment sequences
            r'(;\s*drop\b)',             # DROP commands
            r'(;\s*delete\b)',           # DELETE commands
            r'(;\s*update\b)',           # UPDATE commands
            r'(xp_|sp_)',                # Extended/stored procedures
        ]
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.sql_patterns]
    
    def __call__(self, request):
        # Check for SQL injection in GET/POST parameters
        if self.has_sql_injection(request):
            client_ip = RateLimitMiddleware.get_client_ip(request)
            logger.critical(
                f'SQL Injection attempt detected from IP: {client_ip} | '
                f'Path: {request.path}'
            )
            return HttpResponse('Invalid request detected.', status=403)
        
        response = self.get_response(request)
        return response
    
    def has_sql_injection(self, request):
        """Check all request parameters for SQL injection"""
        params = dict(request.GET)
        params.update(dict(request.POST))
        
        for key, values in params.items():
            for value in values if isinstance(values, list) else [values]:
                if isinstance(value, str):
                    for pattern in self.compiled_patterns:
                        if pattern.search(value):
                            return True
        
        return False


# Decorators for view-level security

def require_https(view_func):
    """Decorator to enforce HTTPS for a view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.is_secure() and not settings.DEBUG:
            logger.warning(f'Non-HTTPS request to {request.path}')
            return HttpResponse('HTTPS required', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


def require_permission(permission):
    """Decorator to check user has specific permission"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponse('Authentication required', status=401)
            
            if not request.user.has_perm(permission):
                logger.warning(
                    f'Unauthorized access attempt by {request.user.username} '
                    f'to {request.path}'
                )
                return HttpResponse('Permission denied', status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def log_sensitive_access(data_type):
    """Decorator to log access to sensitive data"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                ip_address = RateLimitMiddleware.get_client_ip(request)
                audit_logger.info(
                    f'Sensitive data access: {data_type} | '
                    f'User: {request.user.username} | IP: {ip_address}'
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
