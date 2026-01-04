"""
Data Encryption Module for ERP System
=====================================
Provides transparent encryption/decryption for sensitive data fields.
Uses Fernet (symmetric) encryption from cryptography library.
"""

import os
import logging
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
import hashlib

logger = logging.getLogger('security')


class DataEncryption:
    """
    Handles encryption and decryption of sensitive data.
    Uses Fernet for symmetric encryption.
    """
    
    def __init__(self):
        # Get encryption key from environment or settings
        key = os.getenv('ENCRYPTION_KEY') or getattr(settings, 'ENCRYPTION_KEY', None)
        
        if not key:
            logger.warning(
                'ENCRYPTION_KEY not configured. Set ENCRYPTION_KEY environment '
                'variable or add to settings.py'
            )
            # Generate a temporary key for development (NEVER use in production)
            if settings.DEBUG:
                key = Fernet.generate_key()
                logger.info('Generated temporary encryption key for development')
        
        try:
            if isinstance(key, str):
                key = key.encode()
            self.cipher = Fernet(key)
            self.key = key
        except Exception as e:
            logger.error(f'Failed to initialize encryption: {str(e)}')
            self.cipher = None
            self.key = None
    
    def encrypt(self, plaintext):
        """Encrypt plaintext to ciphertext"""
        if not self.cipher:
            logger.error('Encryption not available')
            return plaintext
        
        try:
            if isinstance(plaintext, str):
                plaintext = plaintext.encode()
            ciphertext = self.cipher.encrypt(plaintext)
            return ciphertext.decode()
        except Exception as e:
            logger.error(f'Encryption failed: {str(e)}')
            return plaintext
    
    def decrypt(self, ciphertext):
        """Decrypt ciphertext to plaintext"""
        if not self.cipher:
            logger.error('Decryption not available')
            return ciphertext
        
        try:
            if isinstance(ciphertext, str):
                ciphertext = ciphertext.encode()
            plaintext = self.cipher.decrypt(ciphertext)
            return plaintext.decode()
        except InvalidToken:
            logger.warning('Invalid encryption token - data may be corrupted')
            return ciphertext
        except Exception as e:
            logger.error(f'Decryption failed: {str(e)}')
            return ciphertext


class FieldEncryption:
    """
    Utilities for field-level encryption and masking
    """
    
    @staticmethod
    def hash_pii(value):
        """
        One-way hash for PII using SHA-256.
        Use for non-reversible PII storage.
        """
        if not value:
            return None
        
        if isinstance(value, str):
            value = value.encode()
        
        return hashlib.sha256(value).hexdigest()
    
    @staticmethod
    def mask_sensitive_field(value, show_chars=4):
        """
        Mask sensitive fields for display.
        E.g., "1234567890" -> "***7890"
        """
        if not value:
            return value
        
        value_str = str(value)
        
        if len(value_str) <= show_chars:
            return value_str
        
        mask_length = len(value_str) - show_chars
        return '*' * mask_length + value_str[-show_chars:]
    
    @staticmethod
    def encrypt_field(value):
        """Encrypt a field value"""
        encryptor = DataEncryption()
        return encryptor.encrypt(value)
    
    @staticmethod
    def decrypt_field(value):
        """Decrypt a field value"""
        encryptor = DataEncryption()
        return encryptor.decrypt(value)


class EncryptedField:
    """
    Mixin class for Django model fields that need encryption.
    
    Usage:
        class MyModel(models.Model):
            sensitive_data = models.CharField(max_length=255)
            
            def save(self, *args, **kwargs):
                self.sensitive_data = FieldEncryption.encrypt_field(self.sensitive_data)
                super().save(*args, **kwargs)
            
            def __getattribute__(self, name):
                value = super().__getattribute__(name)
                if name == 'sensitive_data' and isinstance(value, str):
                    return FieldEncryption.decrypt_field(value)
                return value
    """
    
    @property
    def encrypted_value(self):
        """Get encrypted value of field"""
        return self._encrypted
    
    @encrypted_value.setter
    def encrypted_value(self, value):
        """Set and encrypt value"""
        encryptor = DataEncryption()
        self._encrypted = encryptor.encrypt(value)
    
    def decrypt_value(self):
        """Decrypt the field value"""
        encryptor = DataEncryption()
        return encryptor.decrypt(self._encrypted)


# Global encryptor instance
encryptor = DataEncryption()


def encrypt_dict(data_dict):
    """
    Encrypt all values in a dictionary
    Returns a new dictionary with encrypted values
    """
    encrypted = {}
    for key, value in data_dict.items():
        if isinstance(value, str):
            encrypted[key] = encryptor.encrypt(value)
        else:
            encrypted[key] = value
    return encrypted


def decrypt_dict(data_dict):
    """
    Decrypt all encrypted values in a dictionary
    Returns a new dictionary with decrypted values
    """
    decrypted = {}
    for key, value in data_dict.items():
        if isinstance(value, str) and value.startswith('gAAAAAB'):  # Fernet prefix
            try:
                decrypted[key] = encryptor.decrypt(value)
            except:
                decrypted[key] = value
        else:
            decrypted[key] = value
    return decrypted
