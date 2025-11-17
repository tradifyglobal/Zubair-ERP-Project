"""
Enhanced Financial Reporting models.
Implements SOX 302/404 reporting requirements:
- Statement of Changes in Equity
- Cash Flow Statement
- Related Party Transaction Reporting
"""

from django.db import models
from django.utils import timezone
from decimal import Decimal


class StatementOfChanges(models.Model):
    """
    Statement of Changes in Equity (Shareholders' Equity).
    Required for comprehensive financial reporting.
    """
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='statements_of_changes'
    )
    period = models.ForeignKey(
        'accounting.AccountingPeriod',
        on_delete=models.CASCADE,
        related_name='statements_of_changes'
    )

    # Equity components
    beginning_common_stock = models.DecimalField(max_digits=18, decimal_places=2)
    beginning_preferred_stock = models.DecimalField(max_digits=18, decimal_places=2)
    beginning_retained_earnings = models.DecimalField(max_digits=18, decimal_places=2)
    beginning_treasury_stock = models.DecimalField(max_digits=18, decimal_places=2)

    # Movements in period
    # Common stock
    common_stock_issued = models.DecimalField(
        max_digits=18, decimal_places=2, default=0,
        help_text="New shares issued"
    )
    common_stock_retired = models.DecimalField(
        max_digits=18, decimal_places=2, default=0,
        help_text="Shares retired or cancelled"
    )

    # Preferred stock
    preferred_stock_issued = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    preferred_stock_retired = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )

    # Earnings activities
    net_income = models.DecimalField(max_digits=18, decimal_places=2)
    dividends_paid = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    other_comprehensive_income = models.DecimalField(
        max_digits=18, decimal_places=2, default=0,
        help_text="Translation adjustments, fair value changes, etc."
    )

    # Treasury stock changes
    treasury_stock_purchased = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    treasury_stock_sold = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )

    # Equity adjustments
    equity_adjustments = models.DecimalField(
        max_digits=18, decimal_places=2, default=0,
        help_text="Revaluation, correction of errors, etc."
    )

    # Status
    is_approved = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    # Audit
    prepared_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prepared_statements_of_changes'
    )
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_statements_of_changes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('entity', 'period')
        ordering = ['-period']

    def __str__(self):
        return f"Statement of Changes: {self.entity.name} - {self.period}"

    @property
    def ending_common_stock(self):
        return (self.beginning_common_stock + 
                self.common_stock_issued - 
                self.common_stock_retired)

    @property
    def ending_preferred_stock(self):
        return (self.beginning_preferred_stock + 
                self.preferred_stock_issued - 
                self.preferred_stock_retired)

    @property
    def ending_retained_earnings(self):
        return (self.beginning_retained_earnings + 
                self.net_income - 
                self.dividends_paid + 
                self.equity_adjustments)

    @property
    def ending_treasury_stock(self):
        return (self.beginning_treasury_stock + 
                self.treasury_stock_purchased - 
                self.treasury_stock_sold)

    @property
    def total_equity_beginning(self):
        return (self.beginning_common_stock + 
                self.beginning_preferred_stock + 
                self.beginning_retained_earnings - 
                self.beginning_treasury_stock)

    @property
    def total_equity_ending(self):
        return (self.ending_common_stock + 
                self.ending_preferred_stock + 
                self.ending_retained_earnings - 
                self.ending_treasury_stock)


class CashFlowStatement(models.Model):
    """
    Statement of Cash Flows (indirect method).
    Required for comprehensive financial reporting.
    """
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='cash_flow_statements'
    )
    period = models.ForeignKey(
        'accounting.AccountingPeriod',
        on_delete=models.CASCADE,
        related_name='cash_flow_statements'
    )

    # Operating activities
    net_income = models.DecimalField(max_digits=18, decimal_places=2)
    depreciation_amortization = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    stock_based_compensation = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )

    # Working capital changes
    accounts_receivable_change = models.DecimalField(
        max_digits=18, decimal_places=2, default=0,
        help_text="Decrease in AR = positive cash flow"
    )
    inventory_change = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    prepaid_expenses_change = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    accounts_payable_change = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    accrued_expenses_change = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )

    # Other operating
    deferred_taxes = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    other_operating_adjustments = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )

    # Investing activities
    capital_expenditures = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    acquisitions = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    investment_purchases = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    investment_sales = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )

    # Financing activities
    debt_proceeds = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    debt_repayments = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    equity_issued = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    treasury_stock_purchased = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    dividends_paid = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )

    # Currency translation
    foreign_exchange_effects = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )

    # Reconciliation
    beginning_cash = models.DecimalField(max_digits=18, decimal_places=2)
    ending_cash = models.DecimalField(max_digits=18, decimal_places=2)

    # Status
    is_approved = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    # Audit
    prepared_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prepared_cash_flows'
    )
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_cash_flows'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('entity', 'period')
        ordering = ['-period']

    def __str__(self):
        return f"Cash Flow Statement: {self.entity.name} - {self.period}"

    @property
    def cash_from_operations(self):
        """Calculate net cash from operating activities."""
        return (self.net_income +
                self.depreciation_amortization +
                self.stock_based_compensation +
                self.accounts_receivable_change +
                self.inventory_change +
                self.prepaid_expenses_change +
                self.accounts_payable_change +
                self.accrued_expenses_change +
                self.deferred_taxes +
                self.other_operating_adjustments)

    @property
    def cash_from_investing(self):
        """Calculate net cash from investing activities."""
        return (-self.capital_expenditures -
                self.acquisitions -
                self.investment_purchases +
                self.investment_sales)

    @property
    def cash_from_financing(self):
        """Calculate net cash from financing activities."""
        return (self.debt_proceeds -
                self.debt_repayments +
                self.equity_issued -
                self.treasury_stock_purchased -
                self.dividends_paid)

    @property
    def net_change_in_cash(self):
        """Calculate total net change in cash."""
        return (self.cash_from_operations +
                self.cash_from_investing +
                self.cash_from_financing +
                self.foreign_exchange_effects)

    def validate_reconciliation(self):
        """Verify cash reconciliation ties out."""
        calculated_ending = self.beginning_cash + self.net_change_in_cash
        return abs(calculated_ending - self.ending_cash) < Decimal('0.01')


class RelatedPartyTransaction(models.Model):
    """
    Log of related party transactions.
    Required for SOX 302/404 and IFRS disclosure compliance.
    """
    TRANSACTION_TYPES = [
        ('SALE', 'Sale of goods/services'),
        ('PURCHASE', 'Purchase of goods/services'),
        ('LOAN', 'Loan or credit facility'),
        ('GUARANTEE', 'Guarantee or indemnity'),
        ('RENT', 'Lease or rental'),
        ('INVESTMENT', 'Investment or capital contribution'),
        ('TRANSFER', 'Asset transfer'),
        ('OTHER', 'Other'),
    ]

    RELATED_PARTY_TYPES = [
        ('DIRECTOR', 'Director/Officer'),
        ('SHAREHOLDER', 'Shareholder (>5%)'),
        ('AFFILIATED_COMPANY', 'Affiliated company'),
        ('FAMILY_MEMBER', 'Family member'),
        ('ENTITY_CONTROLLED', 'Entity controlled by related party'),
        ('OTHER', 'Other'),
    ]

    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='related_party_transactions'
    )

    # Related party
    related_party_name = models.CharField(max_length=255)
    related_party_type = models.CharField(
        max_length=50,
        choices=RELATED_PARTY_TYPES
    )
    related_party_relationship = models.CharField(
        max_length=500,
        help_text="Description of relationship to entity"
    )

    # Transaction details
    transaction_type = models.CharField(
        max_length=50,
        choices=TRANSACTION_TYPES
    )
    transaction_date = models.DateField()
    transaction_amount = models.DecimalField(max_digits=18, decimal_places=2)
    transaction_currency = models.CharField(max_length=3)

    # Business purpose
    business_purpose = models.TextField(
        help_text="Reason for transaction and how terms were determined"
    )

    # Terms
    terms_description = models.TextField(
        help_text="Description of terms (e.g., payment terms, interest rate)"
    )
    comparable_pricing = models.CharField(
        max_length=500,
        blank=True,
        help_text="How pricing compares to independent third parties"
    )

    # Approvals
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_related_party_transactions'
    )
    audit_committee_note = models.TextField(blank=True)

    # Accounting
    gl_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_party_transactions'
    )

    # Disclosure
    requires_disclosure = models.BooleanField(
        default=True,
        help_text="Must be disclosed in financial statements"
    )
    disclosure_reference = models.CharField(
        max_length=50,
        blank=True,
        help_text="Reference in footnotes (e.g., Note 28)"
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['entity', 'transaction_date']),
            models.Index(fields=['related_party_type', 'transaction_type']),
        ]

    def __str__(self):
        return f"{self.related_party_name}: {self.get_transaction_type_display()} ({self.transaction_date})"

    def get_disclosure_text(self):
        """Generate disclosure text for financial statement footnotes."""
        return f"""
During {self.transaction_date.year}, the Company engaged in a {self.get_transaction_type_display().lower()} 
transaction with {self.related_party_name}, a {self.get_related_party_type_display().lower()} of the Company, 
in the amount of {self.transaction_currency} {self.transaction_amount:,.2f}. 

Related Party Relationship: {self.related_party_relationship}

Business Purpose: {self.business_purpose}

Terms: {self.terms_description}

Comparable Pricing: {self.comparable_pricing or 'Market rates'}
        """.strip()
