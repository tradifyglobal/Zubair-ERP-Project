#!/usr/bin/env python
"""
Script to append new models to accounting/models.py on production server
Run this on the production server to add ShareholderInvestmentRegister models
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TradifyERP.settings')
sys.path.insert(0, '/var/www/tradifyerp')
sys.path.insert(0, '/var/www/tradifyerp/TradifyERP')

django.setup()

# Now check and add models if they don't exist
models_file = '/var/www/tradifyerp/accounting/models.py'

# Read current content
with open(models_file, 'r') as f:
    content = f.read()

# Check if models already exist
if 'class ShareholderInvestmentRegister' in content:
    print("✓ ShareholderInvestmentRegister model already exists")
    sys.exit(0)

print("Adding new models to accounting/models.py...")

# New models code to append
new_models = '''


# ========== SHAREHOLDER INVESTMENT REGISTER MODELS ==========
# Sub-ledger for tracking shareholder contributions
# Auto-populated from CashReceiptLine/BankReceiptLine on authorization

class ShareholderInvestmentRegister(models.Model):
    """
    Sub-ledger tracking all shareholder/stakeholder contributions to the entity.
    
    Provides:
    - Individual shareholder investment history
    - Contribution tracking by type (capital, loan, reinvested dividends)
    - Currency-wise breakdown with exchange rates
    - Status tracking (pending, completed, cancelled)
    
    Auto-populated from CashReceiptLine/BankReceiptLine when status→AUTHORIZED
    """
    
    INVESTMENT_TYPE_CHOICES = [
        ('CAPITAL', 'Capital Contribution'),
        ('LOAN', 'Shareholder Loan'),
        ('DIVIDEND_REINVESTMENT', 'Dividend Reinvestment'),
        ('OTHER', 'Other Investment'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('REVERSED', 'Reversed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Primary Keys
    entity = models.ForeignKey(
        'Entity',
        on_delete=models.CASCADE,
        related_name='shareholder_investments'
    )
    
    stakeholder = models.ForeignKey(
        'Stakeholder',
        on_delete=models.PROTECT,
        related_name='investment_register'
    )
    
    # Investment Details
    investment_date = models.DateField(default=timezone.now, db_index=True)
    investment_type = models.CharField(
        max_length=25,
        choices=INVESTMENT_TYPE_CHOICES,
        default='CAPITAL'
    )
    
    # Amount Details (in company currency)
    amount_company_currency = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Amount in entity's company currency"
    )
    
    # Original Amount (in transaction currency)
    original_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Original amount in transaction currency"
    )
    
    # Currency conversion
    currency = models.ForeignKey(
        'Currency',
        on_delete=models.PROTECT,
        related_name='investments',
        null=True,
        blank=True
    )
    
    exchange_rate = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=1.0,
        help_text="Exchange rate: 1 transaction_currency = X company_currency"
    )
    
    # Source Linkage
    source_cash_receipt = models.ForeignKey(
        'CashReceiptLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='investment_register_entries'
    )
    
    source_bank_receipt = models.ForeignKey(
        'BankReceiptLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='investment_register_entries'
    )
    
    # GL Linkage
    gl_reference = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="GL entry reference (e.g., CASH-RECEIPT-001)"
    )
    
    # Status & Tracking
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shareholder_investments_created'
    )
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    # Notes
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes or comments"
    )
    
    class Meta:
        ordering = ['-investment_date', '-created_date']
        indexes = [
            models.Index(fields=['entity', 'stakeholder', '-investment_date']),
            models.Index(fields=['entity', 'status', '-investment_date']),
            models.Index(fields=['stakeholder', '-investment_date']),
        ]
        verbose_name_plural = 'Shareholder Investment Register'
        
    def __str__(self):
        return f"{self.stakeholder.name} - {self.investment_date} - {self.amount_company_currency}"
    
    def mark_completed(self, user=None):
        """Mark investment as completed after GL posting"""
        self.status = 'COMPLETED'
        if user:
            self.updated_by_user = user
        self.save()
    
    def reverse(self, user=None, reason=''):
        """Reverse an investment (used for adjustments/corrections)"""
        self.status = 'REVERSED'
        if reason:
            self.notes = f"REVERSED: {reason}\\n{self.notes or ''}"
        if user:
            self.updated_by_user = user
        self.save()


class ShareholderInvestmentSummary(models.Model):
    """
    Cached summary view for performance optimization.
    
    Denormalized data from ShareholderInvestmentRegister.
    Updated daily or on-demand for reporting.
    """
    
    entity = models.ForeignKey('Entity', on_delete=models.CASCADE)
    stakeholder = models.ForeignKey('Stakeholder', on_delete=models.CASCADE)
    
    # Summary Statistics
    total_contributions = models.DecimalField(max_digits=18, decimal_places=2)
    contribution_count = models.IntegerField()
    first_contribution_date = models.DateField(null=True, blank=True)
    last_contribution_date = models.DateField(null=True, blank=True)
    average_contribution = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Status Breakdown
    completed_count = models.IntegerField(default=0)
    pending_count = models.IntegerField(default=0)
    cancelled_count = models.IntegerField(default=0)
    
    # Timestamps
    last_calculated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('entity', 'stakeholder')
        verbose_name_plural = 'Shareholder Investment Summaries'
    
    def __str__(self):
        return f"{self.stakeholder.name} - Total: {self.total_contributions}"
    
    @classmethod
    def refresh_for_entity(cls, entity):
        """Refresh all summaries for an entity"""
        from django.db.models import Sum, Count, Min, Max, Avg, Q
        
        stakeholders = Stakeholder.objects.filter(
            investment_register__entity=entity
        ).distinct()
        
        for stakeholder in stakeholders:
            investments = ShareholderInvestmentRegister.objects.filter(
                entity=entity,
                stakeholder=stakeholder
            )
            
            stats = investments.aggregate(
                total=Sum('amount_company_currency'),
                count=Count('id'),
                first_date=Min('investment_date'),
                last_date=Max('investment_date'),
                avg=Avg('amount_company_currency'),
                completed=Count('id', filter=Q(status='COMPLETED')),
                pending=Count('id', filter=Q(status='PENDING')),
                cancelled=Count('id', filter=Q(status='CANCELLED')),
            )
            
            cls.objects.update_or_create(
                entity=entity,
                stakeholder=stakeholder,
                defaults={
                    'total_contributions': stats['total'] or Decimal('0'),
                    'contribution_count': stats['count'] or 0,
                    'first_contribution_date': stats['first_date'],
                    'last_contribution_date': stats['last_date'],
                    'average_contribution': stats['avg'],
                    'completed_count': stats['completed'] or 0,
                    'pending_count': stats['pending'] or 0,
                    'cancelled_count': stats['cancelled'] or 0,
                }
            )
'''

# Append to file
with open(models_file, 'a') as f:
    f.write(new_models)

print(f"✓ New models appended to {models_file}")
print("✓ Ready for migration: python manage.py makemigrations accounting")
