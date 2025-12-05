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
    source = models.ForeignKey(
        'LeadSource',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads'
    )
    
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


# ===== MASTERS =====

class Territory(models.Model):
    """Sales territories for territory management."""
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='territories'
    )
    
    territory_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    region = models.CharField(max_length=100, blank=True)
    
    # Manager
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_territories'
    )
    
    # Target
    annual_target = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['territory_name']
    
    def __str__(self):
        return self.territory_name


class CustomerGroup(models.Model):
    """Customer grouping for segmentation."""
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='customer_groups'
    )
    
    group_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    group_code = models.CharField(max_length=50, unique=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['group_name']
    
    def __str__(self):
        return self.group_name


class Contact(models.Model):
    """Contact information for leads/customers."""
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='crm_contacts'
    )
    
    contact_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20, blank=True)
    
    # Organization
    company = models.CharField(max_length=255)
    designation = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['contact_name']
    
    def __str__(self):
        return f"{self.contact_name} - {self.company}"


class Prospect(models.Model):
    """Prospect management."""
    
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('CONTACTED', 'Contacted'),
        ('QUALIFIED', 'Qualified'),
        ('CONVERTED', 'Converted'),
        ('LOST', 'Lost'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='prospects'
    )
    
    prospect_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    probability = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    estimated_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_prospects')
    
    created_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return self.prospect_name


class SalesPerson(models.Model):
    """Sales team members management."""
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='sales_persons'
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sales_person')
    employee_id = models.CharField(max_length=50, unique=True)
    
    # Territory & Manager
    territory = models.ForeignKey(Territory, on_delete=models.SET_NULL, null=True, blank=True)
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_salespersons'
    )
    
    # Targets
    monthly_target = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    annual_target = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name']
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username


class LeadSource(models.Model):
    """Lead source categorization."""
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='lead_sources'
    )
    
    source_name = models.CharField(max_length=100)
    source_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['source_name']
    
    def __str__(self):
        return self.source_name


# ===== SALES PIPELINE ADDITIONAL =====

class Contract(models.Model):
    """Sales contracts."""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('SIGNED', 'Signed'),
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('TERMINATED', 'Terminated'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='crm_contracts'
    )
    
    contract_number = models.CharField(max_length=50, unique=True)
    contract_name = models.CharField(max_length=255)
    
    opportunity = models.ForeignKey(Opportunity, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='contracts')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    contract_value = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    start_date = models.DateField()
    end_date = models.DateField()
    renewal_date = models.DateField(null=True, blank=True)
    
    terms = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_contracts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.contract_number} - {self.contract_name}"


class Appointment(models.Model):
    """Sales appointments/meetings."""
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('RESCHEDULED', 'Rescheduled'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    
    appointment_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)
    
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['appointment_date']
    
    def __str__(self):
        return f"{self.title} - {self.appointment_date}"


class Communication(models.Model):
    """Communication log with customers."""
    
    TYPE_CHOICES = [
        ('EMAIL', 'Email'),
        ('CALL', 'Phone Call'),
        ('SMS', 'SMS'),
        ('MEETING', 'Meeting'),
        ('MESSAGE', 'Message'),
        ('OTHER', 'Other'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='communications'
    )
    
    communication_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='communications')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.SET_NULL, null=True, blank=True, related_name='communications')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='communications')
    
    subject = models.CharField(max_length=255)
    message = models.TextField()
    
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_communications')
    recipient_name = models.CharField(max_length=255, blank=True)
    recipient_email = models.EmailField(blank=True)
    
    communication_date = models.DateTimeField(default=timezone.now)
    
    outcome = models.TextField(blank=True)
    next_follow_up = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-communication_date']
    
    def __str__(self):
        return f"{self.get_communication_type_display()} - {self.subject}"


# ===== CAMPAIGN ADDITIONAL =====

class EmailCampaign(models.Model):
    """Email marketing campaigns."""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SCHEDULED', 'Scheduled'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='email_campaigns'
    )
    
    campaign_name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    
    from_email = models.EmailField()
    recipient_list = models.ManyToManyField(Lead, related_name='email_campaigns', blank=True)
    
    email_body = models.TextField()
    template = models.CharField(max_length=255, blank=True)
    
    scheduled_date = models.DateTimeField(null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_email_campaigns')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.campaign_name


class SMSCenter(models.Model):
    """SMS campaign center."""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SCHEDULED', 'Scheduled'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='sms_centers'
    )
    
    campaign_name = models.CharField(max_length=255)
    message = models.CharField(max_length=160)
    
    recipient_list = models.ManyToManyField(Lead, related_name='sms_campaigns', blank=True)
    
    scheduled_date = models.DateTimeField(null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_sms_campaigns')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.campaign_name


class SMSLog(models.Model):
    """SMS delivery log."""
    
    sms_campaign = models.ForeignKey(SMSCenter, on_delete=models.CASCADE, related_name='logs')
    
    recipient_phone = models.CharField(max_length=20)
    recipient_name = models.CharField(max_length=255)
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('SENT', 'Sent'),
            ('DELIVERED', 'Delivered'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING'
    )
    
    error_message = models.TextField(blank=True)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sms_campaign.campaign_name} - {self.recipient_phone}"


class EmailGroup(models.Model):
    """Email distribution groups."""
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='email_groups'
    )
    
    group_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    members = models.ManyToManyField(Lead, related_name='email_groups', blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['group_name']
    
    def __str__(self):
        return self.group_name


# ===== MAINTENANCE =====

class MaintenanceSchedule(models.Model):
    """Maintenance schedules for service management."""
    
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('SEMI_ANNUAL', 'Semi-Annual'),
        ('ANNUAL', 'Annual'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='maintenance_schedules'
    )
    
    schedule_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='maintenance_schedules')
    
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField()
    
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['next_maintenance_date']
    
    def __str__(self):
        return self.schedule_name


class MaintenanceVisit(models.Model):
    """Record of maintenance visits."""
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='maintenance_visits'
    )
    
    maintenance_schedule = models.ForeignKey(MaintenanceSchedule, on_delete=models.CASCADE, related_name='visits')
    visit_number = models.CharField(max_length=50, unique=True)
    
    visit_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    work_description = models.TextField(blank=True)
    findings = models.TextField(blank=True)
    
    hours_spent = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    
    parts_replaced = models.TextField(blank=True)
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    next_visit_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-visit_date']
    
    def save(self, *args, **kwargs):
        """Auto-calculate total_cost from parts_cost + labor_cost."""
        self.total_cost = (self.parts_cost or 0) + (self.labor_cost or 0)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.visit_number} - {self.visit_date}"


class WarrantyClaim(models.Model):
    """Warranty claim management."""
    
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='warranty_claims'
    )
    
    claim_number = models.CharField(max_length=50, unique=True)
    claim_date = models.DateField(default=timezone.now)
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='warranty_claims')
    product_description = models.CharField(max_length=255)
    purchase_date = models.DateField()
    
    issue_description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')
    
    claimed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    resolution = models.TextField(blank=True)
    resolution_date = models.DateField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_warranty_claims')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-claim_date']
    
    def __str__(self):
        return f"{self.claim_number} - {self.product_description}"


# ===== SETTINGS =====

class SMSSettings(models.Model):
    """SMS configuration and settings."""
    
    entity = models.OneToOneField(
        Entity,
        on_delete=models.CASCADE,
        related_name='sms_settings'
    )
    
    sms_provider = models.CharField(max_length=100, blank=True)
    api_key = models.CharField(max_length=255, blank=True)
    api_secret = models.CharField(max_length=255, blank=True)
    
    sender_id = models.CharField(max_length=20, blank=True)
    
    is_enabled = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"SMS Settings - {self.entity.code}"
