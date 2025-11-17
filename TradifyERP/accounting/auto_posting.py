"""
Auto Journal Entry Rules and Signal handlers for Phase 3.
Implements automatic GL posting for approved transactions per SOX 302.
"""

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
import json


class AutoJournalEntryRule(models.Model):
    """
    Rules for automatically generating GL entries.
    Ensures consistent accounting treatment per SOX 302.
    """
    EVENT_TYPES = [
        ('CAPITAL_CONTRIBUTION_APPROVED', 'Capital Contribution Approved'),
        ('CAPITAL_CONTRIBUTION_RETURNED', 'Capital Contribution Returned'),
        ('SHARE_ISSUANCE', 'Share Issuance'),
        ('SHARE_SPLIT', 'Share Split'),
        ('SHARE_CONSOLIDATION', 'Share Consolidation'),
        ('DIVIDEND_APPROVED', 'Dividend Approved'),
        ('DIVIDEND_PAID', 'Dividend Paid'),
        ('PERIOD_CLOSE', 'Period Close'),
    ]

    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='auto_journal_rules'
    )
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPES
    )

    # GL accounts
    debit_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.PROTECT,
        related_name='auto_rules_debit'
    )
    credit_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.PROTECT,
        related_name='auto_rules_credit'
    )

    # GL details
    description_template = models.CharField(
        max_length=500,
        help_text="Can use {transaction_id}, {stakeholder_name}, {amount} placeholders"
    )

    # Amount mapping (if needed)
    amount_field = models.CharField(
        max_length=100,
        default='amount_company_currency',
        help_text="Field name to use for GL amount"
    )

    # Control flags
    is_active = models.BooleanField(default=True)
    requires_approval = models.BooleanField(
        default=True,
        help_text="Only post after approval workflow complete"
    )
    auto_post = models.BooleanField(
        default=True,
        help_text="Automatically post without manual confirmation"
    )

    # Currency conversion
    use_transaction_currency = models.BooleanField(
        default=False,
        help_text="Use transaction's original currency instead of company currency"
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_auto_rules'
    )

    class Meta:
        unique_together = ('entity', 'event_type')
        ordering = ['event_type']

    def __str__(self):
        return f"{self.entity.name} - {self.get_event_type_display()}"

    def get_description(self, transaction_obj):
        """Render description template with transaction data."""
        placeholders = {
            'transaction_id': getattr(transaction_obj, 'id', ''),
            'stakeholder_name': getattr(getattr(transaction_obj, 'stakeholder', None), 'full_name', ''),
            'amount': getattr(transaction_obj, self.amount_field, ''),
        }
        return self.description_template.format(**placeholders)


class JournalEntryPostingQueue(models.Model):
    """
    Queue for GL postings pending approval or batch processing.
    Implements SOX 404 segregation of duties.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Posting'),
        ('POSTED', 'Posted'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]

    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='posting_queue'
    )

    # Source transaction
    rule = models.ForeignKey(
        AutoJournalEntryRule,
        on_delete=models.CASCADE,
        related_name='posting_queue'
    )
    source_object_id = models.IntegerField()
    source_object_type = models.CharField(max_length=50)  # 'CapitalContribution', 'Dividend', etc

    # Debit/Credit entries
    debit_amount = models.DecimalField(max_digits=18, decimal_places=2)
    credit_amount = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.CharField(max_length=500)

    # Posting details
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    posted_at = models.DateTimeField(null=True, blank=True)
    posted_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posted_entries'
    )

    # Error tracking
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['entity', 'status']),
            models.Index(fields=['source_object_type', 'source_object_id']),
        ]

    def __str__(self):
        return f"Queue {self.id}: {self.source_object_type} → {self.status}"

    def post(self, user):
        """Post queued entries to GL."""
        from .models import LedgerEntry

        try:
            # Create debit entry
            debit = LedgerEntry.objects.create(
                account=self.rule.debit_account,
                entity=self.entity,
                entry_date=timezone.now().date(),
                entry_type='DEBIT',
                amount=self.debit_amount,
                description=self.description,
                reference_number=f"{self.source_object_type}-{self.source_object_id}",
                is_posted=True,
                posted_by=user
            )

            # Create credit entry
            credit = LedgerEntry.objects.create(
                account=self.rule.credit_account,
                entity=self.entity,
                entry_date=timezone.now().date(),
                entry_type='CREDIT',
                amount=self.credit_amount,
                description=self.description,
                reference_number=f"{self.source_object_type}-{self.source_object_id}",
                is_posted=True,
                posted_by=user
            )

            # Update queue status
            self.status = 'POSTED'
            self.posted_at = timezone.now()
            self.posted_by = user
            self.save()

            return (debit, credit)

        except Exception as e:
            self.error_message = str(e)
            self.retry_count += 1
            self.status = 'FAILED' if self.retry_count >= self.max_retries else 'PENDING'
            self.save()
            raise


# Signal handlers for auto-posting

@receiver(post_save, sender='accounting.CapitalContribution')
def auto_queue_capital_contribution(sender, instance, created, **kwargs):
    """
    When capital contribution is approved, queue GL posting.
    Only processes if linked approval workflow exists and is approved.
    """
    if not created:
        return  # Only for new contributions

    # Check if approval workflow exists
    try:
        workflow = instance.approval_workflow
        if workflow.status != 'APPROVED':
            return  # Not approved yet
    except:
        return  # No approval workflow

    # Find auto-posting rule
    try:
        rule = AutoJournalEntryRule.objects.get(
            entity=instance.entity,
            event_type='CAPITAL_CONTRIBUTION_APPROVED'
        )
    except AutoJournalEntryRule.DoesNotExist:
        return  # No rule configured

    if not rule.is_active:
        return

    # Check if already queued
    if JournalEntryPostingQueue.objects.filter(
        entity=instance.entity,
        source_object_type='CapitalContribution',
        source_object_id=instance.id
    ).exists():
        return

    # Queue entry
    JournalEntryPostingQueue.objects.create(
        entity=instance.entity,
        rule=rule,
        source_object_type='CapitalContribution',
        source_object_id=instance.id,
        debit_amount=instance.amount_company_currency,
        credit_amount=instance.amount_company_currency,
        description=rule.get_description(instance)
    )


@receiver(post_save, sender='accounting.Shareholding')
def auto_post_share_issuance(sender, instance, created, **kwargs):
    """
    When new shareholding is created, auto-queue GL entry if configured.
    """
    if not created:
        return

    try:
        rule = AutoJournalEntryRule.objects.get(
            entity=instance.entity,
            event_type='SHARE_ISSUANCE'
        )
    except AutoJournalEntryRule.DoesNotExist:
        return

    if not rule.is_active:
        return

    # Don't queue if already processed
    if JournalEntryPostingQueue.objects.filter(
        entity=instance.entity,
        source_object_type='Shareholding',
        source_object_id=instance.id
    ).exists():
        return

    # Queue entry
    JournalEntryPostingQueue.objects.create(
        entity=instance.entity,
        rule=rule,
        source_object_type='Shareholding',
        source_object_id=instance.id,
        debit_amount=instance.share_value or 0,
        credit_amount=instance.share_value or 0,
        description=f"Share issuance: {instance.stakeholder.full_name} - {instance.shares} shares"
    )
