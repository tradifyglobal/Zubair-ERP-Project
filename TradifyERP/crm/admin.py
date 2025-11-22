from django.contrib import admin
from .models import Lead, SalesStage, Opportunity, Quote, Activity, Campaign, CRMSettings
from .retail_models import (
    LoyaltyProgram, LoyaltyMember, PointTransaction, 
    POSTransaction, Promotion, PromotionUsage, CustomerSegment
)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('lead_number', 'lead_name', 'company_name', 'email', 'status', 'lead_score', 'assigned_to')
    list_filter = ('status', 'source', 'created_date', 'lead_score')
    search_fields = ('lead_name', 'company_name', 'email')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_date'


@admin.register(SalesStage)
class SalesStageAdmin(admin.ModelAdmin):
    list_display = ('stage_name', 'sequence', 'win_probability', 'is_active', 'is_final_stage')
    list_filter = ('is_active', 'is_final_stage')


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('opportunity_number', 'opportunity_name', 'customer', 'deal_amount', 'stage', 'status', 'expected_close_date')
    list_filter = ('status', 'stage', 'expected_close_date', 'assigned_to')
    search_fields = ('opportunity_number', 'opportunity_name', 'customer__customer_name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'expected_close_date'


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('quote_number', 'customer', 'total_amount', 'status', 'quote_date', 'valid_until')
    list_filter = ('status', 'quote_date')
    search_fields = ('quote_number', 'customer__customer_name')
    date_hierarchy = 'quote_date'


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('subject', 'activity_type', 'activity_date', 'assigned_to', 'is_completed', 'priority')
    list_filter = ('activity_type', 'is_completed', 'priority', 'activity_date')
    search_fields = ('subject', 'description')
    date_hierarchy = 'activity_date'


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('campaign_name', 'campaign_type', 'status', 'start_date', 'end_date', 'budget', 'revenue_generated')
    list_filter = ('status', 'campaign_type', 'start_date')
    search_fields = ('campaign_name',)
    date_hierarchy = 'start_date'


@admin.register(CRMSettings)
class CRMSettingsAdmin(admin.ModelAdmin):
    list_display = ('entity', 'auto_assign_leads', 'lead_qualification_score_threshold', 'sales_forecast_method')
    readonly_fields = ('created_at', 'updated_at')


# ===== RETAIL & E-COMMERCE MODELS =====
@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ['program_name', 'loyalty_type', 'status', 'created_at']
    list_filter = ['loyalty_type', 'status']
    search_fields = ['program_name', 'program_code', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LoyaltyMember)
class LoyaltyMemberAdmin(admin.ModelAdmin):
    list_display = ['membership_number', 'customer', 'tier_level', 'current_points', 'status']
    list_filter = ['tier_level', 'status']
    search_fields = ['membership_number', 'customer__customer_name']
    readonly_fields = ['created_at', 'updated_at', 'lifetime_points_earned', 'lifetime_points_redeemed']


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['member', 'transaction_type', 'points', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['member__membership_number', 'reference_number']
    readonly_fields = ['created_at']


@admin.register(POSTransaction)
class POSTransactionAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'store_location', 'created_at', 'total_amount']
    list_filter = ['store_location', 'created_at']
    search_fields = ['receipt_number', 'member__membership_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['promotion_name', 'promotion_type', 'start_date', 'end_date', 'status']
    list_filter = ['promotion_type', 'status']
    search_fields = ['promotion_name', 'promotion_code']
    readonly_fields = ['created_at']


@admin.register(PromotionUsage)
class PromotionUsageAdmin(admin.ModelAdmin):
    list_display = ['promotion', 'customer', 'usage_date', 'discount_amount']
    list_filter = ['usage_date']
    search_fields = ['promotion__promotion_code']


@admin.register(CustomerSegment)
class CustomerSegmentAdmin(admin.ModelAdmin):
    list_display = ['segment_name', 'criteria_type', 'is_active']
    list_filter = ['criteria_type', 'is_active']
    search_fields = ['segment_name', 'description']
    readonly_fields = ['created_at', 'updated_at']




# ===== MANUFACTURING MODELS =====
# Note: Manufacturing models have been moved to the manufacturing app.
# See: manufacturing/admin.py for Distributor, DistributorContact, DistributorOrder,
# OrderShipment, AfterSalesService, WarrantyRegistration, DistributorPerformance

