"""
TRIAL BALANCE MODELS
Auto-generates after GL posting to verify accuracy and prepare for financial statements
"""

from django.db import models
from django.utils import timezone
from django.db.models import Sum, Q
from decimal import Decimal


class TrialBalance(models.Model):
    """
    Trial Balance header - stores a snapshot of GL balances at a point in time
    Generated after GL posting to verify debits = credits
    """
    
    # Identifiers
    trial_balance_date = models.DateField(
        default=timezone.now,
        help_text="Date as of which trial balance is generated"
    )
    entity = models.ForeignKey(
        'Entity',
        on_delete=models.PROTECT,
        related_name='trial_balances'
    )
    
    # Summary Totals
    total_debit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Sum of all debits"
    )
    total_credit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Sum of all credits"
    )
    
    # Status
    is_balanced = models.BooleanField(
        default=False,
        help_text="True if total_debit = total_credit"
    )
    balance_difference = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Difference between debits and credits (should be 0)"
    )
    
    # Metadata
    generated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        null=True,
        help_text="User who triggered generation (or System)"
    )
    generation_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When trial balance was generated"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('DRAFT', 'Draft'),
            ('GENERATED', 'Generated'),
            ('VERIFIED', 'Verified'),
            ('ERROR', 'Error'),
        ],
        default='DRAFT'
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Any discrepancies or notes about trial balance"
    )
    
    # Audit
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-trial_balance_date']
        verbose_name = 'Trial Balance'
        verbose_name_plural = 'Trial Balances'
        unique_together = [['entity', 'trial_balance_date']]
        indexes = [
            models.Index(fields=['entity', 'trial_balance_date']),
            models.Index(fields=['is_balanced']),
        ]
    
    def __str__(self):
        return f"Trial Balance - {self.entity.name} - {self.trial_balance_date}"
    
    def generate(self):
        """
        Generate trial balance by:
        1. Fetching all GL account balances
        2. Calculating totals
        3. Verifying balance
        """
        from accounting.models import GLAccount
        
        # Get all accounts for entity
        accounts = GLAccount.objects.filter(
            entity=self.entity,
            is_active=True
        )
        
        total_dr = Decimal('0.00')
        total_cr = Decimal('0.00')
        
        # Create line items for each account
        for account in accounts:
            if account.balance > 0:
                if account.account_type in ['ASSET', 'EXPENSE', 'COST_OF_GOODS']:
                    total_dr += account.balance
                else:  # LIABILITY, EQUITY, INCOME
                    total_cr += account.balance
            else:
                if account.account_type in ['ASSET', 'EXPENSE', 'COST_OF_GOODS']:
                    total_cr += abs(account.balance)
                else:
                    total_dr += abs(account.balance)
            
            # Create or update line item
            TrialBalanceLine.objects.update_or_create(
                trial_balance=self,
                account=account,
                defaults={
                    'debit_amount': account.balance if account.balance > 0 else Decimal('0.00'),
                    'credit_amount': abs(account.balance) if account.balance < 0 else Decimal('0.00'),
                }
            )
        
        # Update totals
        self.total_debit = total_dr
        self.total_credit = total_cr
        self.balance_difference = abs(total_dr - total_cr)
        self.is_balanced = (total_dr == total_cr)
        self.status = 'GENERATED' if self.is_balanced else 'ERROR'
        
        if not self.is_balanced:
            self.notes = f"Trial Balance Error: Debit {total_dr} != Credit {total_cr}, Difference: {self.balance_difference}"
        
        self.save()
        
        return self.is_balanced


class TrialBalanceLine(models.Model):
    """
    Trial Balance line item - shows each account's balance
    """
    
    # Relationships
    trial_balance = models.ForeignKey(
        TrialBalance,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    account = models.ForeignKey(
        'accounting.GLAccount',
        on_delete=models.PROTECT
    )
    
    # Amounts
    debit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    credit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Audit
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['account__code']
        verbose_name = 'Trial Balance Line'
        verbose_name_plural = 'Trial Balance Lines'
        unique_together = [['trial_balance', 'account']]
    
    def __str__(self):
        return f"{self.account.code} - Dr: {self.debit_amount}, Cr: {self.credit_amount}"
    
    @property
    def balance(self):
        """Net balance (debit - credit)"""
        return self.debit_amount - self.credit_amount


class TrialBalanceReconciliation(models.Model):
    """
    Tracks trial balance reconciliation issues and resolutions
    """
    
    # Relationships
    trial_balance = models.ForeignKey(
        TrialBalance,
        on_delete=models.CASCADE,
        related_name='reconciliations'
    )
    
    # Issue Details
    issue_type = models.CharField(
        max_length=50,
        choices=[
            ('UNBALANCED', 'Unbalanced Trial Balance'),
            ('MISSING_ENTRY', 'Missing GL Entry'),
            ('INCORRECT_POSTING', 'Incorrect Posting'),
            ('DUPLICATE_ENTRY', 'Duplicate Entry'),
            ('AMOUNT_MISMATCH', 'Amount Mismatch'),
            ('OTHER', 'Other'),
        ]
    )
    
    issue_description = models.TextField()
    affected_account = models.ForeignKey(
        'accounting.GLAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Resolution
    status = models.CharField(
        max_length=20,
        choices=[
            ('OPEN', 'Open'),
            ('IN_PROGRESS', 'In Progress'),
            ('RESOLVED', 'Resolved'),
            ('CLOSED', 'Closed'),
        ],
        default='OPEN'
    )
    
    resolution_description = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trial_balance_resolutions'
    )
    resolved_date = models.DateTimeField(null=True, blank=True)
    
    # Audit
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['status', '-created_date']
        verbose_name = 'Trial Balance Reconciliation'
        verbose_name_plural = 'Trial Balance Reconciliations'
    
    def __str__(self):
        return f"{self.get_issue_type_display()} - {self.status}"


class MonthlyTrialBalance(models.Model):
    """
    Monthly snapshot of trial balance for historical tracking and financial statements
    """
    
    # Identifiers
    month_end_date = models.DateField(
        help_text="Last day of month for this trial balance"
    )
    entity = models.ForeignKey(
        'Entity',
        on_delete=models.PROTECT,
        related_name='monthly_trial_balances'
    )
    
    # Reference Trial Balance
    trial_balance = models.ForeignKey(
        TrialBalance,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Summary
    total_debit = models.DecimalField(max_digits=15, decimal_places=2)
    total_credit = models.DecimalField(max_digits=15, decimal_places=2)
    is_balanced = models.BooleanField(default=True)
    
    # Status
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_monthly_trial_balances'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    
    # Financial Statement Status
    p_and_l_generated = models.BooleanField(default=False)
    balance_sheet_generated = models.BooleanField(default=False)
    
    # Audit
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-month_end_date']
        verbose_name = 'Monthly Trial Balance'
        verbose_name_plural = 'Monthly Trial Balances'
        unique_together = [['entity', 'month_end_date']]
        indexes = [
            models.Index(fields=['entity', 'month_end_date']),
            models.Index(fields=['is_balanced', 'approved']),
        ]
    
    def __str__(self):
        return f"Monthly TB - {self.entity.name} - {self.month_end_date}"
