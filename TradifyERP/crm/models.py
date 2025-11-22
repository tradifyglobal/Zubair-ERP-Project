"""
CRM Module Models
Complete CRM including:
- Lead management & qualification
- Sales pipeline & opportunities
- Quote generation
- Customer activity tracking
- Sales forecasting
- Campaign management

Fully integrated with accounting for revenue GL posting.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from accounting.models import Entity, Account
from sales.models import Customer


class Lead(models.Model):
    """Sales leads."""
    
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('CONTACTED', 'Contacted'),
        ('QUALIFIED', 'Qualified'),
        ('PROPOSAL', 'Proposal Sent'),
        ('CONVERTED', 'Converted to Opportunity'),
        ('LOST', 'Lost'),
        ('DUPLICATE', 'Duplicate'),
    ]
    
    LEAD_SOURCE_CHOICES = [
        ('WEBSITE', 'Website'),
        ('REFERRAL', 'Referral'),
        ('COLD_CALL', 'Cold Call'),
        ('EMAIL', 'Email Campaign'),
        ('TRADE_SHOW', 'Trade Show'),
        ('SOCIAL_MEDIA', 'Social Media'),
        ('ADVERTISEMENT', 'Advertisement'),
        ('INBOUND', 'Inbound Inquiry'),
        ('OTHER', 'Other'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='crm_leads'
    )
    
    # Lead Info
    lead_number = models.CharField(max_length=50, unique=True, db_index=True)
    lead_name = models.CharField(max_length=255)
    
    # Contact Details
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=255)
    
    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Lead Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    source = models.CharField(max_length=20, choices=LEAD_SOURCE_CHOICES)
    
    # Lead Scoring
    lead_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Estimated Value
    estimated_deal_size = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_leads'
    )
    
    # Dates
    created_date = models.DateField(default=timezone.now)
    last_contact_date = models.DateField(null=True, blank=True)
    qualified_date = models.DateField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_leads'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_date']
        indexes = [
            models.Index(fields=['entity', 'status']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['lead_score']),
        ]
    
    def __str__(self):
        return f"{self.lead_number} - {self.lead_name}"


class SalesStage(models.Model):
    """Sales pipeline stages."""
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='sales_stages'
    )
    
    stage_name = models.CharField(max_length=100)
    sequence = models.IntegerField()
    description = models.TextField(blank=True)
    
    # Probability
    win_probability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_final_stage = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['sequence']
        unique_together = ('entity', 'sequence')
    
    def __str__(self):
        return self.stage_name


class Opportunity(models.Model):
    """Sales opportunities."""
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('WON', 'Won'),
        ('LOST', 'Lost'),
        ('PENDING', 'Pending'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='crm_opportunities'
    )
    
    # Identification
    opportunity_number = models.CharField(max_length=50, unique=True, db_index=True)
    opportunity_name = models.CharField(max_length=255)
    
    # Customer
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='opportunities'
    )
    
    # Lead Reference
    lead = models.ForeignKey(
        Lead,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunities'
    )
    
    # Deal Details
    deal_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Stage
    stage = models.ForeignKey(
        SalesStage,
        on_delete=models.PROTECT,
        related_name='opportunities'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    
    # Probability
    win_probability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Weighted Value
    @property
    def weighted_value(self):
        """Calculate weighted opportunity value."""
        return self.deal_amount * (self.win_probability / 100)
    
    # Dates
    created_date = models.DateField(default=timezone.now)
    expected_close_date = models.DateField()
    actual_close_date = models.DateField(null=True, blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_opportunities'
    )
    
    # Description
    description = models.TextField(blank=True)
    
    # Next Steps
    next_steps = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-expected_close_date']
        indexes = [
            models.Index(fields=['entity', 'status']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['expected_close_date']),
        ]
    
    def __str__(self):
        return f"{self.opportunity_number} - {self.opportunity_name}"


class Quote(models.Model):
    """Sales quotes."""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='crm_quotes'
    )
    
    # Identification
    quote_number = models.CharField(max_length=50, unique=True, db_index=True)
    
    # Linked Records
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='quotes'
    )
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='quotes'
    )
    
    # Details
    quote_date = models.DateField(default=timezone.now)
    valid_until = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Amount
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Terms
    payment_terms = models.CharField(max_length=100, blank=True)
    delivery_terms = models.CharField(max_length=100, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Tracking
    sent_date = models.DateField(null=True, blank=True)
    accepted_date = models.DateField(null=True, blank=True)
    accepted_by = models.CharField(max_length=255, blank=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_quotes'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-quote_date']
    
    def __str__(self):
        return f"Quote {self.quote_number}"


class Activity(models.Model):
    """Customer/Lead activities (calls, emails, meetings)."""
    
    ACTIVITY_TYPES = [
        ('CALL', 'Phone Call'),
        ('EMAIL', 'Email'),
        ('MEETING', 'Meeting'),
        ('TASK', 'Task'),
        ('NOTE', 'Note'),
        ('OTHER', 'Other'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='crm_activities'
    )
    
    # Related Records
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='activities'
    )
    
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='activities'
    )
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='activities'
    )
    
    # Activity
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    activity_date = models.DateTimeField(default=timezone.now)
    
    # Details
    subject = models.CharField(max_length=255)
    description = models.TextField()
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_activities'
    )
    
    # Status
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    # Priority
    priority = models.CharField(
        max_length=20,
        choices=[
            ('LOW', 'Low'),
            ('MEDIUM', 'Medium'),
            ('HIGH', 'High'),
        ],
        default='MEDIUM'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_activities'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-activity_date']
        indexes = [
            models.Index(fields=['assigned_to', 'is_completed']),
        ]
    
    def __str__(self):
        return f"{self.subject} - {self.activity_date}"


class Campaign(models.Model):
    """Sales campaigns."""
    
    STATUS_CHOICES = [
        ('PLANNING', 'Planning'),
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='campaigns'
    )
    
    # Campaign Details
    campaign_name = models.CharField(max_length=255)
    campaign_type = models.CharField(max_length=50)  # Email, Cold Call, etc.
    description = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNING')
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Budget
    budget = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Metrics
    leads_generated = models.IntegerField(default=0)
    opportunities_created = models.IntegerField(default=0)
    revenue_generated = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # ROI Calculation
    @property
    def roi(self):
        """Calculate ROI."""
        if self.actual_cost == 0:
            return Decimal('0')
        return ((self.revenue_generated - self.actual_cost) / self.actual_cost * 100)
    
    # Assignment
    campaign_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_campaigns'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.campaign_name


class CRMSettings(models.Model):
    """CRM settings per entity."""
    
    entity = models.OneToOneField(
        Entity,
        on_delete=models.CASCADE,
        related_name='crm_settings'
    )
    
    # Lead Settings
    auto_assign_leads = models.BooleanField(default=False)
    lead_qualification_score_threshold = models.IntegerField(default=50)
    
    # Opportunity Settings
    auto_create_opportunity_from_lead = models.BooleanField(default=True)
    default_sales_stage = models.ForeignKey(
        SalesStage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Pipeline Settings
    sales_forecast_method = models.CharField(
        max_length=50,
        choices=[
            ('WEIGHTED', 'Weighted'),
            ('PIPELINE', 'Pipeline'),
            ('BEST_CASE', 'Best Case'),
        ],
        default='WEIGHTED'
    )
    
    # Conversion Settings
    track_conversion_rate = models.BooleanField(default=True)
    auto_create_customer = models.BooleanField(default=False)
    
    # Revenue Account for GL
    revenue_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crm_revenue'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"CRM Settings - {self.entity.code}"
