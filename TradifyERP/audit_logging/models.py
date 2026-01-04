"""
Audit logging models for TradifyERP
Tracks all sensitive operations and security events
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)


class AuditLog(models.Model):
    """
    Comprehensive audit trail for all sensitive operations
    """
    
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('READ', 'Read'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('FAILED_LOGIN', 'Failed Login'),
        ('PERMISSION_DENIED', 'Permission Denied'),
        ('DATA_EXPORT', 'Data Export'),
        ('DATA_IMPORT', 'Data Import'),
        ('SENSITIVE_ACCESS', 'Sensitive Data Access'),
    ]
    
    # Identification
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Action details
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Change tracking
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    changed_fields = models.JSONField(null=True, blank=True)
    
    # Status
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
        verbose_name_plural = "Audit Logs"
    
    def __str__(self):
        return f"{self.action} {self.model_name} by {self.user} at {self.timestamp}"
    
    @classmethod
    def log_action(cls, user, action, model_name, object_id=None, 
                   old_values=None, new_values=None, ip_address='127.0.0.1',
                   user_agent='', success=True, error_message=''):
        """
        Log an action to audit trail
        """
        try:
            changed_fields = []
            if old_values and new_values:
                all_keys = set(old_values.keys()) | set(new_values.keys())
                changed_fields = [
                    k for k in all_keys 
                    if old_values.get(k) != new_values.get(k)
                ]
            
            cls.objects.create(
                user=user,
                action=action,
                model_name=model_name,
                object_id=object_id,
                old_values=old_values,
                new_values=new_values,
                changed_fields=changed_fields,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                error_message=error_message
            )
            
            logger.info(
                f"AUDIT: Action={action} | Model={model_name} | "
                f"User={user} | ObjectID={object_id} | IP={ip_address}"
            )
        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")


class SecurityEvent(models.Model):
    """
    Track security events (failed logins, unusual access patterns, etc.)
    """
    
    EVENT_TYPES = [
        ('FAILED_LOGIN', 'Failed Login Attempt'),
        ('BRUTE_FORCE', 'Brute Force Detected'),
        ('SUSPICIOUS_ACTIVITY', 'Suspicious Activity'),
        ('UNAUTHORIZED_ACCESS', 'Unauthorized Access Attempt'),
        ('DATA_BREACH_ALERT', 'Potential Data Breach'),
        ('RATE_LIMIT_EXCEEDED', 'Rate Limit Exceeded'),
        ('ENCRYPTION_FAILURE', 'Encryption Failure'),
        ('CONFIG_CHANGE', 'Security Config Change'),
    ]
    
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    severity = models.IntegerField(choices=[
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical')
    ])
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['severity', 'resolved']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} at {self.timestamp}"
    
    @classmethod
    def log_security_event(cls, event_type, description, ip_address, 
                          user=None, severity=2):
        """
        Log a security event
        """
        event = cls.objects.create(
            event_type=event_type,
            description=description,
            ip_address=ip_address,
            user=user,
            severity=severity
        )
        
        logger.warning(
            f"SECURITY_EVENT: Type={event_type} | "
            f"IP={ip_address} | Severity={severity} | {description}"
        )
        
        return event


class DataAccessLog(models.Model):
    """
    Log all access to sensitive data (customer info, financial data)
    """
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_type = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    action = models.CharField(max_length=50)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField()
    reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['data_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.user} accessed {self.data_type}({self.object_id}) via {self.action}"
    
    @classmethod
    def log_access(cls, user, data_type, object_id, action, ip_address, reason=''):
        """Log data access"""
        cls.objects.create(
            user=user,
            data_type=data_type,
            object_id=object_id,
            action=action,
            ip_address=ip_address,
            reason=reason
        )
        
        logger.info(
            f"DATA_ACCESS: User={user} | Type={data_type} | "
            f"ObjectID={object_id} | Action={action}"
        )
