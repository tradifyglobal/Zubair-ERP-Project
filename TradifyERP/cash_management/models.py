"""
Cash Management Module Models
Complete treasury and cash management including:
- Payment scheduling & forecasting
- Liquidity management
- Cash position tracking
- FX exposure management
- Treasury operations
- Cash pool management

Fully integrated with accounting for GL posting.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from accounting.models import Entity, Account, LedgerEntry, Currency, BankProfile


class CashPosition(models.Model):
    """Current cash position and balance tracking."""
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='cash_positions'
    )
    
    bank_account = models.ForeignKey(
        BankProfile,
        on_delete=models.CASCADE,
        related_name='positions'
    )
    
    # Position Details
    position_date = models.DateField(default=timezone.now, db_index=True)
    opening_balance = models.DecimalField(max_digits=18, decimal_places=2)
    closing_balance = models.DecimalField(max_digits=18, decimal_places=2)
    
    # Reconciliation
    is_reconciled = models.BooleanField(default=False)
    reconciliation_date = models.DateTimeField(null=True, blank=True)
    reconciled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reconciled_cash_positions'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-position_date']
        unique_together = ('entity', 'bank_account', 'position_date')
        indexes = [
            models.Index(fields=['entity', 'position_date']),
            models.Index(fields=['bank_account', 'position_date']),
        ]
    
    def __str__(self):
        return f"Cash Position - {self.bank_account.bank_name} ({self.position_date})"


class PaymentSchedule(models.Model):
    """Payment schedules for AP bills and other obligations."""
    
    PAYMENT_STATUS = [
        ('SCHEDULED', 'Scheduled'),
        ('APPROVED', 'Approved'),
        ('PROCESSED', 'Processed'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
        ('OVERDUE', 'Overdue'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='payment_schedules'
    )
    
    # Reference
    reference_document = models.CharField(max_length=100)  # Bill number, PO, etc.
    reference_type = models.CharField(max_length=50)  # BILL, PO, LOAN, etc.
    
    # Payment Details
    payment_amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    
    # Dates
    scheduled_date = models.DateField(db_index=True)
    due_date = models.DateField()
    actual_payment_date = models.DateField(null=True, blank=True)
    
    # Bank Account
    from_account = models.ForeignKey(
        BankProfile,
        on_delete=models.PROTECT,
        related_name='scheduled_payments'
    )
    to_account_details = models.CharField(max_length=255)  # Payee account info
    
    # Status
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='SCHEDULED')
    
    # GL Integration
    gl_entry = models.OneToOneField(
        LedgerEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_schedule'
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_payment_schedules'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_date']
        indexes = [
            models.Index(fields=['entity', 'scheduled_date']),
            models.Index(fields=['status', 'scheduled_date']),
        ]
    
    def __str__(self):
        return f"Payment - {self.reference_document} - {self.payment_amount} ({self.scheduled_date})"
    
    def is_overdue(self):
        """Check if payment is overdue."""
        if self.status not in ['PAID', 'CANCELLED']:
            return timezone.now().date() > self.due_date
        return False


class LiquidityForecast(models.Model):
    """Liquidity forecasting for cash planning."""
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='liquidity_forecasts'
    )
    
    # Forecast Period
    forecast_start_date = models.DateField()
    forecast_end_date = models.DateField()
    forecast_horizon_days = models.IntegerField()  # e.g., 90 days
    
    # Opening Position
    opening_balance = models.DecimalField(max_digits=18, decimal_places=2)
    
    # Forecasted Inflows
    forecasted_inflows = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    # Forecasted Outflows
    forecasted_outflows = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    # Closing Position
    forecasted_closing_balance = models.DecimalField(max_digits=18, decimal_places=2)
    
    # Minimum Cash Level
    minimum_cash_level = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Minimum cash required for operations"
    )
    
    # Risk Assessment
    surplus_deficit = models.DecimalField(max_digits=18, decimal_places=2)  # Closing - Minimum
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('LOW', 'Low Risk'),
            ('MEDIUM', 'Medium Risk'),
            ('HIGH', 'High Risk'),
        ],
        default='MEDIUM'
    )
    
    # Variance Analysis
    actual_closing_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True
    )
    variance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-forecast_start_date']
        indexes = [
            models.Index(fields=['entity', 'forecast_start_date']),
        ]
    
    def __str__(self):
        return f"Liquidity Forecast - {self.entity.code} ({self.forecast_start_date} to {self.forecast_end_date})"


class LiquidityForecastLine(models.Model):
    """Daily liquidity forecast breakdown."""
    
    forecast = models.ForeignKey(
        LiquidityForecast,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    
    # Day
    forecast_date = models.DateField()
    
    # Cash Flows
    opening_balance = models.DecimalField(max_digits=18, decimal_places=2)
    inflows = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    outflows = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=18, decimal_places=2)
    
    # Variance
    actual_closing_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True
    )
    variance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['forecast_date']
        unique_together = ('forecast', 'forecast_date')
    
    def __str__(self):
        return f"{self.forecast_date} - {self.closing_balance}"


class TreasuryAccount(models.Model):
    """Treasury account for investment/borrowing."""
    
    ACCOUNT_TYPES = [
        ('INVESTMENT', 'Investment Account'),
        ('LOAN', 'Loan Account'),
        ('CREDIT_LINE', 'Credit Line'),
        ('OPERATING', 'Operating Account'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='treasury_accounts'
    )
    
    # Account Details
    account_code = models.CharField(max_length=50, unique=True)
    account_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    
    # Financial Details
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    opening_balance = models.DecimalField(max_digits=18, decimal_places=2)
    current_balance = models.DecimalField(max_digits=18, decimal_places=2)
    
    # Terms (for loans/credit lines)
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Annual interest rate percentage"
    )
    maturity_date = models.DateField(null=True, blank=True)
    credit_limit = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # GL Integration
    gl_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='treasury_accounts'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['account_code']
        unique_together = ('entity', 'account_code')
    
    def __str__(self):
        return f"{self.account_name} ({self.account_code})"


class CashFlowForecastDetail(models.Model):
    """Detailed cash flow forecast by category."""
    
    CASH_FLOW_CATEGORIES = [
        ('OPERATING_INFLOW', 'Operating Inflows'),
        ('OPERATING_OUTFLOW', 'Operating Outflows'),
        ('INVESTING_INFLOW', 'Investing Inflows'),
        ('INVESTING_OUTFLOW', 'Investing Outflows'),
        ('FINANCING_INFLOW', 'Financing Inflows'),
        ('FINANCING_OUTFLOW', 'Financing Outflows'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='cash_flow_details'
    )
    
    # Period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Category
    category = models.CharField(max_length=30, choices=CASH_FLOW_CATEGORIES)
    description = models.CharField(max_length=255)
    
    # Amounts
    forecasted_amount = models.DecimalField(max_digits=18, decimal_places=2)
    actual_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True
    )
    variance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['period_start', 'category']
        indexes = [
            models.Index(fields=['entity', 'period_start']),
        ]
    
    def __str__(self):
        return f"{self.description} - {self.period_start}"


class FXExposure(models.Model):
    """Foreign exchange exposure tracking."""
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='fx_exposures'
    )
    
    # Currencies
    home_currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='fx_exposures_home'
    )
    foreign_currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='fx_exposures_foreign'
    )
    
    # Exposure Details
    exposure_type = models.CharField(
        max_length=20,
        choices=[
            ('RECEIVABLE', 'AR Receivable'),
            ('PAYABLE', 'AP Payable'),
            ('INVESTMENT', 'Investment'),
            ('CASH', 'Cash Balance'),
        ]
    )
    
    # Amount
    foreign_amount = models.DecimalField(max_digits=18, decimal_places=2)
    exchange_rate = models.DecimalField(max_digits=18, decimal_places=6)
    home_currency_amount = models.DecimalField(max_digits=18, decimal_places=2)
    
    # Dates
    exposure_date = models.DateField()
    maturity_date = models.DateField(null=True, blank=True)
    
    # Hedging
    is_hedged = models.BooleanField(default=False)
    hedge_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        help_text="Amount covered by hedging"
    )
    hedge_rate = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        null=True,
        blank=True
    )
    
    # Reference
    reference_number = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-exposure_date']
        indexes = [
            models.Index(fields=['entity', 'exposure_date']),
        ]
    
    def __str__(self):
        return f"FX Exposure - {self.foreign_currency.code} to {self.home_currency.code}"


class CashManagementSettings(models.Model):
    """Cash management configuration per entity."""
    
    entity = models.OneToOneField(
        Entity,
        on_delete=models.CASCADE,
        related_name='cash_management_settings'
    )
    
    # Minimum Cash Levels
    minimum_operating_cash = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        help_text="Minimum cash for daily operations"
    )
    
    # Payment Policies
    default_payment_terms_days = models.IntegerField(default=30)
    auto_schedule_payments = models.BooleanField(default=True)
    payment_approval_required = models.BooleanField(default=True)
    
    # Forecast Settings
    forecast_horizon_days = models.IntegerField(default=90)
    auto_update_forecast = models.BooleanField(default=True)
    
    # FX Settings
    fx_rate_source = models.CharField(max_length=100, blank=True)  # e.g., ECB, Fed
    auto_hedge_exposure = models.BooleanField(default=False)
    hedge_trigger_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50,
        help_text="Percentage of exposure to auto-hedge"
    )
    
    # GL Integration
    cash_clearing_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cash_clearing'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cash Management Settings - {self.entity.code}"
