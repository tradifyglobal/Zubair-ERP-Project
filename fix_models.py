#!/usr/bin/env python3
models_file = '/var/www/tradifyerp/accounting/models.py'
with open(models_file, 'r') as f:
    content = f.read()

# Replace placeholder
old_placeholder = "class ShareholderInvestmentRegister(models.Model): pass"
new_models = """
class ShareholderInvestmentRegister(models.Model):
    \"\"\"Sub-ledger for shareholder contributions.\"\"\"
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
    entity = models.ForeignKey('Entity', on_delete=models.CASCADE, related_name='shareholder_investments')
    stakeholder = models.ForeignKey('Stakeholder', on_delete=models.PROTECT, related_name='investment_register')
    investment_date = models.DateField(default=timezone.now, db_index=True)
    investment_type = models.CharField(max_length=25, choices=INVESTMENT_TYPE_CHOICES, default='CAPITAL')
    amount_company_currency = models.DecimalField(max_digits=18, decimal_places=2)
    original_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    currency = models.ForeignKey('Currency', on_delete=models.PROTECT, related_name='investments', null=True, blank=True)
    exchange_rate = models.DecimalField(max_digits=18, decimal_places=6, default=1.0)
    source_cash_receipt = models.ForeignKey('CashReceiptLine', on_delete=models.SET_NULL, null=True, blank=True, related_name='investment_register_entries')
    source_bank_receipt = models.ForeignKey('BankReceiptLine', on_delete=models.SET_NULL, null=True, blank=True, related_name='investment_register_entries')
    gl_reference = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='shareholder_investments_created')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    class Meta:
        ordering = ['-investment_date', '-created_date']
        indexes = [models.Index(fields=['entity', 'stakeholder', '-investment_date']), models.Index(fields=['entity', 'status', '-investment_date'])]
        verbose_name_plural = 'Shareholder Investment Register'
    def __str__(self):
        return f"{self.stakeholder.name} - {self.investment_date} - {self.amount_company_currency}"


class ShareholderInvestmentSummary(models.Model):
    \"\"\"Cached summary for performance.\"\"\"
    entity = models.ForeignKey('Entity', on_delete=models.CASCADE)
    stakeholder = models.ForeignKey('Stakeholder', on_delete=models.CASCADE)
    total_contributions = models.DecimalField(max_digits=18, decimal_places=2)
    contribution_count = models.IntegerField()
    first_contribution_date = models.DateField(null=True, blank=True)
    last_contribution_date = models.DateField(null=True, blank=True)
    average_contribution = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    completed_count = models.IntegerField(default=0)
    pending_count = models.IntegerField(default=0)
    cancelled_count = models.IntegerField(default=0)
    last_calculated = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('entity', 'stakeholder')
        verbose_name_plural = 'Shareholder Investment Summaries'
    def __str__(self):
        return f"{self.stakeholder.name} - Total: {self.total_contributions}"
"""

if old_placeholder in content:
    content = content.replace(old_placeholder, new_models)
    with open(models_file, 'w') as f:
        f.write(content)
    print('Models updated successfully')
else:
    print('Placeholder not found')
