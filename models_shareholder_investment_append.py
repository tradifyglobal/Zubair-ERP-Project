

# ========== SHAREHOLDER INVESTMENT REGISTER MODELS ==========
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
    
    investment_date = models.DateField(default=timezone.now, db_index=True)
    investment_type = models.CharField(
        max_length=25,
        choices=INVESTMENT_TYPE_CHOICES,
        default='CAPITAL'
    )
    
    amount_company_currency = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Amount in entity's company currency"
    )
    
    original_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True
    )
    
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
        default=1.0
    )
    
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
    
    gl_reference = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shareholder_investments_created'
    )
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-investment_date', '-created_date']
        indexes = [
            models.Index(fields=['entity', 'stakeholder', '-investment_date']),
            models.Index(fields=['entity', 'status', '-investment_date']),
        ]
        verbose_name_plural = 'Shareholder Investment Register'
    
    def __str__(self):
        return f"{self.stakeholder.name} - {self.investment_date} - {self.amount_company_currency}"


class ShareholderInvestmentSummary(models.Model):
    """Cached summary view for performance optimization."""
    
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
