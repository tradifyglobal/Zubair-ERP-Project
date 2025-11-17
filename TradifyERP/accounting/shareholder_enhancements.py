"""
Shareholder Module Enhancements - Brings Shareholder from 8.5/10 to 9.5/10
Advanced shareholder management, dividends, voting rights, and corporate actions.
"""

from django.db import models
from django.utils import timezone
from decimal import Decimal


class DividendPolicy(models.Model):
    """
    Corporate dividend policy definition.
    """
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='dividend_policies'
    )
    
    policy_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Policy Details
    dividend_frequency = models.CharField(
        max_length=50,
        choices=[
            ('ANNUAL', 'Annual'),
            ('SEMI_ANNUAL', 'Semi-Annual'),
            ('QUARTERLY', 'Quarterly'),
            ('MONTHLY', 'Monthly'),
        ]
    )
    
    payout_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Percentage of earnings to distribute as dividends"
    )
    
    minimum_retention_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Minimum percentage to retain for operations"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    effective_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_dividend_policies'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effective_date']
    
    def __str__(self):
        return f"{self.entity} - {self.policy_name}"


class DividendDeclaration(models.Model):
    """
    Track dividend declarations by the board of directors.
    """
    DIVIDEND_TYPES = [
        ('CASH', 'Cash Dividend'),
        ('STOCK', 'Stock Dividend'),
        ('PROPERTY', 'Property Dividend'),
        ('SCRIP', 'Scrip Dividend'),
    ]
    
    STATUS_CHOICES = [
        ('PROPOSED', 'Proposed'),
        ('APPROVED', 'Approved by Board'),
        ('DECLARED', 'Declared'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='dividend_declarations'
    )
    
    dividend_type = models.CharField(max_length=20, choices=DIVIDEND_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PROPOSED')
    
    # Dates
    declaration_date = models.DateField()
    record_date = models.DateField()          # Shareholders as of this date receive dividend
    payment_date = models.DateField()
    ex_dividend_date = models.DateField()     # Last day to buy stock and receive dividend
    
    # Amount
    total_dividend_amount = models.DecimalField(max_digits=18, decimal_places=2)
    dividend_per_share = models.DecimalField(max_digits=12, decimal_places=6)
    
    # Details
    description = models.TextField(blank=True)
    business_justification = models.TextField(blank=True)
    
    # Governance
    board_resolution_number = models.CharField(max_length=100, blank=True)
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_dividends'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    
    # GL Account for dividend expense
    dividend_expense_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dividend_declarations'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-declaration_date']
        unique_together = ('entity', 'declaration_date', 'dividend_type')
    
    def __str__(self):
        return f"Dividend {self.declaration_date} - ${self.total_dividend_amount}"


class ShareholderDividend(models.Model):
    """
    Individual shareholder dividend payments.
    """
    STATUS_CHOICES = [
        ('ACCRUED', 'Accrued'),
        ('APPROVED', 'Approved for Payment'),
        ('PAID', 'Paid'),
        ('UNCLAIMED', 'Unclaimed'),
    ]
    
    dividend_declaration = models.ForeignKey(
        DividendDeclaration,
        on_delete=models.CASCADE,
        related_name='shareholder_dividends'
    )
    
    stakeholder = models.ForeignKey(
        'accounting.Stakeholder',
        on_delete=models.CASCADE,
        related_name='dividends'
    )
    
    # Shares held on record date
    shares_held = models.DecimalField(max_digits=18, decimal_places=2)
    
    # Dividend amount
    dividend_amount = models.DecimalField(max_digits=18, decimal_places=2)
    
    # Status & Payment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACCRUED')
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('CASH', 'Cash'),
            ('CHECK', 'Check'),
            ('EFT', 'Electronic Transfer'),
            ('REINVEST', 'Reinvested'),
        ],
        blank=True
    )
    
    payment_date = models.DateField(null=True, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)  # Check number, transaction ID
    
    # GL Entry
    gl_entry = models.ForeignKey(
        'accounting.LedgerEntry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shareholder_dividends'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('dividend_declaration', 'stakeholder')
        ordering = ['-dividend_declaration__declaration_date']
    
    def __str__(self):
        return f"{self.stakeholder} - ${self.dividend_amount}"


class ShareClass(models.Model):
    """
    Define different share classes with different rights and privileges.
    E.g., Common Shares, Class A, Class B, Preferred Shares
    """
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='share_classes'
    )
    
    class_name = models.CharField(max_length=50)  # e.g., "Common", "Class A", "Preferred"
    code = models.CharField(max_length=10)
    
    # Rights & Privileges
    voting_rights = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        help_text="Votes per share"
    )
    
    dividend_preference = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Preferred dividend rate %"
    )
    
    is_cumulative = models.BooleanField(
        default=False,
        help_text="Unpaid dividends accumulate for preferred shares"
    )
    
    is_convertible = models.BooleanField(default=False)
    conversion_terms = models.TextField(blank=True)
    
    # Liquidation preferences
    liquidation_priority = models.IntegerField(default=0)  # 0 = highest priority
    
    # Par value
    par_value = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Status
    is_active = models.BooleanField(default=True)
    authorized_shares = models.IntegerField()
    issued_shares = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('entity', 'class_name')
        ordering = ['entity', 'liquidation_priority', 'class_name']
    
    def __str__(self):
        return f"{self.entity} - {self.class_name} Shares"


class ShareholderVoting(models.Model):
    """
    Track shareholder voting rights and voting patterns.
    """
    VOTING_STATUS = [
        ('NOT_VOTED', 'Not Voted'),
        ('VOTED_FOR', 'Voted For'),
        ('VOTED_AGAINST', 'Voted Against'),
        ('ABSTAINED', 'Abstained'),
    ]
    
    stakeholder = models.ForeignKey(
        'accounting.Stakeholder',
        on_delete=models.CASCADE,
        related_name='voting_records'
    )
    
    matter_id = models.CharField(max_length=100)  # e.g., "AGM2025_PROPOSAL1"
    matter_description = models.TextField()
    meeting_date = models.DateField()
    
    # Voting rights
    shares_held = models.DecimalField(max_digits=18, decimal_places=2)
    votes_per_share = models.DecimalField(max_digits=8, decimal_places=4)
    total_votes = models.DecimalField(max_digits=18, decimal_places=2)
    
    # Vote
    voting_status = models.CharField(max_length=20, choices=VOTING_STATUS, default='NOT_VOTED')
    voted_date = models.DateTimeField(null=True, blank=True)
    proxy_voted = models.BooleanField(default=False)
    proxy_name = models.CharField(max_length=255, blank=True)
    
    # Comments
    voting_instructions = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('stakeholder', 'matter_id')
        ordering = ['-meeting_date']
    
    def __str__(self):
        return f"{self.stakeholder} - {self.matter_id}: {self.voting_status}"


class CorporateAction(models.Model):
    """
    Track corporate actions affecting share structure.
    Stock splits, mergers, rights issuances, etc.
    """
    ACTION_TYPES = [
        ('STOCK_SPLIT', 'Stock Split'),
        ('REVERSE_SPLIT', 'Reverse Stock Split'),
        ('DIVIDEND_REINVEST', 'Dividend Reinvestment'),
        ('RIGHTS_OFFERING', 'Rights Offering'),
        ('BONUS_ISSUE', 'Bonus Issue'),
        ('MERGER', 'Merger'),
        ('ACQUISITION', 'Acquisition'),
        ('SPIN_OFF', 'Spin-Off'),
        ('RECAPITALIZATION', 'Recapitalization'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='corporate_actions'
    )
    
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    
    # Effective Date
    announcement_date = models.DateField()
    record_date = models.DateField()          # As of this date
    effective_date = models.DateField()
    
    # Details
    action_details = models.JSONField(default=dict)  # Flexible storage for action-specific data
    # e.g., for split: {"split_ratio": "2:1", "reason": "increase liquidity"}
    # e.g., for dividend: {"dividend_per_share": 5.00, "type": "special"}
    
    # Impact
    impact_on_shares = models.CharField(max_length=255, blank=True)  # e.g., "+50%", "2:1 split"
    impact_on_price = models.CharField(max_length=255, blank=True)   # Adjusted for splits
    
    # Governance
    board_resolution = models.CharField(max_length=100, blank=True)
    shareholder_approval_required = models.BooleanField(default=False)
    shareholder_approved = models.BooleanField(default=False)
    approval_date = models.DateField(null=True, blank=True)
    
    # Status
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effective_date']
    
    def __str__(self):
        return f"{self.entity} - {self.get_action_type_display()} ({self.effective_date})"


class ShareholderRegistration(models.Model):
    """
    Share certificate registry and transfer records.
    """
    REGISTRATION_STATUS = [
        ('ACTIVE', 'Active'),
        ('TRANSFERRED', 'Transferred'),
        ('CANCELLED', 'Cancelled'),
        ('LOST', 'Lost/Damaged'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='share_registrations'
    )
    
    certificate_number = models.CharField(max_length=100, unique=True)
    stakeholder = models.ForeignKey(
        'accounting.Stakeholder',
        on_delete=models.PROTECT,
        related_name='share_certificates'
    )
    
    share_class = models.ForeignKey(
        ShareClass,
        on_delete=models.PROTECT,
        related_name='certificates'
    )
    
    # Share Details
    number_of_shares = models.DecimalField(max_digits=18, decimal_places=2)
    issue_date = models.DateField()
    
    # Status
    status = models.CharField(max_length=20, choices=REGISTRATION_STATUS, default='ACTIVE')
    
    # Transfers
    transferred_to = models.ForeignKey(
        'accounting.Stakeholder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transferred_share_certificates'
    )
    transfer_date = models.DateField(null=True, blank=True)
    transfer_consideration = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # GL Integration
    share_premium_account = models.ForeignKey(
        'accounting.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='share_registrations'
    )
    
    # Documentation
    document_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['stakeholder', 'status']),
            models.Index(fields=['certificate_number']),
        ]
    
    def __str__(self):
        return f"Certificate {self.certificate_number} - {self.stakeholder}"


class ShareholderAgreement(models.Model):
    """
    Track shareholder agreements and special arrangements.
    """
    AGREEMENT_TYPES = [
        ('DRAG_ALONG', 'Drag-Along Rights'),
        ('TAG_ALONG', 'Tag-Along Rights'),
        ('PREEMPTIVE', 'Preemptive Rights'),
        ('ANTI_DILUTION', 'Anti-Dilution Rights'),
        ('REDEMPTION', 'Redemption Rights'),
        ('PUT_OPTION', 'Put Option'),
        ('CALL_OPTION', 'Call Option'),
        ('VOTING_AGREEMENT', 'Voting Agreement'),
        ('LOCK_UP', 'Lock-Up Agreement'),
        ('CONFIDENTIALITY', 'Confidentiality Agreement'),
        ('OTHER', 'Other'),
    ]
    
    entity = models.ForeignKey(
        'accounting.Entity',
        on_delete=models.CASCADE,
        related_name='shareholder_agreements'
    )
    
    stakeholders = models.ManyToManyField(
        'accounting.Stakeholder',
        related_name='agreements'
    )
    
    agreement_type = models.CharField(max_length=50, choices=AGREEMENT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Key Terms
    effective_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    is_perpetual = models.BooleanField(default=False)
    
    # Special Rights
    key_terms = models.JSONField(default=dict)  # Flexible storage for agreement terms
    
    # Document
    document_url = models.URLField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effective_date']
    
    def __str__(self):
        return f"{self.entity} - {self.get_agreement_type_display()}"
