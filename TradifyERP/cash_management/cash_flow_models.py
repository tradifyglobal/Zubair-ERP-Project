"""Cash Flow Statement Models - categorizes and reports cash movements"""

from django.db import models
from decimal import Decimal
from datetime import date
from accounting.models import Entity, LedgerEntry, Account, Currency


class CashFlowCategory(models.Model):
    """Categories for cash flow classification"""
    
    ACTIVITY_TYPES = (
        ('OPERATING', 'Operating Activities'),
        ('INVESTING', 'Investing Activities'),
        ('FINANCING', 'Financing Activities'),
    )
    
    name = models.CharField(max_length=100)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True)
    account_patterns = models.TextField(help_text="Comma-separated account number patterns (e.g., '100,101')")
    is_inflow = models.BooleanField(default=True, help_text="Is this an inflow (True) or outflow (False)?")
    
    class Meta:
        ordering = ['activity_type', 'name']
        unique_together = ('name', 'activity_type')
    
    def __str__(self):
        return f"{self.name} ({self.get_activity_type_display()})"


class CashFlowStatement(models.Model):
    """Monthly/Period Cash Flow Statement"""
    
    PERIOD_CHOICES = (
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('ANNUAL', 'Annual'),
    )
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='cash_flow_statements')
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='MONTHLY')
    start_date = models.DateField()
    end_date = models.DateField()
    
    opening_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    # Operating Activities
    operating_inflows = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    operating_outflows = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    net_operating_cash_flow = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    # Investing Activities
    investing_inflows = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    investing_outflows = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    net_investing_cash_flow = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    # Financing Activities
    financing_inflows = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    financing_outflows = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    net_financing_cash_flow = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    # Summary
    total_net_cash_flow = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    # Bank reconciliation
    bank_closing_balance = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    reconciliation_difference = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_reconciled = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    generated_by = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-start_date']
        unique_together = ('entity', 'period_type', 'start_date', 'end_date')
    
    def __str__(self):
        return f"{self.entity.name} - {self.period_type} ({self.start_date} to {self.end_date})"
    
    @property
    def is_balanced(self):
        """Check if statement balances: Opening + Net Flow = Closing"""
        expected_closing = self.opening_balance + self.total_net_cash_flow
        return abs(expected_closing - self.closing_balance) < Decimal('0.01')


class CashFlowLineItem(models.Model):
    """Detailed line item in cash flow statement"""
    
    cash_flow_statement = models.ForeignKey(CashFlowStatement, on_delete=models.CASCADE, related_name='line_items')
    category = models.ForeignKey(CashFlowCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    line_number = models.IntegerField()
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    is_inflow = models.BooleanField(default=True)
    
    # Source references
    source_type = models.CharField(max_length=50, blank=True, help_text="'INVOICE', 'BILL', 'PAYMENT', 'TRANSFER', etc.")
    source_id = models.IntegerField(null=True, blank=True)
    
    # Detail tracking
    quantity_transactions = models.IntegerField(default=1, help_text="Number of transactions aggregated")
    detail_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['cash_flow_statement', 'line_number']
    
    def __str__(self):
        return f"{self.description}: {self.amount}"


class CashFlowForecastDetail(models.Model):
    """Forecasted cash flows by category"""
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    category = models.ForeignKey(CashFlowCategory, on_delete=models.CASCADE)
    
    forecast_date = models.DateField()
    forecasted_inflow = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    forecasted_outflow = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    source_documents = models.TextField(help_text="Comma-separated list of source invoice/bill IDs")
    confidence_level = models.CharField(
        max_length=20,
        choices=[('HIGH', 'High'), ('MEDIUM', 'Medium'), ('LOW', 'Low')],
        default='MEDIUM'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['forecast_date']
        unique_together = ('entity', 'category', 'forecast_date')
    
    def __str__(self):
        net = self.forecasted_inflow - self.forecasted_outflow
        return f"{self.category.name} on {self.forecast_date}: {net}"


class CashFlowVarianceAnalysis(models.Model):
    """Actual vs. Budgeted/Forecasted variance analysis"""
    
    cash_flow_statement = models.OneToOneField(CashFlowStatement, on_delete=models.CASCADE, related_name='variance_analysis')
    
    # Operating
    operating_forecast = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    operating_variance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    operating_variance_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Investing
    investing_forecast = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    investing_variance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    investing_variance_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Financing
    financing_forecast = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    financing_variance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    financing_variance_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Total
    total_forecast = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_variance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_variance_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    variance_explanation = models.TextField(blank=True, help_text="Management explanation of major variances")
    
    class Meta:
        verbose_name_plural = "Cash Flow Variance Analyses"
    
    def __str__(self):
        return f"Variance Analysis for {self.cash_flow_statement}"


class CashFlowComparison(models.Model):
    """Period-over-period comparison"""
    
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    
    current_period_statement = models.ForeignKey(CashFlowStatement, on_delete=models.CASCADE, related_name='current_comparisons')
    prior_period_statement = models.ForeignKey(CashFlowStatement, on_delete=models.CASCADE, related_name='prior_comparisons')
    
    # Operating
    operating_current = models.DecimalField(max_digits=18, decimal_places=2)
    operating_prior = models.DecimalField(max_digits=18, decimal_places=2)
    operating_change = models.DecimalField(max_digits=18, decimal_places=2)
    operating_change_pct = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Investing
    investing_current = models.DecimalField(max_digits=18, decimal_places=2)
    investing_prior = models.DecimalField(max_digits=18, decimal_places=2)
    investing_change = models.DecimalField(max_digits=18, decimal_places=2)
    investing_change_pct = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Financing
    financing_current = models.DecimalField(max_digits=18, decimal_places=2)
    financing_prior = models.DecimalField(max_digits=18, decimal_places=2)
    financing_change = models.DecimalField(max_digits=18, decimal_places=2)
    financing_change_pct = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Closing
    closing_current = models.DecimalField(max_digits=18, decimal_places=2)
    closing_prior = models.DecimalField(max_digits=18, decimal_places=2)
    closing_change = models.DecimalField(max_digits=18, decimal_places=2)
    closing_change_pct = models.DecimalField(max_digits=6, decimal_places=2)
    
    analysis_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-current_period_statement__start_date']
    
    def __str__(self):
        return f"Comparison: {self.current_period_statement.start_date} vs {self.prior_period_statement.start_date}"
