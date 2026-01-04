"""
Enhanced Security Middleware for TradifyERP
Implements security headers, rate limiting, and data protection
"""

from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.contrib.auth.models import AnonymousUser
import logging
from functools import wraps
from datetime import timedelta

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses
    Prevents common web vulnerabilities
    """

    def process_response(self, request, response):
        # Prevent clickjacking
        response['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Disable client-side caching for sensitive pages
        if request.path.startswith('/accounting/') or request.path.startswith('/admin/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'self'"
        )
        
        # Strict Transport Security (enable in production with HTTPS)
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature Policy
        response['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'payment=()'
        )
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware to prevent brute force attacks
    and API abuse
    """

    def process_request(self, request):
        # Skip rate limiting for static files and media
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None
        
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Rate limit by IP and endpoint
        rate_limit_key = f"rate_limit:{client_ip}:{request.path}"
        attempt_count = cache.get(rate_limit_key, 0)
        
        # Allow 100 requests per 5 minutes per IP
        if attempt_count >= 100:
            logger.warning(f"Rate limit exceeded for {client_ip} on {request.path}")
            return HttpResponse(
                'Too many requests. Please try again later.',
                status=429
            )
        
        # Increment counter
        cache.set(rate_limit_key, attempt_count + 1, 300)  # 5 minutes
        
        return None

    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Log all data access and modifications for audit trail
    """

    def process_request(self, request):
        # Log sensitive operations
        sensitive_paths = [
            '/accounting/',
            '/admin/',
            '/api/',
            '/customer/',
            '/invoice/',
        ]
        
        is_sensitive = any(
            request.path.startswith(path) for path in sensitive_paths
        )
        
        if is_sensitive and request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            user = request.user if request.user.is_authenticated else 'AnonymousUser'
            logger.info(
                f"SENSITIVE_OPERATION: User={user} | "
                f"Method={request.method} | "
                f"Path={request.path} | "
                f"IP={self.get_client_ip(request)}"
            )
        
        return None

    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SQLInjectionProtectionMiddleware(MiddlewareMixin):
    """
    Protect against SQL injection by validating request data
    """

    DANGEROUS_CHARS = ['--', ';', '/*', '*/', 'xp_', 'sp_', ';DROP']

    def process_request(self, request):
        # Check GET and POST parameters
        all_params = {**request.GET.dict(), **request.POST.dict()}
        
        for key, value in all_params.items():
            if isinstance(value, str):
                for dangerous in self.DANGEROUS_CHARS:
                    if dangerous.lower() in value.lower():
                        logger.warning(
                            f"Potential SQL injection attempt detected: "
                            f"Key={key}, User={request.user}"
                        )
                        return HttpResponse(
                            'Invalid request parameters',
                            status=400
                        )
        
        return None


def require_https(view_func):
    """
    Decorator to require HTTPS for sensitive views
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.is_secure() and not request.META.get('DEBUG'):
            return HttpResponse('HTTPS required', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


def require_permission(permission):
    """
    Decorator to require specific permission
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponse('Authentication required', status=401)
            
            if not request.user.has_perm(permission):
                logger.warning(
                    f"Permission denied: User={request.user} | "
                    f"Required={permission}"
                )
                return HttpResponse('Permission denied', status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def log_sensitive_access(data_type):
    """
    Decorator to log access to sensitive data
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            logger.info(
                f"SENSITIVE_DATA_ACCESS: User={request.user} | "
                f"DataType={data_type} | "
                f"Timestamp={__import__('django.utils.timezone', fromlist=['now']).now()}"
            )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
