from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator
from decimal import Decimal


class Currency(models.Model):
    """Currency definitions - referenced in stakeholder models."""
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    exchange_rate = models.DecimalField(max_digits=18, decimal_places=6, default=1.0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.code} ({self.symbol})"


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
    phone_number = models.CharField(max_length=20)
    secondary_phone = models.CharField(max_length=20, blank=True, null=True)
    fax = models.CharField(max_length=20, blank=True, null=True)
    
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
        """Calculate total capital invested by this stakeholder."""
        return sum(
            cc.amount_usd for cc in self.capital_contributions.filter(status='COMPLETED')
        )
    
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
    
    # Core Fields
    entity = models.ForeignKey('accounting.Entity', on_delete=models.CASCADE, related_name='capital_contributions')
    stakeholder = models.ForeignKey(Stakeholder, on_delete=models.CASCADE, related_name='capital_contributions')
    contribution_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
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
    payment_bank_account = models.CharField(max_length=255, blank=True, null=True)
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
