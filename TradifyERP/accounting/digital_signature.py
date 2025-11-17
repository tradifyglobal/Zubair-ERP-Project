"""
Digital Signature and Document Signing models.
Implements SOX 302 officer certification with cryptographic signatures.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64
import hashlib


class DigitalCertificate(models.Model):
    """
    PKI certificate for officers.
    Stores public/private key pairs per SOX 302.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='digital_certificate'
    )

    # Key material (encrypted at rest)
    private_key_pem = models.TextField(
        help_text="Encrypted private key in PEM format"
    )
    public_key_pem = models.TextField(
        help_text="Public key in PEM format"
    )

    # Certificate metadata
    certificate_authority = models.CharField(
        max_length=255,
        default='Internal PKI',
        help_text="Issuing authority name"
    )
    issued_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(
        help_text="Certificate expiration date"
    )

    # Status
    is_active = models.BooleanField(default=True)
    is_revoked = models.BooleanField(default=False)
    revoked_at = models.DateTimeField(null=True, blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Digital Certificates"

    def __str__(self):
        return f"Cert: {self.user.get_full_name()} (expires {self.expires_at.date()})"

    def is_expired(self):
        """Check if certificate is expired."""
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Check if certificate is valid and active."""
        return self.is_active and not self.is_revoked and not self.is_expired()

    @staticmethod
    def generate_keypair():
        """Generate RSA 2048 key pair."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        return private_key

    def sign_data(self, data, password=None):
        """
        Sign data with private key.
        Returns base64-encoded signature.
        """
        from cryptography.hazmat.primitives.serialization import load_pem_private_key

        # Load private key
        private_key = load_pem_private_key(
            self.private_key_pem.encode(),
            password=password.encode() if password else None,
            backend=default_backend()
        )

        # Sign
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return base64.b64encode(signature).decode()

    def verify_signature(self, data, signature_b64):
        """
        Verify signature with public key.
        Returns True if valid, False if invalid.
        """
        from cryptography.hazmat.primitives.serialization import load_pem_public_key

        try:
            # Load public key
            public_key = load_pem_public_key(
                self.public_key_pem.encode(),
                backend=default_backend()
            )

            # Decode signature
            signature = base64.b64decode(signature_b64)

            # Verify
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False


class SignedDocument(models.Model):
    """
    Signed financial documents with audit trail.
    Implements SOX 302 officer certification.
    """
    DOCUMENT_TYPES = [
        ('FINANCIAL_STATEMENT', 'Financial Statement'),
        ('TRIAL_BALANCE', 'Trial Balance'),
        ('JOURNAL_ENTRY', 'Journal Entry'),
        ('PERIOD_CLOSE', 'Period Close'),
        ('APPROVAL_WORKFLOW', 'Approval Workflow'),
        ('RECONCILIATION', 'Reconciliation'),
    ]

    # Document reference
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='signed_documents'
    )
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPES
    )
    document_name = models.CharField(max_length=255)

    # Content hash
    content_hash = models.CharField(
        max_length=64,
        help_text="SHA256 hash of document content"
    )
    content_hash_algorithm = models.CharField(
        max_length=20,
        default='SHA256'
    )

    # Metadata
    document_date = models.DateField()
    period = models.ForeignKey(
        'accounting.AccountingPeriod',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='signed_documents'
    )

    # Status
    is_signed = models.BooleanField(default=False)
    is_finalized = models.BooleanField(default=False)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-document_date']
        unique_together = ('entity', 'document_type', 'document_date')

    def __str__(self):
        return f"{self.get_document_type_display()}: {self.document_name}"

    @staticmethod
    def calculate_hash(content):
        """Calculate SHA256 hash of content."""
        return hashlib.sha256(content.encode() if isinstance(content, str) else content).hexdigest()


class DocumentSignature(models.Model):
    """
    Individual signature on a document.
    Supports multi-signature approval.
    """
    document = models.ForeignKey(
        SignedDocument,
        on_delete=models.CASCADE,
        related_name='signatures'
    )

    # Signer
    signed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='document_signatures'
    )

    # Signature
    signature_data = models.TextField(
        help_text="Base64-encoded signature"
    )
    signature_timestamp = models.DateTimeField(auto_now_add=True)

    # Certificate used
    certificate = models.ForeignKey(
        DigitalCertificate,
        on_delete=models.PROTECT,
        related_name='signatures'
    )

    # Verification
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    # Reason for signing
    signing_reason = models.CharField(
        max_length=500,
        blank=True,
        help_text="e.g., 'Approval as CFO', 'Certification', 'Audit Sign-off'"
    )

    # Audit
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['signature_timestamp']
        unique_together = ('document', 'signed_by')

    def __str__(self):
        return f"Signature by {self.signed_by.get_full_name()} on {self.document.document_name}"

    def verify_signature(self):
        """
        Verify signature against document content hash.
        Returns True if valid.
        """
        if not self.certificate.is_valid():
            return False

        is_valid = self.certificate.verify_signature(
            self.document.content_hash.encode(),
            self.signature_data
        )

        if is_valid:
            self.is_verified = True
            self.verified_at = timezone.now()
            self.save()

        return is_valid


class DocumentAuditTrail(models.Model):
    """
    Immutable audit trail for all document changes.
    Implements SOX 404 change management.
    """
    ACTION_CHOICES = [
        ('CREATED', 'Document Created'),
        ('MODIFIED', 'Content Modified'),
        ('SIGNED', 'Signed'),
        ('VERIFIED', 'Signature Verified'),
        ('APPROVED', 'Approved'),
        ('FINALIZED', 'Finalized'),
        ('REJECTED', 'Rejected'),
    ]

    document = models.ForeignKey(
        SignedDocument,
        on_delete=models.CASCADE,
        related_name='audit_trail'
    )

    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES
    )

    # User who performed action
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='document_audit_actions'
    )

    # Change details
    previous_content_hash = models.CharField(max_length=64, blank=True)
    new_content_hash = models.CharField(max_length=64, blank=True)

    # Context
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Timestamp (immutable)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Document Audit Trails"

    def __str__(self):
        return f"{self.document.document_name}: {self.get_action_display()}"
