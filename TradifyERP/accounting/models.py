from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User


class Entity(models.Model):
    """Represents a legal entity or business unit."""
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    company_currency = models.ForeignKey(
        'Currency',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='entities',
        help_text="Default currency for this entity (e.g., INR)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Entities"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class UserEntity(models.Model):
    """Link users to entities they have access to."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entity_assignments')
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='user_assignments')
    is_default = models.BooleanField(default=False, help_text="User's default entity on login")
    can_switch = models.BooleanField(default=True, help_text="User can switch to other assigned entities")
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='entity_assignments_given')

    class Meta:
        unique_together = ('user', 'entity')
        verbose_name_plural = "User Entities"
        ordering = ['-is_default', 'entity__name']

    def __str__(self):
        return f"{self.user.username} - {self.entity.name}"


class Currency(models.Model):
    """Currency definitions."""
    code = models.CharField(max_length=3, unique=True)  # e.g., USD, EUR, GBP
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    exchange_rate = models.DecimalField(max_digits=18, decimal_places=6, default=1.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Currencies"
        ordering = ['code']

    def __str__(self):
        return f"{self.code} ({self.symbol})"


class Account(models.Model):
    """Chart of Accounts."""
    ACCOUNT_TYPES = [
        ('ASSET', 'Asset'),
        ('LIABILITY', 'Liability'),
        ('EQUITY', 'Equity'),
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]

    account_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    description = models.TextField(blank=True, null=True)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='accounts')
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    opening_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    parent_account = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_accounts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['account_number']
        unique_together = ('entity', 'account_number')

    def __str__(self):
        return f"{self.account_number} - {self.name}"
    
    def is_capital_account(self):
        """Check if this is a capital/equity account."""
        return 'capital' in self.name.lower() and self.account_type == 'EQUITY'
    
    def get_shareholder_subaccount(self, stakeholder):
        """Get or create a shareholder sub-account under this capital account."""
        if not self.is_capital_account():
            return None
        
        # Find highest sub-account number
        sub_accounts = self.sub_accounts.filter(account_number__startswith=self.account_number + '-').order_by('-account_number')
        
        if sub_accounts.exists():
            last_number = sub_accounts.first().account_number
            # Extract the sub-number (e.g., "3100-02" -> 02)
            sub_num = int(last_number.split('-')[-1])
            next_sub_num = sub_num + 1
        else:
            next_sub_num = 1
        
        # Generate sub-account code
        new_account_number = f"{self.account_number}-{next_sub_num:02d}"
        
        # Get stakeholder name
        if stakeholder.stakeholder_type == 'INDIVIDUAL':
            shareholder_name = stakeholder.full_name
        else:
            shareholder_name = stakeholder.company_name or str(stakeholder)
        
        # Create or get the sub-account
        sub_account, created = Account.objects.get_or_create(
            entity=self.entity,
            account_number=new_account_number,
            defaults={
                'name': f"{shareholder_name} - Capital",
                'account_type': self.account_type,
                'currency': self.currency,
                'parent_account': self,
                'is_active': True,
                'description': f"Capital account for {shareholder_name}"
            }
        )
        return sub_account


class LedgerEntry(models.Model):
    """General Ledger entries."""
    ENTRY_TYPES = [
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit'),
    ]
    
    WORKFLOW_STATUS = [
        ('DRAFT', 'Draft'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('AUTHORIZED', 'Authorized'),
        ('REJECTED', 'Rejected'),
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='ledger_entries')
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='ledger_entries')
    entry_date = models.DateField()
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPES)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    is_posted = models.BooleanField(default=False)
    workflow_status = models.CharField(max_length=20, choices=WORKFLOW_STATUS, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-entry_date', '-created_at']

    def __str__(self):
        return f"{self.account.account_number} - {self.entry_type} {self.amount} on {self.entry_date}"


class TrialBalance(models.Model):
    """Trial Balance snapshot for a reporting period."""
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='trial_balances')
    as_of_date = models.DateField()
    total_debits = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_credits = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_balanced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('entity', 'as_of_date')
        ordering = ['-as_of_date']

    def __str__(self):
        return f"Trial Balance - {self.entity.code} as of {self.as_of_date}"


class ProfitLossReport(models.Model):
    """P&L Report for a period."""
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='pl_reports')
    period_start = models.DateField()
    period_end = models.DateField()
    total_income = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    net_profit = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('entity', 'period_start', 'period_end')
        ordering = ['-period_end']

    def __str__(self):
        return f"P&L {self.entity.code} ({self.period_start} to {self.period_end})"


class BalanceSheet(models.Model):
    """Balance Sheet snapshot."""
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='balance_sheets')
    as_of_date = models.DateField()
    total_assets = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_liabilities = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_equity = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('entity', 'as_of_date')
        ordering = ['-as_of_date']

    def __str__(self):
        return f"Balance Sheet - {self.entity.code} as of {self.as_of_date}"


class CashFlowForecast(models.Model):
    """Cash Flow Forecast."""
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='cash_flow_forecasts')
    forecast_period = models.CharField(max_length=100)  # e.g., "Q1 2025", "Jan 2025"
    opening_cash = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    inflows = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    outflows = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    closing_cash = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Cash Flow Forecast - {self.entity.code} - {self.forecast_period}"


class CashTransaction(models.Model):
    """Cash in/out transactions."""
    TRANSACTION_TYPES = [
        ('INFLOW', 'Cash Inflow'),
        ('OUTFLOW', 'Cash Outflow'),
    ]

    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='cash_transactions')
    transaction_date = models.DateField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.TextField()
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    is_reconciled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} on {self.transaction_date}"


class BankProfile(models.Model):
    """Bank account profiles."""
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='bank_profiles')
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    account_holder = models.CharField(max_length=255)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['bank_name']

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"


class BankStatement(models.Model):
    """Bank statements."""
    bank_profile = models.ForeignKey(BankProfile, on_delete=models.CASCADE, related_name='statements')
    statement_date = models.DateField()
    opening_balance = models.DecimalField(max_digits=18, decimal_places=2)
    closing_balance = models.DecimalField(max_digits=18, decimal_places=2)
    total_debits = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_credits = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('bank_profile', 'statement_date')
        ordering = ['-statement_date']

    def __str__(self):
        return f"Statement - {self.bank_profile.bank_name} on {self.statement_date}"


class ReconciliationEntry(models.Model):
    """Manual reconciliation entries."""
    bank_statement = models.ForeignKey(BankStatement, on_delete=models.CASCADE, related_name='reconciliation_entries')
    ledger_entry = models.ForeignKey(LedgerEntry, on_delete=models.CASCADE)
    matched_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-matched_date']

    def __str__(self):
        return f"Reconciliation - {self.bank_statement} to {self.ledger_entry}"


class ReconciliationRecord(models.Model):
    """Overall reconciliation records."""
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='reconciliation_records')
    reconciliation_date = models.DateField()
    total_items_reconciled = models.IntegerField(default=0)
    discrepancies_found = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
            ('ERROR', 'Error'),
        ],
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-reconciliation_date']

    def __str__(self):
        return f"Reconciliation {self.entity.code} - {self.reconciliation_date}"


class ReconciliationMatch(models.Model):
    """Individual reconciliation matches between bank and ledger."""
    reconciliation_record = models.ForeignKey(ReconciliationRecord, on_delete=models.CASCADE, related_name='matches')
    bank_entry_amount = models.DecimalField(max_digits=18, decimal_places=2)
    ledger_entry_amount = models.DecimalField(max_digits=18, decimal_places=2)
    variance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    matched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-matched_at']

    def __str__(self):
        return f"Match - Bank: {self.bank_entry_amount} vs Ledger: {self.ledger_entry_amount}"


class TaxRate(models.Model):
    """Tax rate definitions."""
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='tax_rates')
    tax_type = models.CharField(max_length=100)  # e.g., "VAT", "Sales Tax", "Income Tax"
    rate_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    effective_from = models.DateField()
    effective_to = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['tax_type']

    def __str__(self):
        return f"{self.tax_type} - {self.rate_percentage}%"


class TaxTransaction(models.Model):
    """Individual tax transactions."""
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='tax_transactions')
    tax_rate = models.ForeignKey(TaxRate, on_delete=models.PROTECT)
    transaction_date = models.DateField()
    gross_amount = models.DecimalField(max_digits=18, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2)
    net_amount = models.DecimalField(max_digits=18, decimal_places=2)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-transaction_date']

    def __str__(self):
        return f"Tax - {self.tax_rate.tax_type} on {self.transaction_date}"


class TaxSummary(models.Model):
    """Tax summary for a period."""
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='tax_summaries')
    period_start = models.DateField()
    period_end = models.DateField()
    tax_type = models.CharField(max_length=100)
    total_tax = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_taxable = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('entity', 'period_start', 'period_end', 'tax_type')
        ordering = ['-period_end']

    def __str__(self):
        return f"Tax Summary - {self.tax_type} ({self.period_start} to {self.period_end})"


class Customer(models.Model):
    """Customer master data."""
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='customers')
    customer_code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    credit_limit = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ('entity', 'customer_code')

    def __str__(self):
        return f"{self.customer_code} - {self.name}"


class Vendor(models.Model):
    """Vendor/Supplier master data."""
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='vendors')
    vendor_code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ('entity', 'vendor_code')

    def __str__(self):
        return f"{self.vendor_code} - {self.name}"


class VendorInvoice(models.Model):
    """Vendor/Purchase invoices."""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]

    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='vendor_invoices')
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name='invoices')
    invoice_number = models.CharField(max_length=50)
    invoice_date = models.DateField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-invoice_date']
        unique_together = ('entity', 'vendor', 'invoice_number')

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.vendor.name}"
    
    @property
    def paid_amount(self):
        """Calculate total paid amount from related payments."""
        return self.payments.aggregate(total=models.Sum('amount'))['total'] or 0
    
    @property
    def outstanding_amount(self):
        """Calculate outstanding amount."""
        return self.total_amount - self.paid_amount


class VendorPayment(models.Model):
    """Vendor payments."""
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CHECK', 'Check'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CREDIT_CARD', 'Credit Card'),
    ]

    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='vendor_payments')
    vendor_invoice = models.ForeignKey(VendorInvoice, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment {self.reference_number} - {self.amount} on {self.payment_date}"


class FixedAsset(models.Model):
    """Fixed assets register."""
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='fixed_assets')
    asset_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)  # e.g., "Building", "Vehicle", "Equipment"
    purchase_date = models.DateField()
    purchase_cost = models.DecimalField(max_digits=18, decimal_places=2)
    accumulated_depreciation = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    book_value = models.DecimalField(max_digits=18, decimal_places=2)
    useful_life_years = models.IntegerField()
    annual_depreciation = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    # Ledger entry link
    purchase_ledger_entry = models.OneToOneField(LedgerEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name='fixed_asset_purchase')
    # Depreciation tracking
    last_depreciation_date = models.DateField(null=True, blank=True)
    disposal_date = models.DateField(null=True, blank=True)
    disposal_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)  # Disposal/salvage value
    is_disposed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['asset_code']

    def __str__(self):
        return f"{self.asset_code} - {self.name}"
    
    def get_monthly_depreciation(self):
        """Calculate monthly depreciation amount."""
        if self.useful_life_years > 0:
            return self.annual_depreciation / 12
        return Decimal('0')


class DeferredExpense(models.Model):
    """Deferred expenses (prepaid expenses)."""
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='deferred_expenses')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    deferral_date = models.DateField()
    expiry_date = models.DateField()
    expense_type = models.CharField(max_length=100)  # e.g., "Insurance", "Rent"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['expiry_date']

    def __str__(self):
        return f"{self.description} - {self.amount}"


class DeferredRevenue(models.Model):
    """Deferred revenue (unearned revenue)."""
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='deferred_revenues')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    deferral_date = models.DateField()
    recognition_date = models.DateField()
    revenue_type = models.CharField(max_length=100)  # e.g., "Subscription", "Advance Payment"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['recognition_date']

    def __str__(self):
        return f"{self.description} - {self.amount}"


class PeriodLock(models.Model):
    """Period locks to prevent modification of closed periods."""
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='period_locks')
    period_start = models.DateField()
    period_end = models.DateField()
    is_locked = models.BooleanField(default=True)
    locked_by = models.CharField(max_length=255, blank=True, null=True)
    locked_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('entity', 'period_start', 'period_end')
        ordering = ['-period_end']

    def __str__(self):
        status = "Locked" if self.is_locked else "Open"
        return f"Period {self.period_start} to {self.period_end} - {status}"


class AuditLog(models.Model):
    """Audit trail for accounting transactions."""
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('POST', 'Post'),
        ('RECONCILE', 'Reconcile'),
    ]

    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)  # e.g., "LedgerEntry", "VendorInvoice"
    object_id = models.CharField(max_length=100)
    user = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    old_values = models.JSONField(blank=True, null=True)
    new_values = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['entity', '-timestamp']),
            models.Index(fields=['model_name', 'object_id']),
        ]

    def __str__(self):
        return f"{self.action} on {self.model_name} (ID: {self.object_id}) at {self.timestamp}"


# ============ STAKEHOLDER MODELS ============

class Stakeholder(models.Model):
    """Company stakeholders/investors."""
    
    STAKEHOLDER_TYPES = [
        ('INDIVIDUAL', 'Individual'),
        ('CORPORATE', 'Corporate Entity'),
        ('PARTNERSHIP', 'Partnership'),
        ('TRUST', 'Trust'),
        ('FOUNDATION', 'Foundation'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended'),
        ('WITHDRAWN', 'Withdrawn'),
    ]
    
    # Core Identity Information
    entity = models.ForeignKey('accounting.Entity', on_delete=models.CASCADE, related_name='stakeholders')
    stakeholder_type = models.CharField(max_length=20, choices=STAKEHOLDER_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Individual Information
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True, null=True)
    
    # Corporate Information
    company_name = models.CharField(max_length=255, blank=True, null=True)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    company_type = models.CharField(max_length=100, blank=True, null=True)  # e.g., LLC, Corporation, Partnership
    
    # Contact Information
    email = models.EmailField()
    phone_number = models.CharField(max_length=50)
    secondary_phone = models.CharField(max_length=50, blank=True, null=True)
    fax = models.CharField(max_length=50, blank=True, null=True)
    
    # Address Information
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    # Tax & Identification
    tax_identification_number = models.CharField(max_length=50, blank=True, null=True)  # SSN, EIN, VAT ID, etc.
    tax_id_type = models.CharField(max_length=50, blank=True, null=True)  # e.g., SSN, EIN, VAT ID
    
    # Additional Information
    nationality = models.CharField(max_length=100, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    relationship_to_company = models.CharField(max_length=255, blank=True, null=True)  # e.g., "Founder", "Advisor", "Investor"
    notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    joined_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['company_name', 'last_name', 'first_name']
        verbose_name_plural = "Stakeholders"
        unique_together = ('entity', 'email')
    
    def __str__(self):
        if self.stakeholder_type == 'INDIVIDUAL':
            return f"{self.first_name} {self.last_name}"
        else:
            return self.company_name or f"Stakeholder {self.id}"
    
    @property
    def full_name(self):
        """Full name for individuals."""
        if self.stakeholder_type == 'INDIVIDUAL':
            parts = [self.first_name, self.middle_name, self.last_name]
            return ' '.join(p for p in parts if p)
        return self.company_name
    
    @property
    def total_invested(self):
        """Calculate total capital invested by this stakeholder.
        
        Includes:
        - Completed capital contributions (amount_company_currency)
        - Paid shareholder payment commitments (committed_amount)
        """
        total = Decimal('0.00')
        
        # Add completed capital contributions
        completed_contributions = self.capital_contributions.filter(status='COMPLETED')
        for cc in completed_contributions:
            total += Decimal(str(cc.amount_company_currency or 0))
        
        # Add paid payment commitments
        paid_commitments = self.payment_commitments.filter(status='PAID')
        for pc in paid_commitments:
            total += Decimal(str(pc.committed_amount or 0))
        
        return float(total)
    
    @property
    def total_shares(self):
        """Calculate total shares held."""
        return sum(shares.number_of_shares for shares in self.shareholdings.all())
    
    @property
    def ownership_percentage(self):
        """Calculate ownership percentage."""
        total_shares = Shareholding.objects.filter(
            entity=self.entity, 
            is_active=True
        ).aggregate(models.Sum('number_of_shares'))['number_of_shares__sum'] or 0
        
        if total_shares == 0:
            return Decimal('0.00')
        
        my_shares = self.total_shares
        return (Decimal(my_shares) / Decimal(total_shares) * 100).quantize(Decimal('0.01'))


class CapitalContribution(models.Model):
    """Capital contributions/investments made by stakeholders."""
    
    PAYMENT_MODES = [
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CHEQUE', 'Cheque'),
        ('CASH', 'Cash'),
        ('CREDIT_CARD', 'Credit Card'),
        ('WIRE_TRANSFER', 'Wire Transfer'),
        ('CRYPTO', 'Cryptocurrency'),
        ('IN_KIND', 'In-Kind (Assets)'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('RETURNED', 'Returned'),
    ]
    
    WORKFLOW_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('FIRST_REVIEW_COMPLETED', 'First Review Completed'),
        ('REVIEWED', 'Both Reviews Completed'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    # Core Fields
    entity = models.ForeignKey('accounting.Entity', on_delete=models.CASCADE, related_name='capital_contributions')
    stakeholder = models.ForeignKey(Stakeholder, on_delete=models.CASCADE, related_name='capital_contributions')
    contribution_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Workflow Status
    workflow_status = models.CharField(
        max_length=30, 
        choices=WORKFLOW_STATUS_CHOICES, 
        default='DRAFT',
        help_text="Workflow approval status"
    )
    
    # Workflow Users
    submitted_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_capital_contributions',
        help_text="User who submitted the contribution"
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    reviewed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_capital_contributions',
        help_text="First reviewer of the contribution"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, null=True, help_text="Notes from first reviewer")
    
    # Second Reviewer
    reviewed_by_2 = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_capital_contributions_2',
        help_text="Second reviewer of the contribution"
    )
    reviewed_at_2 = models.DateTimeField(null=True, blank=True, help_text="When second reviewer completed review")
    review_notes_2 = models.TextField(blank=True, null=True, help_text="Notes from second reviewer")
    
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_capital_contributions',
        help_text="User who approved the contribution"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True, null=True, help_text="Notes from approver")
    
    rejection_reason = models.TextField(blank=True, null=True, help_text="Reason for rejection")
    
    # Amount Details
    amount = models.DecimalField(max_digits=18, decimal_places=2, help_text="Amount in original currency")
    currency = models.ForeignKey('accounting.Currency', on_delete=models.PROTECT, related_name='capital_contributions')
    
    # Amount Details
    amount = models.DecimalField(max_digits=18, decimal_places=2, help_text="Amount in original currency")
    currency = models.ForeignKey('accounting.Currency', on_delete=models.PROTECT, related_name='capital_contributions')
    
    # Currency Conversion (if different from company currency)
    currency_destination = models.ForeignKey(
        'accounting.Currency', 
        on_delete=models.PROTECT, 
        related_name='capital_contributions_received',
        help_text="Company's primary currency"
    )
    exchange_rate = models.DecimalField(
        max_digits=18, 
        decimal_places=6, 
        default=1.0,
        help_text="Exchange rate from origin to destination currency"
    )
    amount_usd = models.DecimalField(
        max_digits=18, 
        decimal_places=2,
        help_text="Standardized USD amount for comparison",
        editable=False
    )
    amount_company_currency = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Amount converted to company currency",
        editable=False
    )
    
    # Payment Details
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODES)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    payment_bank_account = models.ForeignKey(
        'accounting.BankProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capital_contributions',
        help_text="Bank profile for receiving this contribution"
    )
    payment_method_details = models.TextField(blank=True, null=True)  # Cheque number, wire tracking, etc.
    
    # Bank/Account Details
    paying_bank_name = models.CharField(max_length=255, blank=True, null=True)
    paying_account_number = models.CharField(max_length=100, blank=True, null=True)
    paying_account_holder = models.CharField(max_length=255, blank=True, null=True)
    
    # Accounting Integration
    ledger_entry = models.OneToOneField(
        'accounting.LedgerEntry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capital_contribution'
    )
    equity_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='capital_contributions',
        help_text="Equity account to credit (e.g., Common Stock, Capital Contribution)"
    )
    cash_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_capital',
        help_text="Cash account to debit"
    )
    
    # Documentation
    document_file = models.FileField(upload_to='stakeholder_docs/%Y/%m/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-contribution_date', '-created_at']
        verbose_name_plural = "Capital Contributions"
        unique_together = ('entity', 'reference_number')
    
    def __str__(self):
        return f"{self.stakeholder} - {self.amount} {self.currency.code} ({self.contribution_date})"
    
    def save(self, *args, **kwargs):
        """Auto-calculate amounts and create ledger entry."""
        # Calculate converted amounts
        if self.currency == self.currency_destination:
            self.exchange_rate = 1.0
        
        self.amount_company_currency = self.amount * self.exchange_rate
        
        # Calculate USD equivalent
        # currency_destination.exchange_rate is the rate from that currency to USD
        # So multiply to convert to USD
        try:
            usd_currency = Currency.objects.get(code='USD')
            if self.currency_destination == usd_currency:
                self.amount_usd = self.amount_company_currency
            else:
                # Multiply by the exchange rate to get USD amount
                self.amount_usd = self.amount_company_currency * self.currency_destination.exchange_rate
        except:
            self.amount_usd = self.amount_company_currency
        
        super().save(*args, **kwargs)
        
        # Create ledger entry if status is completed and no entry exists
        if self.status == 'COMPLETED' and not self.ledger_entry:
            self._create_ledger_entry()
    
    def _create_ledger_entry(self):
        """Create accounting entries for capital contribution."""
        from .models import Account, LedgerEntry
        
        try:
            # Find or create equity account
            if not self.equity_account:
                equity_account = Account.objects.filter(
                    entity=self.entity,
                    account_type='EQUITY',
                    name__icontains='capital'
                ).first()
                
                if not equity_account:
                    # Create default equity account
                    equity_account = Account.objects.create(
                        entity=self.entity,
                        account_number='3100',
                        name=f'Capital - {self.stakeholder.full_name}',
                        account_type='EQUITY',
                        currency=self.currency_destination,
                        description=f'Capital contribution from {self.stakeholder.full_name}'
                    )
                self.equity_account = equity_account
            
            # Find or create cash account
            if not self.cash_account:
                cash_account = Account.objects.filter(
                    entity=self.entity,
                    account_type='ASSET',
                    name__icontains='cash'
                ).first()
                
                if not cash_account:
                    # Use first asset account
                    cash_account = Account.objects.filter(
                        entity=self.entity,
                        account_type='ASSET'
                    ).first()
                
                self.cash_account = cash_account
            
            # Create debit entry (Cash)
            debit_entry = LedgerEntry.objects.create(
                account=self.cash_account,
                entity=self.entity,
                entry_date=self.contribution_date,
                entry_type='DEBIT',
                amount=self.amount_company_currency,
                description=f'Capital contribution from {self.stakeholder.full_name} ({self.payment_mode})',
                reference_number=f'CAP-{self.id}',
                is_posted=True
            )
            
            # Create credit entry (Equity)
            LedgerEntry.objects.create(
                account=self.equity_account,
                entity=self.entity,
                entry_date=self.contribution_date,
                entry_type='CREDIT',
                amount=self.amount_company_currency,
                description=f'Capital received from {self.stakeholder.full_name} ({self.payment_mode})',
                reference_number=f'CAP-{self.id}',
                is_posted=True
            )
            
            self.ledger_entry = debit_entry
            self.save(update_fields=['ledger_entry'])
        
        except Exception as e:
            # Log error but don't fail the contribution
            pass
    
    def create_ledger_entry(self):
        """Public method to create ledger entry when approval is completed."""
        if not self.ledger_entry and self.status == 'COMPLETED':
            self._create_ledger_entry()



class Shareholding(models.Model):
    """Share holdings/equity stakes by stakeholders."""
    
    SHARE_TYPES = [
        ('COMMON', 'Common Stock'),
        ('PREFERRED', 'Preferred Stock'),
        ('WARRANT', 'Warrant'),
        ('OPTION', 'Stock Option'),
        ('RESTRICTED', 'Restricted Stock'),
        ('OTHER', 'Other'),
    ]
    
    # Core Fields
    entity = models.ForeignKey('accounting.Entity', on_delete=models.CASCADE, related_name='shareholdings')
    stakeholder = models.ForeignKey(Stakeholder, on_delete=models.CASCADE, related_name='shareholdings')
    share_type = models.CharField(max_length=20, choices=SHARE_TYPES, default='COMMON')
    
    # Share Details
    number_of_shares = models.DecimalField(max_digits=18, decimal_places=2)
    share_class = models.CharField(max_length=50, blank=True, null=True)  # e.g., Class A, Class B
    par_value = models.DecimalField(max_digits=18, decimal_places=4, default=1.0, help_text="Face value per share")
    
    # Share Acquisition
    acquisition_date = models.DateField()
    acquisition_price = models.DecimalField(max_digits=18, decimal_places=2)
    acquisition_currency = models.ForeignKey('accounting.Currency', on_delete=models.PROTECT)
    vesting_schedule = models.CharField(max_length=255, blank=True, null=True)  # e.g., "4 years, 1 year cliff"
    vesting_start_date = models.DateField(blank=True, null=True)
    vesting_end_date = models.DateField(blank=True, null=True)
    
    # Rights & Terms
    voting_rights_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100.0)
    dividend_rights_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100.0)
    is_active = models.BooleanField(default=True)
    
    # Rights Restrictions
    is_transferable = models.BooleanField(default=True)
    is_redeemable = models.BooleanField(default=False)
    redemption_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    
    # Accounting Integration
    stock_ledger_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shareholdings',
        help_text="Stock/Capital account"
    )
    
    # Documentation
    certificate_number = models.CharField(max_length=100, blank=True, null=True)
    certificate_file = models.FileField(upload_to='share_certificates/%Y/%m/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-acquisition_date']
        verbose_name_plural = "Shareholdings"
        unique_together = ('entity', 'stakeholder', 'share_type', 'share_class')
    
    def __str__(self):
        return f"{self.stakeholder} - {self.number_of_shares} {self.share_type} shares"
    
    @property
    def total_value_at_acquisition(self):
        """Total value at time of acquisition."""
        return self.number_of_shares * self.acquisition_price
    
    @property
    def ownership_percentage(self):
        """Percentage ownership of company."""
        total_shares = Shareholding.objects.filter(
            entity=self.entity,
            is_active=True,
            share_type='COMMON'
        ).aggregate(models.Sum('number_of_shares'))['number_of_shares__sum'] or 0
        
        if total_shares == 0:
            return Decimal('0.00')
        
        return (Decimal(self.number_of_shares) / Decimal(total_shares) * 100).quantize(Decimal('0.01'))


# ============ CASH MANAGEMENT MODULE ============

class CashReceiptLine(models.Model):
    """Line items for cash receipts."""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('AUTHORIZED', 'Authorized'),
        ('REJECTED', 'Rejected'),
        ('POSTED', 'Posted'),
    ]
    
    WORKFLOW_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('AUTHORIZED', 'Authorized'),
        ('REJECTED', 'Rejected'),
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='cash_receipt_lines')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='cash_receipt_debit', help_text="Debit account (e.g., 3100-01 Capital)")
    credit_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='cash_receipt_credit', help_text="Credit account (e.g., 100001 Cash)", null=True, blank=True)
    currency = models.ForeignKey('Currency', on_delete=models.PROTECT, null=True, blank=True, help_text="Currency for this transaction")
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=500)
    debit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    workflow_status = models.CharField(max_length=20, choices=WORKFLOW_STATUS_CHOICES, default='DRAFT')
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-id']
        indexes = [
            models.Index(fields=['entity', '-date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Cash Receipt - {self.date} - {self.description[:50]}"


class CashPaymentLine(models.Model):
    """Line items for cash payments."""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('AUTHORIZED', 'Authorized'),
        ('REJECTED', 'Rejected'),
        ('POSTED', 'Posted'),
    ]
    
    WORKFLOW_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('AUTHORIZED', 'Authorized'),
        ('REJECTED', 'Rejected'),
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='cash_payment_lines')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='cash_payment_debit', help_text="Debit account (e.g., shareholder capital)")
    credit_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='cash_payment_credit', help_text="Credit account (e.g., 100001 Cash)", null=True, blank=True)
    currency = models.ForeignKey('Currency', on_delete=models.PROTECT, null=True, blank=True, help_text="Currency for this transaction")
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=500)
    debit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    workflow_status = models.CharField(max_length=20, choices=WORKFLOW_STATUS_CHOICES, default='DRAFT')
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-id']
        indexes = [
            models.Index(fields=['entity', '-date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Cash Payment - {self.date} - {self.description[:50]}"


class BankReceiptLine(models.Model):
    """Line items for bank receipts."""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('AUTHORIZED', 'Authorized'),
        ('REJECTED', 'Rejected'),
        ('POSTED', 'Posted'),
    ]
    
    WORKFLOW_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('AUTHORIZED', 'Authorized'),
        ('REJECTED', 'Rejected'),
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='bank_receipt_lines')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='bank_receipt_debit', help_text="Debit account (e.g., 3100-01 Capital)", null=True, blank=True)
    credit_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='bank_receipt_credit', help_text="Credit account (e.g., 1000 Bank)", null=True, blank=True)
    currency = models.ForeignKey('Currency', on_delete=models.PROTECT, null=True, blank=True, help_text="Currency for this transaction")
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=500)
    debit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    workflow_status = models.CharField(max_length=20, choices=WORKFLOW_STATUS_CHOICES, default='DRAFT')
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-id']
        indexes = [
            models.Index(fields=['entity', '-date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Bank Receipt - {self.date} - {self.debit_amount}"


class BankPaymentLine(models.Model):
    """Line items for bank payments."""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('AUTHORIZED', 'Authorized'),
        ('REJECTED', 'Rejected'),
        ('POSTED', 'Posted'),
    ]
    
    WORKFLOW_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('AUTHORIZED', 'Authorized'),
        ('REJECTED', 'Rejected'),
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='bank_payment_lines')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='bank_payment_debit', help_text="Debit account (e.g., 1000 Bank)", null=True, blank=True)
    credit_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='bank_payment_credit', help_text="Credit account (e.g., 3100-01 Capital)", null=True, blank=True)
    currency = models.ForeignKey('Currency', on_delete=models.PROTECT, null=True, blank=True, help_text="Currency for this transaction")
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=500)
    debit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    workflow_status = models.CharField(max_length=20, choices=WORKFLOW_STATUS_CHOICES, default='DRAFT')
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-id']
        indexes = [
            models.Index(fields=['entity', '-date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Bank Payment - {self.date} - {self.debit_amount}"


class ShareholderInvestmentLimit(models.Model):
    """Investment limits and commitments for shareholders."""
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='shareholder_limits'
    )
    stakeholder = models.OneToOneField(
        Stakeholder,
        on_delete=models.CASCADE,
        related_name='investment_limit'
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        default=1  # Assuming INR is currency_id 1
    )
    
    # Investment Commitment
    target_investment_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=1000000,  # 10 lacs default
        help_text="Target investment amount per shareholder"
    )
    
    # Tracking
    total_invested = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        editable=False,
        help_text="Total amount already invested"
    )
    balance_to_invest = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        editable=False,
        help_text="Remaining amount to meet target"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('entity', 'stakeholder')
        verbose_name_plural = "Shareholder Investment Limits"
    
    def __str__(self):
        return f"{self.stakeholder.full_name} - {self.target_investment_amount} limit"
    
    def update_totals(self):
        """Update total_invested and balance_to_invest from capital contributions."""
        # Sum all completed contributions
        completed_contributions = self.stakeholder.capital_contributions.filter(
            status='COMPLETED',
            entity=self.entity
        ).aggregate(total=models.Sum('amount_company_currency'))['total'] or 0
        
        self.total_invested = completed_contributions
        self.balance_to_invest = self.target_investment_amount - self.total_invested
        self.save()
    
    @property
    def invested_percentage(self):
        """Calculate investment percentage."""
        if self.target_investment_amount == 0:
            return 0
        return (self.total_invested / self.target_investment_amount) * 100


class ShareholderPaymentCommitment(models.Model):
    """Track promised payment dates and commitments from shareholders."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('RESCHEDULED', 'Rescheduled'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='shareholder_commitments'
    )
    stakeholder = models.ForeignKey(
        Stakeholder,
        on_delete=models.CASCADE,
        related_name='payment_commitments'
    )
    
    # Commitment Details
    committed_amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    promised_payment_date = models.DateField(help_text="Date shareholder promised to pay")
    
    # Status Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    actual_payment_date = models.DateField(null=True, blank=True)
    
    # Reference
    notes = models.TextField(blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-promised_payment_date']
        verbose_name_plural = "Shareholder Payment Commitments"
        indexes = [
            models.Index(fields=['stakeholder', 'status']),
            models.Index(fields=['promised_payment_date']),
        ]
    
    def __str__(self):
        return f"{self.stakeholder.full_name} - {self.committed_amount} on {self.promised_payment_date}"
    
    @property
    def is_overdue(self):
        """Check if payment is overdue."""
        if self.status == 'PENDING':
            return timezone.now().date() > self.promised_payment_date
        return False


# Import RBAC models to register them with Django ORM
from .role_models import Role, UserRole, Permission, UserPermissionLog  # noqa: F401
from .module_permissions import ModulePermission, UserModuleAccessLog  # noqa: F401
