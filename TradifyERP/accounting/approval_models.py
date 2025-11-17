"""
Multi-Signature Approval Workflow models.
Implements SOX 302 officer certification requirements.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import json


class ApprovalWorkflow(models.Model):
    """
    Multi-signature approval process for transactions.
    Implements SOX 302/404 requirements for officer certification.
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft - Not Submitted'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('REVISION_NEEDED', 'Revision Needed'),
        ('CANCELLED', 'Cancelled'),
    ]

    # Transaction references (polymorphic)
    ledger_entry = models.OneToOneField(
        'accounting.LedgerEntry',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='approval_workflow'
    )
    capital_contribution = models.OneToOneField(
        'accounting.CapitalContribution',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='approval_workflow'
    )
    journal_entry = models.OneToOneField(
        'accounting.JournalEntry',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='approval_workflow'
    )

    # Workflow metadata
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='approval_workflows'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )

    # Approval requirements
    requires_approval_from_roles = models.JSONField(
        default=list,
        help_text="List of role names required to approve"
    )

    # Submission
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_workflows'
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_workflows'
    )

    # Rejection/Revision
    rejection_reason = models.TextField(blank=True)
    rejection_date = models.DateTimeField(null=True, blank=True)
    revision_count = models.IntegerField(default=0)

    # Completion
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entity', 'status']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        obj_type = 'Ledger Entry' if self.ledger_entry else 'Capital Contribution'
        return f"Approval {self.id}: {obj_type} - {self.get_status_display()}"

    def submit(self, user):
        """Submit workflow for approval."""
        if self.status != 'DRAFT':
            raise ValueError("Only draft workflows can be submitted")

        self.status = 'PENDING_APPROVAL'
        self.submitted_at = timezone.now()
        self.submitted_by = user
        self.save()

    def approve(self, user, comment=""):
        """
        Record approval from user.
        Auto-transitions to APPROVED if all approvals complete.
        """
        from .role_models import UserRole

        # Verify user has role required for approval
        approval = self.approval_set.filter(
            required_role__in=UserRole.objects.filter(
                user=user,
                is_active=True
            ).values_list('role__name', flat=True),
            is_approved=False
        ).first()

        if not approval:
            raise ValueError("This user has no pending approvals for this workflow")

        approval.is_approved = True
        approval.approved_by = user
        approval.approved_at = timezone.now()
        approval.approval_comment = comment
        approval.save()

        # Check if all approvals complete
        if not self.approval_set.filter(is_approved=False).exists():
            self.status = 'APPROVED'
            self.approved_at = timezone.now()
            self.save()

            # Auto-post to GL if it's a capital contribution
            if self.capital_contribution:
                self.auto_post_contribution()

        self.save()

    def reject(self, user, reason):
        """Reject workflow and require revision."""
        if self.status != 'PENDING_APPROVAL':
            raise ValueError("Only pending workflows can be rejected")

        self.status = 'REJECTED'
        self.rejection_reason = reason
        self.rejection_date = timezone.now()
        self.rejected_at = timezone.now()
        self.save()

        # Reset approvals for revision
        self.approval_set.all().update(
            is_approved=False,
            approved_by=None,
            approved_at=None
        )

    def auto_post_contribution(self):
        """Auto-post approved capital contribution to GL."""
        if not self.capital_contribution:
            return

        from .models import LedgerEntry, AutoJournalEntryRule

        try:
            rule = AutoJournalEntryRule.objects.get(
                entity=self.entity,
                event_type='CAPITAL_CONTRIBUTION_APPROVED'
            )

            cc = self.capital_contribution

            # Create GL entries
            debit = LedgerEntry.objects.create(
                account=rule.debit_account,
                entity=self.entity,
                entry_date=cc.contribution_date,
                entry_type='DEBIT',
                amount=cc.amount_company_currency,
                description=f'Capital contribution: {cc.stakeholder.full_name}',
                reference_number=f'CC-{cc.id}',
                is_posted=True
            )

            credit = LedgerEntry.objects.create(
                account=rule.credit_account,
                entity=self.entity,
                entry_date=cc.contribution_date,
                entry_type='CREDIT',
                amount=cc.amount_company_currency,
                description=f'Capital contribution: {cc.stakeholder.full_name}',
                reference_number=f'CC-{cc.id}',
                is_posted=True
            )

            # Link to contribution
            cc.ledger_entry = debit
            cc.save()

        except AutoJournalEntryRule.DoesNotExist:
            pass  # Rule not configured


class Approval(models.Model):
    """
    Individual approval step in workflow.
    Tracks sequential approval chain.
    """
    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.CASCADE,
        related_name='approval_set'
    )

    # Role requirement
    required_role = models.CharField(max_length=50)  # Role name
    order = models.IntegerField()  # Approval sequence (1, 2, 3...)

    # Approval details
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approvals_given'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_comment = models.TextField(blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        unique_together = ('workflow', 'order')

    def __str__(self):
        status = "✓ Approved" if self.is_approved else "○ Pending"
        return f"Step {self.order}: {self.required_role} {status}"


class ApprovalTemplate(models.Model):
    """
    Pre-defined approval templates for common transaction types.
    Streamlines approval setup.
    """
    TRANSACTION_TYPES = [
        ('CAPITAL_CONTRIBUTION', 'Capital Contribution'),
        ('JOURNAL_ENTRY', 'Journal Entry'),
        ('PERIOD_CLOSE', 'Period Close'),
        ('MANUAL_ADJUSTMENT', 'Manual Adjustment'),
    ]

    name = models.CharField(max_length=100)
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='approval_templates'
    )
    transaction_type = models.CharField(
        max_length=50,
        choices=TRANSACTION_TYPES
    )

    # Approval chain (JSON)
    approval_chain = models.JSONField(
        help_text="List of role names in approval order"
    )

    # Thresholds (optional)
    amount_threshold = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Approval required only if amount exceeds this"
    )

    # Status
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('entity', 'transaction_type', 'name')

    def __str__(self):
        return f"{self.name} ({self.get_transaction_type_display()})"

    def get_approval_chain(self):
        """Get approval chain as list."""
        return json.loads(self.approval_chain) if isinstance(self.approval_chain, str) else self.approval_chain
