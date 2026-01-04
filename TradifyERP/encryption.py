"""
Encryption utilities for sensitive data in TradifyERP
Encrypts PII and financial data at rest
"""

from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib
import os
import logging

logger = logging.getLogger(__name__)


class DataEncryption:
    """
    Encrypt and decrypt sensitive data
    Uses Fernet (symmetric encryption)
    """

    def __init__(self):
        # Generate or retrieve encryption key
        self.key = self._get_encryption_key()
        self.cipher = Fernet(self.key)

    @staticmethod
    def _get_encryption_key():
        """
        Get encryption key from environment or settings
        IMPORTANT: Store this in a secure key management system (AWS KMS, HashiCorp Vault, etc.)
        """
        # Try to get from environment first (most secure)
        env_key = os.environ.get('ENCRYPTION_KEY')
        if env_key:
            return env_key.encode()
        
        # Fallback to settings (less secure, for development only)
        settings_key = getattr(settings, 'ENCRYPTION_KEY', None)
        if settings_key:
            return settings_key.encode()
        
        # Generate new key if none exists (development only)
        logger.warning(
            "SECURITY WARNING: No encryption key found. "
            "Generating temporary key. Set ENCRYPTION_KEY environment variable in production."
        )
        return Fernet.generate_key()

    def encrypt(self, data):
        """Encrypt plaintext data"""
        if data is None:
            return None
        
        try:
            # Convert to string if not already
            if not isinstance(data, str):
                data = str(data)
            
            # Encrypt
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise

    def decrypt(self, encrypted_data):
        """Decrypt encrypted data"""
        if encrypted_data is None:
            return None
        
        try:
            # Decrypt
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise


class FieldEncryption:
    """
    Django model field encryption for transparent encryption/decryption
    """

    @staticmethod
    def hash_password(password, salt=None):
        """
        Hash password using PBKDF2 (Django default)
        Use Django's built-in make_password for user passwords
        """
        from django.contrib.auth.hashers import make_password
        return make_password(password)

    @staticmethod
    def hash_pii(data):
        """
        One-way hash for PII (for comparison purposes)
        Cannot be decrypted
        """
        if not data:
            return None
        
        # Use SHA-256 for PII hashing
        return hashlib.sha256(str(data).encode()).hexdigest()

    @staticmethod
    def mask_sensitive_field(value, show_last=4):
        """
        Mask sensitive data for display (e.g., phone, SSN, credit card)
        Shows only last N characters
        """
        if not value:
            return None
        
        value_str = str(value)
        if len(value_str) <= show_last:
            return '*' * len(value_str)
        
        return '*' * (len(value_str) - show_last) + value_str[-show_last:]


class EncryptedField:
    """
    Mixin for Django models to encrypt specific fields
    """
    
    ENCRYPTED_FIELDS = []  # Override in model
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._encryptor = DataEncryption()
    
    def save(self, *args, **kwargs):
        """Encrypt fields before saving"""
        for field_name in self.ENCRYPTED_FIELDS:
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                if value is not None:
                    encrypted_value = self._encryptor.encrypt(value)
                    # Store as f__{field_name} or use a separate encrypted field
                    setattr(self, f'{field_name}_encrypted', encrypted_value)
        
        super().save(*args, **kwargs)
    
    def __getattribute__(self, name):
        """Decrypt fields when accessed"""
        # Get the value
        value = super().__getattribute__(name)
        
        # Check if this is an encrypted field
        encrypted_fields = super().__getattribute__('ENCRYPTED_FIELDS')
        if name in encrypted_fields and value is not None:
            try:
                encryptor = super().__getattribute__('_encryptor')
                return encryptor.decrypt(value)
            except Exception as e:
                logger.error(f"Error decrypting {name}: {str(e)}")
                return value
        
        return value


# Initialize global encryptor
try:
    encryptor = DataEncryption()
except Exception as e:
    logger.error(f"Failed to initialize encryption: {str(e)}")
    encryptor = None
