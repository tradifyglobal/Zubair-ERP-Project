"""
Retail & E-commerce CRM Module
Loyalty programs, POS integration, personalized promotions, customer engagement.

Integrated with main CRM for customer management and GL for revenue tracking.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from accounting.models import Entity, Account, LedgerEntry, Currency
from crm.models import Lead, Opportunity
from sales.models import Customer


class LoyaltyProgram(models.Model):
    """Loyalty program master configuration."""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended'),
        ('ARCHIVED', 'Archived'),
    ]
    
    LOYALTY_TYPE = [
        ('POINTS', 'Points-based'),
        ('TIERED', 'Tiered'),
        ('CASH_BACK', 'Cash Back'),
        ('SUBSCRIPTION', 'Subscription'),
        ('REFERRAL', 'Referral'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='loyalty_programs'
    )
    
    # Program Details
    program_name = models.CharField(max_length=255)
    program_code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    
    # Program Type
    loyalty_type = models.CharField(max_length=20, choices=LOYALTY_TYPE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Point Configuration
    points_per_currency = models.DecimalField(
        max_digits=10, 
        decimal_places=4,
        default=1,
        help_text="Points earned per currency unit spent"
    )
    point_expiry_days = models.IntegerField(
        default=365,
        help_text="Days until points expire (0 = never)"
    )
    
    # Redemption
    points_per_reward = models.IntegerField(
        default=100,
        help_text="Points needed to redeem reward"
    )
    reward_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Monetary value of reward"
    )
    
    # Minimum spend for enrollment
    minimum_enrollment_purchase = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Minimum purchase to enroll"
    )
    
    # Tier Configuration (for tiered programs)
    enable_tiers = models.BooleanField(default=False)
    
    # Active dates
    launch_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    
    # Tracking
    gl_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='loyalty_accruals'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'retail_loyalty_program'
        ordering = ['-launch_date']
        indexes = [
            models.Index(fields=['entity', 'status']),
            models.Index(fields=['program_code']),
        ]
    
    def __str__(self):
        return f"{self.program_name} ({self.program_code})"


class LoyaltyMember(models.Model):
    """Customer membership in loyalty program."""
    
    MEMBERSHIP_STATUS = [
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    program = models.ForeignKey(
        LoyaltyProgram,
        on_delete=models.CASCADE,
        related_name='members'
    )
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='loyalty_memberships'
    )
    
    # Membership Details
    membership_number = models.CharField(max_length=50, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS, default='ACTIVE')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    last_transaction_date = models.DateTimeField(null=True, blank=True)
    
    # Point Balance
    current_points = models.IntegerField(default=0)
    lifetime_points_earned = models.IntegerField(default=0)
    lifetime_points_redeemed = models.IntegerField(default=0)
    
    # Tier (for tiered programs)
    tier_name = models.CharField(max_length=100, blank=True)
    tier_level = models.IntegerField(default=1)
    
    # Preferences
    email_opted_in = models.BooleanField(default=True)
    sms_opted_in = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'retail_loyalty_member'
        unique_together = ('program', 'customer')
        ordering = ['-enrollment_date']
        indexes = [
            models.Index(fields=['program', 'status']),
            models.Index(fields=['membership_number']),
        ]
    
    def __str__(self):
        return f"{self.customer.name} - {self.program.program_code}"


class PointTransaction(models.Model):
    """Record of points earned, redeemed, or adjusted."""
    
    TRANSACTION_TYPE = [
        ('EARNED', 'Earned'),
        ('REDEEMED', 'Redeemed'),
        ('ADJUSTED', 'Adjusted'),
        ('EXPIRED', 'Expired'),
        ('REFUNDED', 'Refunded'),
    ]
    
    member = models.ForeignKey(
        LoyaltyMember,
        on_delete=models.CASCADE,
        related_name='point_transactions'
    )
    
    # Transaction Details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    points = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True)
    
    # Reference
    sale_order_id = models.CharField(max_length=50, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    
    # Expiry (for earned points)
    expiry_date = models.DateField(null=True, blank=True)
    is_expired = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'retail_point_transaction'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['member', 'transaction_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.member} - {self.transaction_type}: {self.points} pts"


class POSTransaction(models.Model):
    """Point-of-sale transaction record for retail."""
    
    STATUS_CHOICES = [
        ('COMPLETED', 'Completed'),
        ('VOIDED', 'Voided'),
        ('PENDING', 'Pending'),
        ('REFUNDED', 'Refunded'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='pos_transactions'
    )
    
    # Transaction Details
    receipt_number = models.CharField(max_length=50, unique=True, db_index=True)
    transaction_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='COMPLETED')
    
    # Customer
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pos_transactions'
    )
    loyalty_member = models.ForeignKey(
        LoyaltyMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pos_transactions'
    )
    
    # Amounts
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Payment
    payment_method = models.CharField(max_length=50)
    
    # Loyalty
    loyalty_points_earned = models.IntegerField(default=0)
    loyalty_discount_applied = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # GL Integration
    is_posted = models.BooleanField(default=False)
    gl_entry = models.ForeignKey(
        LedgerEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pos_transactions'
    )
    
    # Store/Terminal
    store_location = models.CharField(max_length=100, blank=True)
    terminal_id = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'retail_pos_transaction'
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['entity', 'transaction_date']),
            models.Index(fields=['receipt_number']),
            models.Index(fields=['customer']),
        ]
    
    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.total_amount}"


class Promotion(models.Model):
    """Marketing promotions and discounts."""
    
    PROMOTION_TYPE = [
        ('DISCOUNT_PERCENTAGE', 'Discount %'),
        ('DISCOUNT_FIXED', 'Fixed Discount'),
        ('BOGO', 'Buy One Get One'),
        ('FREE_SHIPPING', 'Free Shipping'),
        ('LOYALTY_BONUS', 'Loyalty Bonus'),
        ('BUNDLE', 'Bundle Deal'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('ENDED', 'Ended'),
        ('ARCHIVED', 'Archived'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='retail_promotions'
    )
    
    # Promotion Details
    promotion_name = models.CharField(max_length=255)
    promotion_code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    
    # Type and Value
    promotion_type = models.CharField(max_length=30, choices=PROMOTION_TYPE)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Target
    target_customers = models.ForeignKey(
        'LoyaltyProgram',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Limit to specific loyalty program"
    )
    target_tier = models.CharField(max_length=100, blank=True)
    
    # Conditions
    minimum_purchase = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    maximum_discount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    usage_limit = models.IntegerField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    
    # Dates
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Personalization
    is_personalized = models.BooleanField(default=False)
    personalization_criteria = models.CharField(max_length=255, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_promotions'
    )
    
    class Meta:
        db_table = 'retail_promotion'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['entity', 'status']),
            models.Index(fields=['promotion_code']),
        ]
    
    def __str__(self):
        return f"{self.promotion_name} ({self.promotion_code})"


class PromotionUsage(models.Model):
    """Track promotion usage and redemption."""
    
    promotion = models.ForeignKey(
        Promotion,
        on_delete=models.CASCADE,
        related_name='usages'
    )
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='promotion_usages'
    )
    
    pos_transaction = models.ForeignKey(
        POSTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='promotion_usages'
    )
    
    # Usage Details
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)
    usage_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'retail_promotion_usage'
        ordering = ['-usage_date']
        indexes = [
            models.Index(fields=['promotion', 'customer']),
        ]
    
    def __str__(self):
        return f"{self.promotion.promotion_code} used by {self.customer.name}"


class CustomerSegment(models.Model):
    """Customer segmentation for targeted promotions."""
    
    SEGMENT_CRITERIA = [
        ('PURCHASE_HISTORY', 'Purchase History'),
        ('LOYALTY_TIER', 'Loyalty Tier'),
        ('GEOGRAPHIC', 'Geographic'),
        ('DEMOGRAPHIC', 'Demographic'),
        ('BEHAVIOR', 'Behavior'),
        ('ENGAGEMENT', 'Engagement Level'),
    ]
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='customer_segments'
    )
    
    # Segment Details
    segment_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    criteria_type = models.CharField(max_length=30, choices=SEGMENT_CRITERIA)
    
    # Criteria Details
    min_purchase_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_purchase_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    min_loyalty_tier = models.CharField(max_length=100, blank=True)
    geographic_region = models.CharField(max_length=255, blank=True)
    
    # Customers in segment
    customers = models.ManyToManyField(
        Customer,
        blank=True,
        related_name='customer_segments'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'retail_customer_segment'
        ordering = ['segment_name']
        indexes = [
            models.Index(fields=['entity', 'is_active']),
        ]
    
    def __str__(self):
        return self.segment_name
